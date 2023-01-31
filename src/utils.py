import logging
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class SanremoDatasetCreator:

    def __init__(self, bigs_per_year, tot_years, years):
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        self.bigs_per_year = bigs_per_year
        self.tot_years = tot_years
        self.years = years

    def get_ids_from_playlist(self, lista_uri: list):
        """
        Returns lists of song id, title and artist for all playlists
        """
        ids = [[] for _ in range(len(lista_uri))]
        track_list = [[] for _ in range(len(lista_uri))]
        artist_list = [[] for _ in range(len(lista_uri))]
        artist_count = [[] for _ in range(len(lista_uri))]

        for j, uri in enumerate(lista_uri):
            results = self.spotify.playlist(uri)
            results = {}
            try:
                results = self.spotify.playlist(uri)
            except:
                print(f"the playlist '{uri}' contains at least one song which no longer exists on spotify")
                pass

            for i in range(len(results['tracks']['items'])):
                ids[j].append(results['tracks']['items'][i]['track']['id'])
                track_list[j].append(results['tracks']['items'][i]['track']['name'])
                artist_list[j].append(
                    " & ".join([artist['name'] for artist in results['tracks']['items'][i]['track']['artists']])
                )
                artist_count[j].append(len(results['tracks']['items'][i]['track']['artists']))

        return ids, track_list, artist_list, artist_count

    def exclude_rookies(self, ids_list, track_list, artist_list, artist_count):
        """
        adjust list length to exclude rookies
        """
        for i in range(self.tot_years):
            ids_list[i] = ids_list[i][:self.bigs_per_year[i]]
            track_list[i] = track_list[i][:self.bigs_per_year[i]]
            artist_list[i] = artist_list[i][:self.bigs_per_year[i]]
            artist_count[i] = artist_count[i][:self.bigs_per_year[i]]

        return ids_list, track_list, artist_list, artist_count

    def extract_song_features(self, ids_list):
        """
        Returns a pandas dataframe with track features
        """
        df = pd.DataFrame()

        # iterate over the list of all songs ids
        for i, lista in enumerate(ids_list):

            # iterate over the list of each year songs ids
            for j,track_id in enumerate(lista):
                
                try:
                    song = self.spotify.audio_features(track_id)
                    df = df.append({'danceability':song[0]['danceability'],
                                    'energy':song[0]['energy'],
                                    'key':song[0]['key'],
                                    'loudness':song[0]['loudness'],
                                    'mode':song[0]['mode'],
                                    'speechiness':song[0]['speechiness'],
                                    'acousticness':song[0]['acousticness'],
                                    'instrumentalness':song[0]['instrumentalness'],
                                    'liveness':song[0]['liveness'],
                                    'valence':song[0]['valence'],
                                    'tempo':song[0]['tempo'],
                                    'duration_ms':song[0]['duration_ms'],
                                    'time_signature':song[0]['time_signature'],
                                    'year': self.years[i]}, ignore_index=True)

                except:
                    logging.warning(f" missing element #{j} in list #{i}")

        return df

    def add_winner(self,df):
        """
        Add winner column  - first of each playlist is a winner
        """
        bigs_per_year_cum = np.cumsum(self.bigs_per_year)
        bigs_per_year_cum = np.sort(np.append(bigs_per_year_cum, 0))
        df['winner']=0

        for i in range(len(df)):
            if i in bigs_per_year_cum:
                df.loc[i,'winner'] = 1
        
        return df

    #add title and artist
    def add_title_and_artist(
        self,
        df:pd.DataFrame,
        track_list:list,
        artist_list:list,
        artist_count:list
    ) -> pd.DataFrame:
        '''
        Add title and artist to sanremo dataframe
        '''
        unique_track_list = []
        unique_artist_list = []
        unique_count_list = []

        for l1,l2,l3 in zip(track_list,artist_list,artist_count):
            for track,artist,count in zip(l1,l2,l3):
                unique_track_list.append(track)
                unique_artist_list.append(artist)
                unique_count_list.append(count)


        # 20230128: removing one element without track features
        #unique_track_list.remove("biggio e mandelli vita d inferno lyric video 4207191295023505344")
        #unique_artist_list.remove("")

        # add columns
        df['song'] = unique_track_list
        df['artist'] = unique_artist_list
        df['number_of_artists'] = unique_count_list
    
        return df