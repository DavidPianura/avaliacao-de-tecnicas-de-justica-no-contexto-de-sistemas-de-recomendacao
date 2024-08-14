import numpy as np
import pandas as pd

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

            pearson_sum += (((p_term - til_q)^2)/til_q)
        
        return pearson_sum
        

class CalibrationEvaluator:

    """
    Métricas para avaliação de calibração: 
        Mean Average Calibration Error (MACE)
        Mean Rank Miscalibration (MRMC)
    """
    def __init__(self, alpha: float = 0.01) -> None:
        self.alpha = alpha

    

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
    
    def _average_precision(self, recommended_items: list, user: int) -> dict:
        """
        Calcula a precisão média para um usuário.

        recommended_items: Lista de itens recomendados para o usuário.
        relevant_items: Conjunto de itens que são relevantes para o usuário.

        Retorna a precisão média.
        """
        hits = 0
        sum_precisions = 0.0

        for i, item in enumerate(recommended_items):
            if item in self.test[self.test[self.userColumn] == user][self.itemColumn].to_list():
                hits += 1
                precision_at_i = hits / (i + 1)
                sum_precisions += precision_at_i

        # Retorna AP. Se não houver itens relevantes, retorna 0
        if hits == 0:
            return 0.0
        return sum_precisions / len(self.test)

    def mean_average_precision(self):
        """
        Calcula a média da precisão média (MAP) para um conjunto de usuários.

        recommendations: Um dicionário onde a chave é o userId e o valor é a lista de itens recomendados.
        ground_truth: Um dicionário onde a chave é o userId e o valor é o conjunto de itens relevantes.
                        (considerado o conjunto de testes)

        Retorna a MAP.
        """
        ap_sum = 0.0
        num_users = len(self.test)

        for user in self.ground_truth:
            ap_sum += self._average_precision(self.map_recommendations.get(user, []), user)

        # Retorna MAP
        return ap_sum / num_users

class CrossValidation:
    def __init__(self) -> None:
        pass

    def cross_val(self, n_folds: int = 5):
        pass



    