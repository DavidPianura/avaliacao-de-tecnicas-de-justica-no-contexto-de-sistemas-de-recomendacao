import pandas as pd
import numpy as np
from typing import Literal
from .distributions import Distributions
from .evaluator import FairnessMeasures


class Calibration():
    def __init__(self,
                 utilityMatrix: pd.DataFrame, 
                 prediction_user_map: dict,
                 userColumn: str, 
                 itemColumn: str, 
                 genres_map: dict,
                 train: pd.DataFrame,
                 test: pd.DataFrame,
                 tradeoff: float
                 ):
        
        self.distributions = Distributions(train, 
                                      prediction_user_map=prediction_user_map,
                                      userColumn=userColumn,
                                      itemColumn=itemColumn,
                                      genres_map=genres_map,
                                      )

        self.weights = [i for i in range(0.0, 1.1, 0.1)]
        self.fairness_measures = FairnessMeasures()
        self.evaluator = FairnessMeasures(alpha=0.001)

        self.userColumn = userColumn
        self.itemColumn = itemColumn
        self.genres_map = genres_map

        self.test = test
        self.tradeoff = tradeoff
        self.prediction_user_map = prediction_user_map

    def rerank_recommendation(self, profile_dist, list_recomended_items, user, N, tradeoff, fairness_measure: Literal['kullback-leibler', 'hellinger', 'pearson']):
        re_ranked_list = []
        re_ranked_with_score = []
        
        for _ in range(N):
            
            max_mmr = -np.inf
            max_item = None
            max_item_rating = None
            
            for item, rating in list_recomended_items:
                if item in re_ranked_list:
                    continue
                    
                temporary_list = re_ranked_list + [item]
                temporary_list_with_score = re_ranked_with_score + [(item, rating)]
                    
                weight_part = sum(
                    recomendation[1]
                    for recomendation in temporary_list_with_score
                )
                
                full_tmp_calib = self.evaluator.calculate_fairness_measure(fairness_measure, 
                                                                           user_profile_dist=profile_dist,
                                                                           rec_profile_dist=temporary_list_with_score)
                #full_tmp_calib = calculate_calibration_sum(
                #    profile_dist,
                #    temporary_list_with_score,
                #    user
                #)
                
                maximized = (1 - tradeoff)*weight_part - tradeoff*full_tmp_calib
                
                if maximized > max_mmr:
                    max_mmr = maximized
                    max_item = item
                    max_item_rating = rating
                
            if max_item is not None:
                re_ranked_list.append(max_item)
                re_ranked_with_score.append((max_item, max_item_rating))
                
        return re_ranked_list, re_ranked_with_score  
    

    def calibrate_for_all_users(self, fairness_measure):
        
        prediction_user_map_after_calibration = {}
        for user in self.test[self.userColumn].unique():
            user_profile_distribution = self.distributions.get_user_profile_distribution(user)
            reranked_list = self.rerank_recommendation(user_profile_distribution, 
                                                       self.prediction_user_map[user], 
                                                       user, 
                                                       10, 
                                                       self.tradeoff,
                                                       fairness_measure)
            prediction_user_map_after_calibration[user] = reranked_list  
        
        return prediction_user_map_after_calibration
    ###########################################################################################
        
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

    

        
