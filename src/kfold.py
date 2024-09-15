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
from .evaluator import CalibrationEvaluator, RSEvaluator
import numpy as np
from math import sqrt

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
        self.spark = SparkSession.builder \
                    .appName("KFOLD") \
                    .config("spark.driver.memory", "4g") \
                    .config("spark.executor.memory", "8g") \
                    .getOrCreate()

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

            for lamb in np.arange(0, 1.1, 0.1):
                print("*" * 30)
                print(f'Lambda = {lamb}')


                for fairness_measure in ['kullback-leibler', 'hellinger', 'pearson']:
                    print('Reseting metrics lists')
                    mace = []
                    mrmc = []
                    mapMeasure = []
                    mrr = []
                    
                    print("*" * 20)
                    print(f'FAIRNESS MEASURE: {fairness_measure}')
                    i = 1
                    for train_idx, test_idx in self.kf.split(self.df, y=self.df[self.userColumn]):
                        print("="*5 + f'{i}º Fold' + "="*5)

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
                        predictions = als.get_predictions()
                        predictions_user_map = als.predictions_user_map(predictions=predictions)

                        print("Calibrating...")
                        calibrator = Calibration(self.df, predictions_user_map, self.userColumn, self.itemColumn, self.genre_map, train, test, lamb)
                        prediction_user_map_after_calibration = calibrator.calibrate_for_all_users(fairness_measure)

                        # TODO: Calcular MACE, MRMC, MAP, MRR
                        ############## CALIBRATION EVALUATION ############## 
                        calibration_evaluator = CalibrationEvaluator(test, self.userColumn, self.itemColumn, self.genre_map)
                        
                        print('CALCULATING MRMC')
                        mrmc_calculation = calibration_evaluator.get_mean_rank_miscalibration(prediction_user_map_after_calibration, fairness_measure)
                        mrmc.append(mrmc_calculation)
                        print(f'MRMC = {mrmc_calculation}')

                        print('CALCULATING MACE')
                        mace_calculation = calibration_evaluator.get_mean_average_calibration_error(prediction_user_map_after_calibration)
                        mace.append(mace_calculation)
                        print(f'MACE = {mace_calculation}')

                        ############## PRECISION EVALUATION ##############
                        rs_evaluation = RSEvaluator(prediction_user_map_after_calibration, test, self.userColumn, self.itemColumn)

                        print('CALCULATING MAP')
                        map_calculation = rs_evaluation.mean_average_precision()
                        mapMeasure.append(map_calculation)
                        print(f'MAP = {map_calculation}')

                        print('CALCULATING MRR')
                        mrr_calculation = rs_evaluation.mean_reciprocal_rank()
                        mrr.append(mrr_calculation) 
                        print(f'MRR = {mrr_calculation}')

                        i+=1

                    print("=" * 15)
                    print('Getting mean and stdev')

                    mace_mean = sum(mace)/len(mace)
                    print(f'MACE Mean = {mace_mean}')
                    mace_desvpad = stdev(mace)
                    print(f'MACE Error = {mace_desvpad}')

                    mrmc_mean = sum(mrmc)/len(mrmc)
                    print(f'MRMC Mean = {mrmc_mean}')
                    mrmc_desvpad = stdev(mrmc)
                    print(f'MRMC Error = {mrmc_desvpad}')

                    map_mean = sum(mapMeasure)/len(mapMeasure)
                    print(f'MAP Mean = {map_mean}')
                    map_desvpad = stdev(mapMeasure)
                    print(f'MAP Error = {map_desvpad}')

                    mrr_mean = sum(mrr)/len(mrr)
                    print(f'MRR Mean = {mrr_mean}')
                    mrr_desvpad = stdev(mrr)
                    print(f'MRR Error = {mrr_desvpad}')

                    new_row = {'FairnessMeasure': fairness_measure,
                               'Lambda': lamb,
                               'MACE': {'mean': mace_mean, 'stdev': mace_desvpad/sqrt(len(mace))},
                               'MRMC': {'mean': mrmc_mean, 'stdev':mrmc_desvpad/sqrt(len(mrmc))},
                               'MAP': {'mean': map_mean, 'stdev': map_desvpad/sqrt(len(mapMeasure))},
                               'MRR': {'mean': mrr_mean, 'stdev': mrr_desvpad/sqrt(len(mrr))}
                               }
                    
                    print('Appending to results')
                    new_df_results = pd.DataFrame(new_row)
                    new_df_results.index.name = 'Statistic'
                    new_df_results = new_df_results.reset_index()[['Lambda', 'FairnessMeasure', 'Statistic', 'MACE', 'MRMC', 'MAP', 'MRR']]
                    results = pd.concat([results, new_df_results])
                    
                    print('\n')

        return results









