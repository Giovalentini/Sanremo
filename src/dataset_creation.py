#import libraries
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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

#get each song id, title and artist for all playlists
def get_ids_from_playlist(lista_uri):
    '''
    Returns lists of song id, title and artist for all playlists
    '''
    ids=[[] for _ in range(len(lista_uri))]
    track_list = [[] for _ in range(len(lista_uri))]
    artist_list = [[] for _ in range(len(lista_uri))]

    for j,uri in enumerate(lista_uri):
        try:
            results = spotify.playlist(uri)
        except:
            print(f"the playlist '{uri}' contains at least one song which no longer exists on spotify")

        for i in range(len(results['tracks']['items'])):
            ids[j].append(results['tracks']['items'][i]['track']['id'])
            track_list[j].append(results['tracks']['items'][i]['track']['name'])
            artist_list[j].append(results['tracks']['items'][i]['track']['artists'][0]['name'])

    return ids, track_list, artist_list

ids_list, track_list, artist_list = get_ids_from_playlist(lista_uri)

# Function to adjust list length to include only bigs (some playlists include rookies too)
def exclude_rookies(bigs_per_year, tot_years):
    '''
    adjust list length to exclude rookies 
    '''
    for i in range(tot_years):
        ids_list[i] = ids_list[i][:bigs_per_year[i]]
        track_list[i] = track_list[i][:bigs_per_year[i]]
        artist_list[i] = artist_list[i][:bigs_per_year[i]]

    return ids_list, track_list, artist_list

bigs_per_year = (24,26,24,24,19,22,18,19,11,13,14,14,14)
tot_years = len(lista_uri)

ids_list, track_list, artist_list = exclude_rookies(bigs_per_year, tot_years)


#now I have all bigs songs ids. Next step: extract track features and put them in a df

def extract_song_features(ids_list):
    '''
    Returns a pandas dataframe with track features
    '''
    df = pd.DataFrame()

    # iterate over the list of all songs ids
    for i,lista in enumerate(ids_list):
        
        # iterate over the list of each year songs ids
        for track_id in lista:

            try:
                song = spotify.audio_features(track_id)
                df = df.append({'danceability': song[0]['danceability'],
                                'energy': song[0]['energy'],
                                'key': song[0]['key'],
                                'loudness': song[0]['loudness'],
                                'mode': song[0]['mode'],
                                'speechiness': song[0]['speechiness'],
                                'acousticness': song[0]['acousticness'],
                                'instrumentalness': song[0]['instrumentalness'],
                                'liveness': song[0]['liveness'],
                                'valence': song[0]['valence'],
                                'tempo': song[0]['tempo'],
                                'duration_ms': song[0]['duration_ms'],
                                'time_signature': song[0]['time_signature'],
                                'year': years[i]}, ignore_index=True)

            except:
                print(track_id,song)
    
    return df

sanremo_df = extract_song_features(ids_list=ids_list)

#there's one track_id which doesn't work - 4WJVLEkcMMV2tHo1Bd65VN

#add winner column - first of each playlist is a winner except for 2021
def add_winner(df):
    '''
    Add winner column  - first of each playlist is a winner except for 2021
    '''
    bigs_per_year_cum = np.cumsum(bigs_per_year)
    df['winner']=0

    for i in range(len(df)):
        if i in bigs_per_year_cum:
            df.loc[i,'winner'] = 1

    return df

sanremo_df = add_winner(sanremo_df)

#add title and artist
def add_title_and_artist(df):
    '''
    Add title and artist to sanremo dataframe
    '''
    unique_track_list = []
    unique_artist_list = []

    for l1,l2 in zip(track_list,artist_list):
        for track,artist in zip(l1,l2):
            unique_track_list.append(track)
            unique_artist_list.append(artist)

    # add columns
    df['song']=unique_track_list
    df['artist']=unique_artist_list

    return df 

sanremo_df = add_title_and_artist(sanremo_df)

#add 2021 winner
#sanremo_df.loc[sanremo_df['song']=='ZITTI E BUONI','winner']=1

#manually impute artist type and sex
# Type: 1 for solo artist, 2 for collab or duet, 3 for band
# Sex: 0 for male, 1 for female, 2 for mix/other (considered frontman in bands to elige sex)
#sanremo_df[['song','artist']].to_excel(r"C:\Users\g.valentini\Documents\Projects\Sanremo\src\artist_sex_type.xlsx")
artist_sex_type = pd.read_excel(r"C:\Users\g.valentini\Documents\Projects\Sanremo\src\artist_sex_type.xlsx")
sanremo_df = pd.merge(sanremo_df,artist_sex_type,on=['song','artist'])

#sanremo_df.to_excel(r"C:\Users\g.valentini\Documents\Projects\Sanremo\src\sanremo_df.xlsx")
