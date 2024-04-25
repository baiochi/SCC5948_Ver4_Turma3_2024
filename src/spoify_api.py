import requests
import base64
import time


class SpotifyAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self._get_token()

    def _get_token(self):
        url = 'https://accounts.spotify.com/api/token'
        auth_string = self.client_id + ':' + self.client_secret
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

    def get_artist(self, artist_name):
        url = 'https://api.spotify.com/v1/search'
        headers = {
            'Authorization': 'Bearer ' + self.token,
        }
        params = {
            'q': artist_name,
            'type': 'artist',
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def get_several_artists(self, artist_ids: list):
        url = 'https://api.spotify.com/v1/artists'
        headers = {
            'Authorization': 'Bearer ' + self.token,
        }
        params = {
            'ids': ','.join(artist_ids),
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def get_several_albums(self, album_ids: list):
        url = 'https://api.spotify.com/v1/albums/'
        headers = {
            'Authorization': 'Bearer ' + self.token,
        }
        params = {
            'ids': ','.join(album_ids),
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def get_track_features(self, track_id: str, timeout: int = 3):
        url = f'https://api.spotify.com/v1/audio-features/{track_id}'
        headers = {
            'Authorization': 'Bearer ' + self.token,
        }
        timeout = 3
        for _ in range(timeout):
            response = requests.get(url, headers=headers)
            if response.status_code != 429:
                return response.json()
            retry_after = int(response.headers.get('Retry-After', 1))
            print(f'Rate limited. Retrying in {retry_after} seconds')
            time.sleep(retry_after)
        raise Exception('Maximum number of retries exceeded')

    def get_several_tracks(self, track_ids: list):
        url = 'https://api.spotify.com/v1/tracks'
        headers = {
            'Authorization': 'Bearer ' + self.token,
        }
        params = {
            'ids': ','.join(track_ids),
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def get_market(self):
        url = 'https://api.spotify.com/v1/markets'
        headers = {
            'Authorization': 'Bearer ' + self.token,
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def get_featured_playlists(self, locale=None, limit=20, offset=0):
        url = 'https://api.spotify.com/v1/browse/featured-playlists'
        headers = {
            'Authorization': 'Bearer ' + self.token,
        }
        params = {
            'locale': locale,
            'limite': limit,
            'offset': offset,
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()
