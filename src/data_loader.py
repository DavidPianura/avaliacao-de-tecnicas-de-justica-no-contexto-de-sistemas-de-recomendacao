import polars as pl
from discogs_api import DiscogsAPI

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
        self.file_path = file_path
        self.separator = separator
        self.header = header
        self.encoding = encoding
        self.token = 'mDokHVmBVpXhrdfBYEJCJUgxEUipNOQhioIBNpvh'
        self.file_extension = self._infer_file_type()

    def _infer_file_type(self) -> str:
        return self.file_path.split('.')[-1]
        
    def load_data(self) -> pl.DataFrame:
        if self.file_extension == 'json':
            return self._load_json()
        else:
            return self._load_csv()
        
    def _load_json(self) -> pl.DataFrame:
        return pl.read_json(self.file_path)

    def _load_csv(self) -> pl.DataFrame:
        return pl.read_csv(self.file_path, 
                           has_header=self.header is None,
                           separator=self.separator, 
                           new_columns = None if self.header is None else self.header, 
                           encoding=self.encoding,
                           null_values=[r'\N'])
    
    def populate_genres(self, df):
        ...
