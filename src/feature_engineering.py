from ast import literal_eval
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class columnDropperTransformer():
    def __init__(self,columns):
        self.columns=columns

    def transform(self,X,y=None):
        return X.drop(self.columns,axis=1)

    def fit(self, X, y=None):
        return self 

class TransformFeatures(BaseEstimator, TransformerMixin):
    def __init__(self, summarize_genres: bool = False):
        self.summarize_genres = summarize_genres
        self.key_mapping = {
            0: 'C (also B♯, D𝄫)',
            1: 'C♯, D♭ (also B𝄪)',
            2: 'D (also C𝄪, E𝄫)',
            3: 'D♯, E♭ (also F𝄫)',
            4: 'E (also D𝄪, F♭)',
            5: 'F (also E♯, G𝄫)',
            6: 'F♯, G♭ (also E𝄪)',
            7: 'G (also F𝄪, A𝄫)',
            8: 'G♯, A♭',
            9: 'A (also G𝄪, B𝄫)',
            10: 'A♯, B♭ (also C𝄫)',
            11: 'B (also A𝄪, C♭)',
            -1: 'Unknown'
        }
        self.time_signature_map = {
            0: '0/4',
            1: '1/4',
            3: '3/4',
            4: '4/4',
            5: '5/4',
            7: '7/4',
            -1: 'Unknown'
        }
        self.mode_map = {
            0: 'Minor',
            1: 'Major'
        }
        # self.explicit_map = {
        #     'f': 0,
        #     't': 1
        # }
        self.genre_map = {
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
            'funk': 'r&b',
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
    
    def fit(self, X, y=None):
        return self
    
    def apply_summarize_genres(self, data):
        x = data.copy()
        for index, value in enumerate(x):
            for genre, category in self.genre_map.items():
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

    def transform(self, X):

        # Map categorical variables
        X['mode'] = X['mode'].map(self.mode_map)
        X['key'] = X['key'].map(self.key_mapping)
        X['time_signature'] = X['time_signature'].map(self.time_signature_map)
        # X['explicit'] = X['explicit'].map({'f': 0, 't': 1})

        # Force variable eval
        if 'genres' in X.columns:
            # Cast to list
            X['genres'] = X['genres'].dropna().apply(literal_eval)

            if self.summarize_genres:
                X['genres'] = X['genres'].dropna().apply(self.apply_summarize_genres)
            # Explode values
            dummies = pd.get_dummies(X['genres'].explode()).groupby(level=0).sum()
            # Concat values
            X = pd.concat([X, dummies], axis=1)
            X = X.drop(columns='genres')
        
        return X
    

class CreateFeatures(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
        
    def fit(self, X, y=None):
        return self

    def transform(self, X):        

        bins = [0, 0.33, 0.66, 1]
        labels = ['Low', 'Medium', 'High']
    
        X['acoustic_level'] = pd.cut(X['acousticness'], bins=bins, labels=labels)
        X['danceability_level'] = pd.cut(X['danceability'], bins=bins, labels=labels)
        X['energy_level'] = pd.cut(X['energy'], bins=bins, labels=labels)
        X['loudness_level'] = pd.cut(X['loudness'], bins=3, labels=['Low', 'Medium', 'High'])
        
        bins = [0, 0.5, 1]
        labels = ['Vocal', 'Instrumental']
        X['instrumental'] = pd.cut(X['instrumentalness'], bins=bins, labels=labels)
        
        bins = [0, 0.8, 1]
        labels = ['Studio Recorded', 'Live Performance']
        X['live_performance'] = pd.cut(X['liveness'], bins=bins, labels=labels)
        
        bins = [0, 0.33, 0.66, 1]
        labels = ['Music', 'Music and Speech', 'Speech']
        X['speech_content'] = pd.cut(X['speechiness'], bins=bins, labels=labels)
        
        bins = [0, 0.33, 0.66, 1]
        labels = ['Negative', 'Neutral', 'Positive']
        X['mood'] = pd.cut(X['valence'], bins=bins, labels=labels)

        if 'popularity' in X.columns:
            bins = [0, 20, 40, 60, 80, 100]
            labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
            X['popularity_level'] = pd.cut(X['popularity'], bins=bins, labels=labels)
        
        return X

