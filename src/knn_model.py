import pandas as pd
from sklearn.metrics import jaccard_score
from sklearn.neighbors import NearestNeighbors
import numpy as np

class KNNFBC:

    def __init__(self, 
                 df_user_ratings: pd.DataFrame,
                 user_column: str, 
                 item_column: str,
                 rating_column: str,
                 df_item_metadata: pd.DataFrame) -> None:
        
        self.df_user_ratings = df_user_ratings
        self.df_item_metadata = df_item_metadata

        self.user_column = user_column
        self.rating_column = rating_column
        self.item_column = item_column

        self.knn = NearestNeighbors(metric='jaccard', algorithm='brute')

    def get_model(self) -> NearestNeighbors:
        return self.knn
    
    def fit_model(self, test: pd.DataFrame):
        self.knn.fit(test)

    def _recommend_itens(self, user_id) -> list:
        """
        Função para recomendar itens para o usuário
        """
        
        user_ratings = self.df_user_ratings[(self.df_user_ratings[self.user_column] == user_id) & (self.df_user_ratings[self.rating_column] >= 4)]
        item_ids = user_ratings['item'].tolist()

        recommendations = []

        for movie_id in item_ids:
            movie_idx = self.df_item_metadata[self.df_item_metadata['item'] == movie_id].index[0]
    
    def generate_recommendations(self):
        user_recommendations = {}
        
        for user_id in self.df_user_ratings[self.user_column].unique():
            user_recommendations[user_id] = self._recommend_itens(user_id)
        