# Est. time to run: 8 min
import ast
import os
import dotenv
import logging

import numpy as np
from tqdm import tqdm
import pandas as pd
from spoify_api import SpotifyAPI

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)

data_path = '../data/'

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
sp = SpotifyAPI(client_id, client_secret)

# Steps to filter sp_ files
release_df = pd.read_csv(f'{data_path}sp_release.csv')
artist_df = pd.read_csv(f'{data_path}sp_artist_release.csv')
sp_track = pd.read_csv(f'{data_path}sp_track.csv')

target_id = release_df.loc[release_df['popularity'] > 50, 'release_id'].unique()
print('Album count:', len(target_id))

# Filter artists
target_artists = artist_df.loc[artist_df['release_id'].isin(target_id), 'artist_id'].unique()

# Get artist genres
chunck_size = 10
artists_genres_map = {}
for release_id in tqdm(iterable=range(0, len(target_artists), chunck_size),
                       desc='Getting album genres',
                       total=len(target_artists) // chunck_size):
    artists = target_artists[release_id:release_id + chunck_size]
    results = sp.get_several_artists(artists)
    for artist in results['artists']:
        artists_genres_map[artist['id']] = artist['genres']

assert any(bool(genres) for genres in artists_genres_map.values())

# Add genres to artist df
artist_df['genres'] = artist_df['artist_id'].map(artists_genres_map)
# Convert empty lists to NaN
artist_df['genres'] = artist_df['genres'].apply(lambda x: x if x else None)
artist_df.dropna(subset=['genres'], inplace=True)
# Create map with dict[str, list] = release_id:genres
album_genres_map = dict(zip(artist_df['release_id'], artist_df['genres']))

# Filter tracks by target_id
target_tracks = sp_track[sp_track['release_id'].isin(target_id)].copy()
# Merge album genres into target_tracks
target_tracks['genres'] = target_tracks['release_id'].map(album_genres_map)
# Drop unnecessary columns
target_tracks.drop(columns=['track_number', 'release_id', 'disc_number', 'preview_url', 'updated_on'], inplace=True)
# Save data
target_tracks.to_csv(f'{data_path}sample_tracks.csv', index=False)

# Get tracks popularity values
chunck_size = 50
track_popularity_map = {}
for i in tqdm(iterable=range(0, len(target_tracks), chunck_size),
              desc='Getting tracks popularity',
              total=len(target_tracks) // chunck_size):
    tracks: list = target_tracks['track_id'].iloc[i:i + chunck_size].tolist()
    results: dict = sp.get_several_tracks(tracks)
    for track in results['tracks']:
        track_popularity_map[track['id']] = track['popularity']

# Save track_popularity_map to csv
pd.DataFrame(
    track_popularity_map.items(),
    columns=['track_id', 'popularity']
).to_csv(f'{data_path}track_popularity.csv', index=False)

# Read files
popularity_df = pd.read_csv(f'{data_path}track_popularity.csv')
tracks_info = pd.read_csv(f'{data_path}sample_tracks.csv')
audio_features = pd.read_csv(f'{data_path}audio_features.csv')

# Filter with tracks ids
audio_features = audio_features[audio_features['isrc'].isin(tracks_info['isrc'])].copy()
audio_features.drop(columns=['duration_ms', 'updated_on'], inplace=True)

# Merge features
tracks_info = tracks_info.merge(popularity_df, on='track_id', how='left')
tracks_info = tracks_info.merge(audio_features, on='isrc', how='left')

# Save to csv
tracks_info.to_csv(f'{data_path}spotify_data.csv', index=False)
tracks_info.info()


def summarize_genres(data):
    genre_map = {
        'hip hop': 'hip hop',
        'trip hop': 'hip hop',
        'trap': 'hip hop',
        'hop': 'hip hop',
        'hip': 'hip hop',
        'urban contemporary': 'hip hop',
        'wave': 'pop',
        'rap': 'rap',
        'pop': 'pop',
        'rock': 'rock',
        'indie': 'rock',
        'metal': 'rock',
        'punk': 'rock',
        'r&b': 'r&b',
        'jazz': 'r&b',
        'blues': 'r&b',
        'soul': 'r&b',
        # 'classic': 'classic',
        # 'reggae': 'reggae',
        'funk': 'r&b',
        # 'country': 'country',
        # 'video game music': 'soundtrack',
        # 'soundtrack': 'soundtrack',
        'techno': 'eletronic',
        'house': 'eletronic',
        'synth': 'eletronic',
        'trance': 'eletronic',
        'eletronic': 'eletronic',
        'electro': 'eletronic',
        'ambient': 'eletronic',
        'edm': 'eletronic',
        'dubstep': 'eletronic',
        'drum and bass': 'eletronic',
        'dance': 'eletronic',
        'disco': 'eletronic',
        'psychedelic': 'eletronic',
        'beat': 'eletronic',
        'lo-fi': 'eletronic',
        'downbeat': 'eletronic',
        'downtempo': 'eletronic',
        'chill': 'eletronic',
    }
    x = data.copy()
    for index, value in enumerate(x):
        for genre, category in genre_map.items():
            if genre in value:
                x[index] = category
                break
            x[index] = np.nan
    # Remove np.nan from the list
    x = [i for i in x if i is not np.nan]
    # Select unique values
    x = np.unique(x)
    if len(x) == 0:
        x = np.nan
    return x


df = pd.read_csv('data/spotify_data.csv')
df.drop(columns=['track_id', 'track_title', 'isrc'], inplace=True)
df = df.loc[df['instrumentalness'] != 0]
df = df.loc[df['duration_ms'] < 1e6]
df.dropna(subset=['genres', 'key'], inplace=True)
df['genres'] = df['genres'].apply(ast.literal_eval)
df['genres'] = df['genres'].apply(summarize_genres)
df.to_csv('data/spotify_data_cleaned.csv', index=False)
