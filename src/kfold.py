from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from sklearn.model_selection import StratifiedKFold
import pandas as pd
from typing import Literal
from .als_model import ALSModel
from .data_loader import DataLoader
from dotenv import load_dotenv
from .calibration import Calibration
from statistics import stdev

"""
    Statistics
    TODO:
    histograma de itens consumidos por usuários
"""

class KFOLD:
    """
    Classe utilizada para ralizar os experimentos com base em k-fold cross validation, com k = 5 (podendo ser alterado).

    A classe possui o método run_cross_validation, que realiza os passos:
        1) Constrói o modelo
        2) Cria a lista de recomendações para os usuários
        3) Calibra a lista utilizando o algoritmo proposto por Steck para λ no intervalo de 0 até 1 com passo de 0,1
            3.1) Para cada um desses λ, são utilizadas as medidas de justiça:
                - Kullback-Leibler
                - Hellinger
                - Pearson chi-square
            3.2) Seleciona os top10 itens após esse passo pós-processual de calibração
            3.3) As métricas são caculadas baseadas nos top 10 itens
                3.3.1) Métricas de justiça: 
                        - Mean average calibration error (MACE)
                        - Mean rank miscalibration (MRMC)
                      Métricas para avaliação do sistema de recomendação:
                        - Mean average precision (MAP)
                        - Mean reciprocal rank (MRR)
        O método retorna uma tabela em formato de dataframe com os resultados separados por λ, medida de justiça, métricas.

    Atributos:
        dataframe (pd.Dataframe): conjunto de dados utilizados para realização do experimento
        model_type (Literal['FC', 'FBC']): tipo de modelo avaliado, podendo ser FC (ALS) ou FBC (kNN).
        random_state (int): utilizado como parâmetro do objeto KFold da classe sklean.model_selection. Por padrão,
            seu valor é 42
        n_folds (int): número de folds utilizados no cross_validation. Por padrão, seu valor é 5.
    """

    def __init__(self, 
                 dataframe: pd.DataFrame, 
                 model_type: Literal['FC', 'FBC'],
                 userColumn: str,
                 itemColumn: str,
                 ratingColumn: str,
                 genre_map: dict,
                 random_state: int = 42, 
                 n_folds: int = 5) -> None:
        
        load_dotenv()
        self.spark = SparkSession.builder.appName("kFOLD").getOrCreate()

        self.df = dataframe
        self.userColumn = userColumn
        self.itemColumn = itemColumn
        self.ratingColumn = ratingColumn
        self.n_folds = n_folds
        # Stratified kfold
        self.kf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
        self.model_type = model_type
        self.genre_map = genre_map

    def run_cross_validation(self) -> pd.DataFrame:
        i = 1
        results = pd.DataFrame()

        df_spark = self.spark.createDataFrame(self.df)
        if self.model_type == 'FC':
            print(f'{i}) Running FC')

            for lamb in range(0, 1.1, 0.1):
                
                print(f'Lambda = {lamb}')
                mace = []
                mrmc = []
                mapMeasure = []
                mrr = []

                for fairness_measure in ['kullback-leibler', 'hellinger', 'pearson']:
                    print(F'!FAIRNESS MEASURE: {fairness_measure}!')
                    
                    for train_idx, test_idx in self.kf.split(self.df, y=self.df[self.userColumn]):
                        print("="+5 + f'{i}º Fold' + "="*5)

                        # Separação entre treino e teste (com conversão para dataframe do spark, visto que o método ALS pertence
                        # ao spark)
                        print(f'Train/test spliting')
                        train = self.df.iloc[train_idx]
                        train_spark = self.spark.createDataFrame(train)
                        test = self.df.iloc[test_idx]
                        test_spark = self.spark.createDataFrame(test)
                        
                        # Instanciando ALS
                        print('Instantiating ALS...')
                        als = ALSModel(dataframe=df_spark, 
                                        userColumn=self.userColumn, 
                                        itemColumn=self.itemColumn, 
                                        ratingColumn=self.ratingColumn,
                                        training=train_spark,
                                        test=test_spark)
                        
                        # Obtedo 100 recomendações para cada usuário do DataFrame
                        print('Getting n = 100 predictions for each user')
                        predictions = als.get_test_predictions()
                        predictions_user_map = als.predictions_user_map(predictions=predictions)

                        print("Calibrating...")
                        calibrator = Calibration(self.df, predictions_user_map, self.userColumn, self.itemColumn, self.genre_map, train, test, lamb)
                        prediction_user_map_after_calibration = calibrator.calibrate_for_all_users(fairness_measure)

                        # TODO: Calcular MACE, MRMC, MAP, MRR
                        mace.append(...)
                        mrmc.append(...)
                        mapMeasure.append(...)
                        mrr.append(...)              
                        i+=1

                    mace_mean = sum(mace)/len(mace)
                    mace_desvpad = stdev(mace)
                    mrmc_mean = sum(mrmc)/len(mrmc)
                    mrmc_desvpad = stdev(mrmc)
                    map_mean = sum(mapMeasure)/len(mapMeasure)
                    map_mean = stdev(mapMeasure)
                    mrr_mean = sum(mrr)/len(mrr)
                    mrr_desvpad = stdev(mrr)

                    new_row = {'FairnessMeasure': fairness_measure,
                               'Lamba': lamb,
                               'MACE': [mace_mean, mace_desvpad],
                               'MRMC': [mrmc_mean, mrmc_desvpad],
                               'MAP': [map_mean, mace_desvpad],
                               'MRR': [mrr_mean, mrr_desvpad]
                               }
                    
                    results = results.append(new_row)
                    results = results.reset_index(drop=True)
        return results









