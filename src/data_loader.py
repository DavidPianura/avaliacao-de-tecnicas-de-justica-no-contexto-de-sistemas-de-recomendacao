from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from dotenv import load_dotenv
from .discogs_api import DiscogsAPI

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

    def __init__(self, file_path: str, separator: str = ',', header: list = None, encoding: str = 'utf-8'):
        load_dotenv()
        self.file_path = file_path
        self.separator = separator
        self.header = header
        self.encoding = encoding
        self.token = 'mDokHVmBVpXhrdfBYEJCJUgxEUipNOQhioIBNpvh'
        self.file_extension = self._infer_file_type()

        self.spark = SparkSession.builder.appName("DataLoader").getOrCreate()

    def _infer_file_type(self) -> str:
        return self.file_path.split('.')[-1]
        
    def load_data(self) -> DataFrame:
        return self._load_csv()

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

    def populate_genres(self, df):
        discogs = DiscogsAPI('mDokHVmBVpXhrdfBYEJCJUgxEUipNOQhioIBNpvh')
