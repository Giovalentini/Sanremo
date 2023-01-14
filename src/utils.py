# useful functions
import pandas as pd

#get each song id, title and artist for all playlists
def get_ids_from_playlist(lista_uri:list):
    '''
    Returns lists of song id, title and artist for all playlists
    '''
    ids=[[] for _ in range(len(lista_uri))]
    track_list = [[] for _ in range(len(lista_uri))]
    artist_list = [[] for _ in range(len(lista_uri))]

    for j,uri in enumerate(lista_uri):
        results = spotify.playlist(uri)
        results = {}
        try:
            results = spotify.playlist(uri)
            print(results)
        except:
            print(f"the playlist '{uri}' contains at least one song which no longer exists on spotify")
            pass

        for i in range(len(results['tracks']['items'])):
            ids[j].append(results['tracks']['items'][i]['track']['id'])
            track_list[j].append(results['tracks']['items'][i]['track']['name'])
            artist_list[j].append(results['tracks']['items'][i]['track']['artists'][0]['name'])

    return ids, track_list, artist_list

# Function to adjust list length to include only bigs (some playlists include rookies too)
def exclude_rookies(bigs_per_year:tuple, tot_years:int):
    '''
    adjust list length to exclude rookies 
    '''
    for i in range(tot_years):
        ids_list[i] = ids_list[i][:bigs_per_year[i]]
        track_list[i] = track_list[i][:bigs_per_year[i]]
        artist_list[i] = artist_list[i][:bigs_per_year[i]]

    return ids_list, track_list, artist_list

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

#add title and artist
def add_title_and_artist(
    df:pd.DataFrame
) -> pd.DataFrame:
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