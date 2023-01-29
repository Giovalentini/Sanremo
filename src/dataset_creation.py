#import libraries
import logging
import numpy as np
import pandas as pd
import pickle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils import SanremoDatasetCreator

#setup of spotify API
import os
os.environ['SPOTIPY_CLIENT_ID'] = '65856b2827c94410a969dc084bcd1c13'
os.environ['SPOTIPY_CLIENT_SECRET'] = '4a749940bc164fa3892c83e7a2bbfcbe'

# setup logging
logging.basicConfig(level=logging.INFO)

#ids of all playlists - order from 2022 to 2010
#3a67CvngL5t42BVvLgg8u5
lista_uri=['spotify:playlist:3a67CvngL5t42BVvLgg8u5',
           'spotify:playlist:61QFMC1ntb7BrXveI3f4cX',
           'spotify:playlist:0QLiQIBYm1m1wxO6O1P8I5',
           'spotify:playlist:4bBjCi2q4c1Ry5DELrn1LM',
           'spotify:playlist:29qBlT6rlJtpKlaYhaUuK3',
           'spotify:playlist:0HEsgzoiLv3sx8ZZkgfYVp',
           'spotify:playlist:21kNTX3BPkbyJT3Q8Ni8D5',
           'spotify:playlist:3jLuMYBCqx6hniolxG9DP6',
           'spotify:playlist:5BqEPtLYvo7VjSouADG9bL',
           'spotify:playlist:1bJLbLWtSeN3htfgR9mfat',
           'spotify:playlist:4cQgkg1XHs1xc7LnZotEWY',
           'spotify:playlist:5umuFbGnpR1esP6BxjAnTx',
           'spotify:playlist:2zHJQOP880x7aWTkZqqNog']

start_year=2010
end_year = start_year + len(lista_uri) - 1
years=[i for i in reversed(range(start_year,end_year+1))]
bigs_per_year = (24,26,24,24,19,22,18,17,11,13,14,14,14)
tot_years = len(lista_uri)

def main():
    """
    This function runs the main code of the script.
    It gets the ids, tracks, and artists of all playlists,
    removes the rookies, extracts the song features,
    adds the winner column and the title and artist columns
    to the dataframe and returns the dataframe.
    """
    dataset_creator = SanremoDatasetCreator(
        bigs_per_year = bigs_per_year,
        tot_years = tot_years,
        years = years
    )

    # get list of ids, songs and artists from each playlist
    logging.info(" Fetching playlists URIs...")
    ids_list, track_list, artist_list, artist_count = dataset_creator.get_ids_from_playlist(lista_uri)

    # adjust lists removing rookies
    logging.info(" Removing rookies...")
    ids_list, track_list, artist_list, artist_count = dataset_creator.exclude_rookies(
        ids_list, track_list, artist_list, artist_count
    )

    #Extract track features and put them in a df
    logging.info(" Extracting track features...")
    sanremo_df = dataset_creator.extract_song_features(ids_list=ids_list)

    #there's one track_id which doesn't work - 4WJVLEkcMMV2tHo1Bd65VN

    #add winner column - first of each playlist is a winner except for 2021
    logging.info(" Adding winner column...")
    sanremo_df = dataset_creator.add_winner(sanremo_df)

    #add title and artist
    logging.info(" Adding title and artist to each song...")
    sanremo_df = dataset_creator.add_title_and_artist(
        sanremo_df,track_list,artist_list,artist_count
    )

    return sanremo_df

if __name__ == "__main__":
    sanremo_df = main()

    #manually impute artist type and sex
    # Type: 1 for solo artist, 2 for collab or duet, 3 for band
    # Sex: 0 for male, 1 for female, 2 for mix/other (considered frontman in bands to elige sex)
    #sanremo_df[['song','artist']].to_excel(r"C:\Users\g.valentini\Documents\Projects\Sanremo\src\artist_sex_type.xlsx")
    #artist_sex_type = pd.read_excel(r"C:\Users\g.valentini\Documents\Projects\Sanremo\src\artist_sex_type.xlsx")
    #sanremo_df = pd.merge(sanremo_df,artist_sex_type,on=['song','artist'])

    with open("sanremo_df.pkl", "wb") as f:
        pickle.dump(sanremo_df, f)

    sanremo_df.to_excel("../data/sanremo_df.xlsx", index=False)
