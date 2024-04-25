import requests
import base64
import pandas as pd

CLIENT_ID = '9a7fb42ac1d34d769d2285abd9648079'
CLIENT_SECRET = '32cfff138ace44f7bfddcc9233151e1c'


def _get_token(client_id, client_secret):
    url = 'https://accounts.spotify.com/api/token'
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes)

    headers = {
        'Authorization': 'Basic ' + auth_base64.decode('utf-8'),
    }
    data = {
        'grant_type': 'client_credentials',
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()['access_token']


def get_playlist_tracks(token, playlist_id, limit=100, offset=0):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {
        'Authorization': 'Bearer ' + token,
    }
    params = {
        'limit': limit,
        'offset': offset,
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def get_playlist_artists(playlists: dict):
    all_artists = {}
    for name, id in playlists.items():
        tracks = get_playlist_tracks(TOKEN, id, limit=100, offset=0)
        for item in tracks['items']:
            track_artists = {artist['id']: artist['name'] for artist in item['track']['artists']}
            # Update all_artists with the new artists
            all_artists.update(track_artists)
    return all_artists


def get_all_categories(token, locale=None, limit=20, offset=0):
    url = 'https://api.spotify.com/v1/browse/categories'
    headers = {
        'Authorization': 'Bearer ' + token,
    }
    params = {
        'locale': locale,
        'limit': limit,
        'offset': offset,
    }
    response = requests.get(url, headers=headers, params=params)
    categories = response.json()
    categories = {item['id']: item['name'] for item in categories['categories']['items']}
    return categories


def get_categorie_playlists(token, category_id, limit=20, offset=0):
    url = f'https://api.spotify.com/v1/browse/categories/{category_id}/playlists'
    headers = {
        'Authorization': 'Bearer ' + token,
    }
    params = {
        'limit': limit,
        'offset': offset,
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def get_artist_info(token, artist_id: list):
    url = f'https://api.spotify.com/v1/artists/'
    headers = {
        'Authorization': 'Bearer ' + token,
    }
    params = {
        'ids': ','.join(artist_id),
    }
    if len(artist_id) > 50:
        raise ValueError('Too many artist ids')
    response = requests.get(url, headers=headers, params=params)
    return response.json()


TOKEN = _get_token(CLIENT_ID, CLIENT_SECRET)


categories = get_all_categories(TOKEN, limit=50, offset=0)

all_artists = {}
for id, name in categories.items():
    print('Category:', name)
    playlists = get_categorie_playlists(TOKEN, id, limit=50, offset=0)['playlists']
    playlists = {i['name']: i['id'] for i in playlists['items']}

    for name, id in playlists.items():
        tracks = get_playlist_tracks(TOKEN, id, limit=100, offset=0)
        for item in tracks['items']:
            if item['track'] is None:
                continue
            track_artists = {artist['id']: artist['name'] for artist in item['track']['artists']}
            # Update all_artists with the new artists
            all_artists.update(track_artists)

        print(name, len(all_artists))

artists_df = pd.DataFrame(all_artists.items(), columns=['id', 'artist'])

artist_info = {}
for i in range(0, len(artists_df), 50):
    ids = artists_df['id'].iloc[i:i+50].tolist()
    info = get_artist_info(TOKEN, ids)
    for artist_id, info in zip(ids, info['artists']):
        artist_info[artist_id] = {
            'name': info['name'],
            'genres': info['genres'],
            'popularity': info['popularity'],
        }

artist_df = pd.DataFrame(artist_info).T.reset_index().rename(columns={
    'index': 'artist_id',
    'name': 'artist_name',
})

artists_df.to_csv('data/top_categories_artists.csv', index=False, encoding='utf-8')
