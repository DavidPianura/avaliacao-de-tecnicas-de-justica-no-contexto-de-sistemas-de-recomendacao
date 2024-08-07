from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.ml.recommendation import ALS 

class ALS:

    def __init__(self, dataframe: DataFrame, userColumn: str, itemColumn: str, ratingColumn: str) -> None:
        load_dotenv()

        self.spark = SparkSession.builder.appName("ALSModel").getOrCreate()
        self.df = dataframe

        self.usercol = userColumn
        self.itemcol = itemColumn
        self.ratingcol = ratingColumn

        self.als = self._set_als_model()

    def train_test_split(self):
        ...
    
    def _set_als_model(self) -> ALS:
        als = ALS(maxIter=5, 
                  regParam=0.01, 
                  userCol=self.usercol, 
                  itemCol=self.itemcol, 
                  ratingCol=self.ratingcol, 
                  coldStartStrategy="drop")
        return als

    def _fit_model(self):
        ...
