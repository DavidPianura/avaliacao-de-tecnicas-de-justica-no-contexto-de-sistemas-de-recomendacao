import numpy as np
import pandas as pd
from typing import Literal
from .distributions import Distributions

class FairnessMeasures:

    def __init__(self, alpha: float = 0.01) -> None:
        self.alpha = alpha
    
    def kullback_leibler(self, user_profile_dist: dict, rec_profile_dist: dict) -> float:
        p_g_u = user_profile_dist
        q_g_u = rec_profile_dist
        
        
        Ckl = 0
        for genre, p in p_g_u.items():
            q = q_g_u.get(genre, 0.0)
            til_q = (1 - self.alpha) * q + self.alpha * p

            if til_q == 0 or p_g_u.get(genre, 0) == 0:
                Ckl = Ckl
            else:
                Ckl += p * np.log2(p / til_q)
        return Ckl
    
    def hellinger(self, user_profile_dist: dict, rec_profile_dist: dict) -> float:
        p_g_u = user_profile_dist
        q_g_u = rec_profile_dist

        hel_sum = 0

        all_genres = set(user_profile_dist.keys()).union(set(rec_profile_dist.keys()))

        for genre in all_genres:
            p = p_g_u.get(genre, 0.0)
            q = q_g_u.get(genre, 0.0)
            p_term = np.sqrt(p)
            q_term = np.sqrt(q)
            hel_sum += (p_term - q_term)**2
        
        hellinger = np.sqrt(2 * hel_sum)
        return hellinger

    def pearson_chi_square(self, user_profile_dist: dict, rec_profile_dist: dict) -> float:
        p_g_u = user_profile_dist
        q_g_u = rec_profile_dist

        all_genres = set(user_profile_dist.keys()).union(set(rec_profile_dist.keys()))

        pearson_sum = 0

        for genre in all_genres:
            p_term = p_g_u.get(genre, 0.0)
            q_term = q_g_u.get(genre, 0.0)
            til_q = (1-self.alpha)*q_term + self.alpha*p_term

            pearson_sum += (((p_term - til_q)**2)/til_q)
        
        return pearson_sum
    
    def calculate_fairness_measure(self, fairness_measure: Literal['kullback-leibler', 'hellinger', 'pearson'], user_profile_dist: dict, rec_profile_dist: dict):
        if fairness_measure == 'kullback-leibler':
            return self.kullback_leibler(user_profile_dist, rec_profile_dist)
        elif fairness_measure == 'hellinger':
            return self.hellinger(user_profile_dist, rec_profile_dist)
        elif fairness_measure == 'pearson':
            return self.pearson_chi_square(user_profile_dist, rec_profile_dist)

class CalibrationEvaluator:

    """
    Métricas para avaliação de calibração: 
        Mean Average Calibration Error (MACE)
        Mean Rank Miscalibration (MRMC)
    """
    def __init__(self, matrix: pd.DataFrame, userColumn: str, itemColumn: str, genres_map: dict) -> None:
        self.fairness_measures = FairnessMeasures()
        self.distributor = Distributions(matrix, userColumn, itemColumn, genres_map)
        self.genres_map = genres_map
        

    # MRMC (Mean Rank Miscalibration)
    def get_mean_rank_miscalibration(self, predictions, fairness_measure: Literal['kullback-leibler', 'hellinger', 'pearson']):
        
        MRMC = 0
        
        for user in predictions:
            RMC = 0

            # Train or test
            user_profile_dist = self.distributor.get_user_profile_distribution(user)
            if user_profile_dist == {}:
                continue
            
            void = self.fairness_measures.calculate_fairness_measure(fairness_measure, user_profile_dist, {})
            N = len(predictions[user])

            for i in range(1, N):
                user_rec_dist = self.distributor.get_user_recommendation_distribution(predictions[user][:i])
                kl = self.fairness_measures.calculate_fairness_measure(fairness_measure, user_profile_dist, user_rec_dist)
                RMC += kl/void

            MRMC += RMC/N
        
        return MRMC/len(predictions)

    # MACE (Mean Average CAlibration Error)
    def get_mean_average_calibration_error(self, predictions):
        MACE = 0

        for user in predictions:
            ACE = 0

            user_profile_dist = self.distributor.get_user_profile_distribution(user)
            if user_profile_dist == {}:
                continue

            N = len(predictions[user])
            for i in range(1, N):
                CE = 0
                user_rec_dist = self.distributor.get_user_recommendation_distribution(predictions[user][:i])
                for g, dist in user_rec_dist.items():
                    absolute_difference = abs(dist - user_rec_dist.get(g, 0))
                    CE += absolute_difference/len(user_profile_dist)

            ACE += CE/N
        
        return ACE/len(predictions)
    

class RSEvaluator:

    """
    Métricas utilizadas para avaliação do sistema de recomendação (SR):
        Mean Reciprocal Rank (MRR)
        Mean Average Precision (MAP)
    
    Atributos:
        map_recommendations (dict): Dicionário das listas de recomendações mapeadas por usuário {user: [recommendations]}
        test_dataframe (pd.Dataframe): Conjunto groundtruth.
        userColumn (str): Coluna que armazena os IDs dos usuários.
        itemColumn (str): Coluna que armazena os itens interagidos pelo usuário. 
    """

    def __init__(self, map_recommendations: dict, test_dataframe: pd.DataFrame, userColumn: str, itemColumn: str) -> None:
        self.test = test_dataframe
        self.map_recommendations = map_recommendations
        self.userColumn = userColumn
        self.itemColumn = itemColumn

    def _item_is_relevant(self, user_id: int, item_id: int):
        aux = self.test[self.test[self.userColumn] == user_id]
        if item_id in list(aux[self.itemColumn]):
            return True
        return False
    
    def mean_reciprocal_rank(self) -> float:
        MRR = 0
        
        for user_id in self.map_recommendations:
            user_find_corerect_item = False
            for index, (item, score) in enumerate(self.map_recommendations[user_id]):
                if user_find_corerect_item is False:
                    if self._item_is_relevant(user_id, item):
                        MRR += (1/(index+1))
                        user_find_corerect_item = True
            
        return MRR/len(self.map_recommendations)
    
    def _average_precision(self, recommended_items: list, user: int) -> float:
        """
        Calcula a precisão média para um usuário.

        recommended_items: Lista de itens recomendados para o usuário.
        user: ID do usuário.

        Retorna a precisão média.
        """
        hits = 0
        sum_precisions = 0.0
        relevant_items = self.test[self.test[self.userColumn] == user][self.itemColumn].to_list()

        for i, item in enumerate(recommended_items):
            if item in relevant_items:
                hits += 1
                precision_at_i = hits / (i + 1)
                sum_precisions += precision_at_i

        # Retorna AP. Se não houver itens relevantes, retorna 0
        if hits == 0:
            return 0.0
        return sum_precisions / len(relevant_items)

    def mean_average_precision(self):
        """
        Calcula a média da precisão média (MAP) para um conjunto de usuários.

        recommendations: Um dicionário onde a chave é o userId e o valor é a lista de itens recomendados.

        Retorna a MAP.
        """
        users = self.test[self.userColumn].drop_duplicates().to_list()
        ap_sum = 0.0
        num_users = len(users)

        for user in users:
            ap_sum += self._average_precision(self.map_recommendations.get(user, []), user)

        # Retorna MAP
        return ap_sum / num_users if num_users > 0 else 0.0
    