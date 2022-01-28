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

#ids of all playlists - order from 2021 to 2010
#37i9dQZF1DWVQfeA9N7Q0g
lista_uri=['spotify:playlist:61QFMC1ntb7BrXveI3f4cX',
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
anno_fine = 2021
years=[i for i in reversed(range(anno_inizio,anno_fine+1))]

#lista_uri=['spotify:playlist:13TbnOluHonxsVvSWkL7YF'] #1990-2021 in un'unica playlist

#get each song id, title and artist for all playlists
def get_ids_from_playlist(lista_uri):
    ids=[[] for _ in range(len(lista_uri))]
    track_list = [[] for _ in range(len(lista_uri))]
    artist_list = [[] for _ in range(len(lista_uri))]
    for j,uri in enumerate(lista_uri):
        results = spotify.playlist(uri)
        for i in range(len(results['tracks']['items'])):
            ids[j].append(results['tracks']['items'][i]['track']['id'])
            track_list[j].append(results['tracks']['items'][i]['track']['name'])
            artist_list[j].append(results['tracks']['items'][i]['track']['artists'][0]['name'])
    return ids, track_list, artist_list

ids_list, track_list, artist_list = get_ids_from_playlist(lista_uri)

#adjust list length to include only bigs (some playlists include "esordienti" too)
bigs_per_year = (26,24,24,19,22,18,19,11,13,14,14,14)
tot_years = 12
for i in range(tot_years):
    ids_list[i]    = ids_list[i][:bigs_per_year[i]]
    track_list[i]  = track_list[i][:bigs_per_year[i]]
    artist_list[i] = artist_list[i][:bigs_per_year[i]]

#now I have all bigs songs ids. Next step: extract track features and put them in a df
sanremo_df = pd.DataFrame()
for i,lista in enumerate(ids_list):
    for track_id in lista:
        song = spotify.audio_features(track_id)
        sanremo_df = sanremo_df.append({'danceability': song[0]['danceability'],
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

#add winner column - first of each playlist is a winner except for 2021
bigs_per_year_cum = np.cumsum(bigs_per_year)
sanremo_df['winner']=0
for i in range(len(sanremo_df)):
    if i in bigs_per_year_cum:
        sanremo_df.loc[i,'winner'] = 1

#add title and artist
unique_track_list = []
unique_artist_list = []
for l1,l2 in zip(track_list,artist_list):
    for track,artist in zip(l1,l2):
        unique_track_list.append(track)
        unique_artist_list.append(artist)

sanremo_df['song']=unique_track_list
sanremo_df['artist']=unique_artist_list

#add 2021 winner
sanremo_df.loc[sanremo_df['song']=='ZITTI E BUONI','winner']=1

#manually impute artist type and sex
# Type: 1 for solo artist, 2 for collab or duet, 3 for band
# Sex: 0 for male, 1 for female, 2 for mix/other (considered frontman in bands to elige sex)
# sanremo_df[['song','artist']].to_excel("G:/Il mio Drive/Sanremo/artist_sex_type.xlsx")
artist_sex_type = pd.read_excel("G:/Il mio Drive/Sanremo/artist_sex_type.xlsx")
sanremo_df = pd.merge(sanremo_df,artist_sex_type,on=['song','artist'])

#sanremo_df.to_excel("G:/Il mio Drive/Sanremo/sanremo_df.xlsx")
