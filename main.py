from src import *

if __name__ == '__main__':
    loader = DataLoader('data/raw/lastfm/lastfm-dataset-360K/usersha1-artmbid-artname-plays.tsv',
                        separator='\t',
                        header= ['userID', 'artistID', 'artistName', 'plays'],
                        encoding='utf-8'
                        )
    df = loader.load_data()

    df.show()
    