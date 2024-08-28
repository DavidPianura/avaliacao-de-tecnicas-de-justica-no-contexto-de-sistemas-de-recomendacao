from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from dotenv import load_dotenv
import pandas as pd
from .discogs_api import DiscogsAPI

import warnings

warnings.filterwarnings("ignore")

class DataLoader:
    """
    Classe utilizada para carregar os diversos tipos de conjuntos de dados contidos no projeto

    Atributos:
        file_path (str): Caminho para o arquivo de dados.
        separator (str): Separador dos campos no arquivo. Padrão é ','.
        header (list): Lista de nomes das colunas, caso o arquivo não tenha cabeçalho.
        encoding: Codificador utilizado pelo arquivo. Por padrão, é utf-8.
        file_type (str): inferido pela classe.
    """

    def __init__(self, 
                 file_path: str, 
                 separator: str = ',', 
                 header: list = None, 
                 encoding: str = 'utf-8',
                 genre_data_path: str = None,
                 genre_data_separator = None,
                 genre_data_header: list = None,
                 genre_data_encoding: str = 'utf-8',
                 genre_item_column: str = None,
                 genre_genre_column: str = None,
                 genre_genre_separator: str = None,
                 genre_data: pd.DataFrame = None):
        
        load_dotenv()
        self.file_path = file_path
        self.separator = separator
        self.header = header
        self.encoding = encoding
        self.token = 'mDokHVmBVpXhrdfBYEJCJUgxEUipNOQhioIBNpvh'
        self.file_extension = self._infer_file_type()

        self.spark = SparkSession.builder.appName("DataLoader").getOrCreate()

        # Metadados de gêneros
        self.genre_data_path = genre_data_path
        self.genre_data_separator = self.separator if genre_data_separator is None else genre_data_separator
        self.genre_data_header = genre_data_header
        self.genre_data_encoding = genre_data_encoding
        self.genre_item_column = genre_item_column
        self.genre_genre_column = genre_genre_column
        self.genre_genre_separator = genre_genre_separator
        self.genre_data = self._load_genres_data() if genre_data is None else genre_data

        

    def _infer_file_type(self) -> str:
        return self.file_path.split('.')[-1]
        
    def load_data(self) -> DataFrame:
        return self._load_csv()

    def convert_to_pandas(self, df: DataFrame):
        return df.toPandas()

    def _load_csv(self) -> DataFrame:
        df =  self.spark.read.csv(
                                    self.file_path,
                                    sep=self.separator,
                                    inferSchema=True,
                                    nullValue=r'\N',
                                    encoding=self.encoding,
                                )
        df = df.toDF(*self.header)
        return df
    
    def data_to_csv(self, df: DataFrame, destination: str) -> None:
        df.coalesce(1).write.option("header", "true").csv(destination)

    def _load_genres_data(self) -> pd.DataFrame:
        genres = pd.read_csv(self.genre_data_path, sep = self.genre_data_separator, names=self.genre_data_header, encoding=self.genre_data_encoding)
        genres = genres[[self.genre_item_column, self.genre_genre_column]]
        genres = genres.rename(columns={self.genre_item_column: 'item', self.genre_genre_column: 'genres'})
        return genres
    
    def get_genre_map(self) -> dict:
        genre_map = {i['item']:i['genres'].split(self.genre_genre_separator) for i in self.genre_data[['item', 'genres']].to_dict('records')}
        return genre_map

    def train_test_separator(self, df: DataFrame) -> tuple:
        (training, test) = df.randomSplit([0.8, 0.2])
        return (training, test)
