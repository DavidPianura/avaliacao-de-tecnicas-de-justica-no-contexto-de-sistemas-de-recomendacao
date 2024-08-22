from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.ml.recommendation import ALS 
import pandas as pd

class ALSModel:

    def __init__(self, 
                 dataframe: DataFrame, 
                 userColumn: str, 
                 itemColumn: str, 
                 ratingColumn: str, 
                 training: DataFrame, 
                 test: DataFrame) -> None:
        
        load_dotenv()

        self.spark = SparkSession.builder.appName("ALSModel").getOrCreate()
        self.df = dataframe

        self.usercol = userColumn
        self.itemcol = itemColumn
        self.ratingcol = ratingColumn

        (self.training, self.test) = (training, test)
        self.model = self._fit_model()

    def _train_test_split(self) -> tuple:
        (training, test) = self.df.randomSplit([0.8, 0.2])
        return (training, test)
        
    
    def _set_als_model(self) -> ALS:
        als = ALS(maxIter=5, 
                  regParam=0.01, 
                  userCol=self.usercol, 
                  itemCol=self.itemcol, 
                  ratingCol=self.ratingcol, 
                  coldStartStrategy="drop")
        return als

    def _fit_model(self):
        als = self._set_als_model()

        model = als.fit(self.training)
        return model
    
    def make_test_predictions(self):
        predictions = self.model.transform(self.test)
        return predictions
    
    def get_predictions(self, number_of_recomendations: int = 100) -> pd.DataFrame:
        userRec = self.model.recommendForAllUsers(number_of_recomendations) 
        userRecsOnlyItemId = userRec.select(userRec['userId'], userRec['recommendations'])
        return userRecsOnlyItemId.toPandas()
    
    def get_test_predictions(self) -> pd.DataFrame:
        # Gera as previsões para o conjunto de testes
        predictions = self.model.transform(self.test)
        
        # Seleciona as colunas de interesse: userId, itemId e prediction
        selected_predictions = predictions.select(self.usercol, self.itemcol, "prediction")
        
        # Converte o resultado para um DataFrame do pandas
        return selected_predictions.toPandas()
    
    def predictions_user_map(self, predictions: pd.DataFrame) -> dict:
        user_map = {}
        for user_id, rows in predictions.set_index('userId')['recommendations'].items():
            # Converte as linhas de recomendação em uma lista de tuplas (movieId, rating)
            user_map[user_id] = [(row.movieId, row.rating) for row in rows]
        
        return user_map     

    