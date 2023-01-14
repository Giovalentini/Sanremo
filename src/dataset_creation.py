#import libraries
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils import *

#setup of spotify API
import os
os.environ['SPOTIPY_CLIENT_ID'] = '65856b2827c94410a969dc084bcd1c13'
os.environ['SPOTIPY_CLIENT_SECRET'] = '4a749940bc164fa3892c83e7a2bbfcbe'
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

#ids of all playlists - order from 2022 to 2010
#3a67CvngL5t42BVvLgg8u5
lista_uri=['spotify:playlist:3a67CvngL5t42BVvLgg8u5',
           'spotify:playlist:61QFMC1ntb7BrXveI3f4cX',
           'spotify:playlist:0QLiQIBYm1m1wxO6O1P8I5',
           'spotify:playlist:4bBjCi2q4c1Ry5DELrn1LM',
           'spotify:playlist:29qBlT6rlJtpKlaYhaUuK3',
           'spotify:playlist:0HEsgzoiLv3sx8ZZkgfYVp',
           'spotify:playlist:21kNTX3BPkbyJT3Q8Ni8D5',
           'spotify:playlist:0Z18gq4LmBHUYeAmfBY3GS',
           'spotify:playlist:5BqEPtLYvo7VjSouADG9bL',
           'spotify:playlist:1bJLbLWtSeN3htfgR9mfat',
           'spotify:playlist:4cQgkg1XHs1xc7LnZotEWY',
           'spotify:playlist:5umuFbGnpR1esP6BxjAnTx',
           'spotify:playlist:2zHJQOP880x7aWTkZqqNog']

anno_inizio=2010
anno_fine = anno_inizio + len(lista_uri) - 1
years=[i for i in reversed(range(anno_inizio,anno_fine+1))]

#lista_uri=['spotify:playlist:13TbnOluHonxsVvSWkL7YF'] #1990-2021 in un'unica playlist

if __name__ == "__main__":

    # get list of ids, songs and artists from each playlist
    ids_list, track_list, artist_list = get_ids_from_playlist(lista_uri)

    # adjust lists removing rookies
    bigs_per_year = (24,26,24,24,19,22,18,19,11,13,14,14,14)
    tot_years = len(lista_uri)
    ids_list, track_list, artist_list = exclude_rookies(bigs_per_year, tot_years)

    #now I have all bigs songs ids. Next step: extract track features and put them in a df
    sanremo_df = extract_song_features(ids_list=ids_list)

    #there's one track_id which doesn't work - 4WJVLEkcMMV2tHo1Bd65VN

    #add winner column - first of each playlist is a winner except for 2021
    sanremo_df = add_winner(sanremo_df)

    #add title and artist
    sanremo_df = add_title_and_artist(sanremo_df)

#add 2021 winner
#sanremo_df.loc[sanremo_df['song']=='ZITTI E BUONI','winner']=1

#manually impute artist type and sex
# Type: 1 for solo artist, 2 for collab or duet, 3 for band
# Sex: 0 for male, 1 for female, 2 for mix/other (considered frontman in bands to elige sex)
#sanremo_df[['song','artist']].to_excel(r"C:\Users\g.valentini\Documents\Projects\Sanremo\src\artist_sex_type.xlsx")
#artist_sex_type = pd.read_excel(r"C:\Users\g.valentini\Documents\Projects\Sanremo\src\artist_sex_type.xlsx")
#sanremo_df = pd.merge(sanremo_df,artist_sex_type,on=['song','artist'])

#sanremo_df.to_excel(r"C:\Users\g.valentini\Documents\Projects\Sanremo\src\sanremo_df.xlsx")
