import pandas as pd
import numpy as np
from .distributions import Distributions
from .evaluator import FairnessMeasures

class Calibration():
    def __init__(self,
                 utilityMatrix: pd.DataFrame, 
                 prediction_user_map: dict,
                 userColumn: str, 
                 itemColumn: str, 
                 genres_map: dict):
        
        self.distributions = Distributions(utilityMatrix, 
                                      prediction_user_map=prediction_user_map,
                                      userColumn=userColumn,
                                      itemColumn=itemColumn,
                                      genres_map=genres_map)

        self.weights = [i for i in range(0.0, 1.1, 0.1)]
        self.fairness_measures = FairnessMeasures()
    
    def calculate_calibration_sum(self, profile_dist, temporary_list_with_score, user, alpha=0.001):
        kl_div = 0.0

        reco_distr = self.distributions.get_user_recommendation_distribution(temporary_list_with_score)
        for genre, p in profile_dist.items():
            q = reco_distr.get(genre, 0.0)
            til_q = (1 - alpha) * q + alpha * p

            if p == 0.0 or til_q == 0.0:
                kl_div = kl_div
            else:
                kl_div = kl_div + (p * np.log2(p / til_q))
        return kl_div


        
    def mean_rank_miscalibration(self, fairness_measure:str, predictions: dict):
        """
        Uma das métricas que vamos usar para medir o quão injusto é o sistema é o Mean Rank Miscalibration

        Precisamos definir as distribuições p e q, em que:
            * p: distribuição de gêneros do perfil do usuário
            * q: distribuição de gêneros das recomendações geradas para o usuário. 
        
        A função F é usada para calcular a divergência entre as distribuições de gêneros, i.e., F representa
        uma medida de justiça: Kullback-Leibler, Hellinger ou Pearson chi-square
        
        A função RMC percorre os itens do usuário e calcula a descalibração para cada fração da lista de recomendação.
        
        A medida MRMC varia no intervalo [0, 1], em que 1 significa um sistema completamente injusto, e 0 
        significa um sistema completamente justo.
        """
        
        MRMC = 0
        fairness_measures = {'kullback-leibler': self._kullback_leibler, 
                             'hellinger': self._kullback_leibler, 
                             'pearson-chi-square': self._pearson_chi_square}
        

        user_rank_miscalibration = fairness_measures.get(fairness_measure)
        
        for user in predictions:
            RMC = 0
            user_profile_dist = get_user_profile_distribution(train, user)
            if user_profile_dist == {}:
                continue
            
            void = user_rank_miscalibration(user_profile_dist, {})
            N = len(predictions[user])
            for i in range(1, N):
                user_rec_dist = get_user_recommendation_distribution(predictions[user][:i])
                kl = user_rank_miscalibration(user_profile_dist, user_rec_dist)
                RMC += kl/void

            MRMC += RMC/N
            
        return MRMC/len(predictions)

    

        
