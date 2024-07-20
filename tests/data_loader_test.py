from src.data_loader import DataLoader
import polars as pl

base_path = 'data/raw/'

"""
TODO:
    Testes para os datasets:
        - yahoo movies
        - netlix prize
        - movielens
        - lastfm
        - imdb
"""

def test_yahoo_music_user_artist_rating_file_type():
    loader = DataLoader(base_path + 'yahoo_music/dataset/ydata-ymusic-user-artist-ratings-v1_0.txt', 
                      separator='\t', 
                      header = ['anonymous_user_id', 'artist_id', 'rating'])
    assert loader._infer_file_type() == 'txt'
    
def test_yahoo_music_user_artist_rating_load_data():
    loader = DataLoader(base_path + 'yahoo_music/dataset/ydata-ymusic-user-artist-ratings-v1_0.txt', 
                      separator='\t', 
                      header = ['anonymous_user_id', 'artist_id', 'rating'])
    df = loader.load_data()
    assert isinstance(df, pl.DataFrame)
    assert df.shape == (115579440, 3)
    assert df.columns == ['anonymous_user_id', 'artist_id', 'rating']

def test_yahoo_music_artist_names_file_type():
    loader = DataLoader(base_path + 'yahoo_music/dataset/ydata-ymusic-artist-names-v1_0.txt')
    assert loader._infer_file_type() == 'txt'

def test_yahoo_music_artist_names_load_data():
    loader = DataLoader(base_path + 'yahoo_music/dataset/ydata-ymusic-artist-names-v1_0.txt',
                        separator='\t',
                        header=['artistID', 'artistName'],
                        encoding='iso-8859-1')
    df = loader.load_data()
    assert isinstance(df, pl.DataFrame)
    assert df.shape == (97956, 2)
    assert df.columns == ['artistID', 'artistName']
