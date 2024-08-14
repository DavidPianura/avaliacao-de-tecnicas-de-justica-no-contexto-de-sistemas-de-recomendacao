from .als_model import ALS
from pyspark.sql import DataFrame

class Recommender:

    """
    Classe utilizada para lidar com os diferentes tipos de SR

    Atributos:
        
        model (str): Modelo que será utilizado, podendo ser FC (filtragem colaborativa, usando ALS) ou 
                        FBC (filtragem baseada em conteúdo)
    """
    def __init__(self, model: str, df: DataFrame, userColumn: str) -> None:
        self.model = self.set_model(model)
        self.df = df
        self.userColumn
    
    def set_model(self, model: str):
        possibilidades = ['FC', 'FBC']

        if model.upper() not in possibilidades:
            raise Exception("Modelo nao suportado")
        else:
            self.model = model

    def _als_recomendation(self):
        als = ALS()
    