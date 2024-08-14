from src import *
from sys import exit
import pprint
import warnings

warnings.filterwarnings("ignore")

"""
    ...
"""
def analise(path: str, 
            sep: str, 
            header: list, 
            userColumn: str, 
            itemColumn: str, 
            ratingColumn: str,
            genre_data_path: str,
            genre_data_header: list,
            genre_data_separator: str,
            genre_item_column: str,
            genre_genre_column: str,
            genre_genre_separator: str,
            genre_data_encoding: str = 'utf-8'):
    
    loader = DataLoader(file_path=path,
                        separator=sep,
                        header=header,
                        genre_data_path=genre_data_path,
                        genre_data_header=genre_data_header,
                        genre_data_separator=genre_data_separator,
                        genre_item_column=genre_item_column,
                        genre_genre_column=genre_genre_column,
                        genre_genre_separator=genre_genre_separator,
                        genre_data_encoding=genre_data_encoding)
    
    df = loader.load_data()
    genres_map = loader.get_genre_map()
    (train, test) = loader.train_test_separator(df)

    #### ALS ####
    als = ALSModel(dataframe=df, 
              userColumn=userColumn, 
              itemColumn=itemColumn, 
              ratingColumn=ratingColumn,
              training=train,
              test=test)
    
    predictions = als.get_predictions()
    predictions_user_map = als.predictions_user_map(predictions=predictions)

    distributions = Distributions(train.toPandas(), userColumn, itemColumn, genres_map)

    distributions.show_user_profile_distribution_chart(distributions.get_user_profile_distribution(305))
    distributions.show_userProfileDist_userRecDist(predictions_user_map, 305)

    return
    ## TODO: Avaliação do sistema de recomendação ALS ##
    rs_evaluator = RSEvaluator(map_recommendations= predictions_user_map,
                               test_dataframe=test,
                               userColumn=userColumn,
                               itemColumn=itemColumn)
    
    mrr = rs_evaluator.mean_reciprocal_rank()
    map = rs_evaluator.mean_average_precision()

    # TODO: Calibrar listas
    ...

    # TODO: Avaliação de calibração
    ...

if __name__ == '__main__':

    analise('data/raw/movielens/100K/ml-100k/u.data', 
            sep='\t', 
            header=['userId', 'movieId', 'rating', 'timestamp'],
            userColumn='userId',
            itemColumn='movieId',
            ratingColumn='rating',
            genre_data_path='data/raw/movielens/100K/movies.dat',
            genre_data_separator='::',
            genre_data_header=['itemID', 'itemName', 'genres'],
            genre_item_column='itemID',
            genre_genre_column='genres',
            genre_genre_separator='|',
            genre_data_encoding='ISO-8859-1'
            )

    exit()
    ######################################################################################################
    # MovieLens
    loader_movielens = DataLoader(file_path='data/raw/movielens/100K/ml-100k/u.data',
                                  separator='\t',
                                  header=['userId', 'movieId', 'rating', 'timestamp'])
    df_movielens = loader_movielens.load_data()



    ######################################################################################################
    # LASTFM
    loader_lastfm = DataLoader('data/raw/lastfm/lastfm-dataset-360K/usersha1-artmbid-artname-plays.tsv',
                        separator='\t',
                        header= ['userID', 'artistID', 'artistName', 'plays'],
                        encoding='utf-8'
                        )
    
    df_lastfm = loader_lastfm.load_data()
    df_lastfm.show()


    