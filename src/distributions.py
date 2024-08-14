import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import warnings

warnings.filterwarnings("ignore")

class Distributions:
    """
    Classe utilizada para lidar com as distribuições, seja do perfil do usuário, ou das recomendações

    Atributos:
        matrix (pd.Dataframe): Dataframe que representa a matriz de utilidade ou a matriz de predições
        userId (int): ID do usuário que tera seu perfil analisado
        userColumn (str): Coluna que contém os ids dos usuários
        itemColumn (str): Coluna que contém os ids dos itens
        genres_dataframe (pd.Dataframe): Dataframe que contém os metadados dos itens
        genresItemColumn (str): Coluna do Dataframe de metadados de itens que contém o generos id itens
        genresColumn (str): Coluna do Dataframe de metadados de itens que contém o generos dos itens
        genres_map (dict): Mapemamento da forma item: [generos], caso esse mapemento já tenha sido feito anteriormente
    """
    def __init__(self, 
                 matrix: pd.DataFrame,
                 userColumn: str, 
                 itemColumn: str, 
                 genres_map: dict):

        # Matriz
        self.df = matrix
        self.itemColumn = itemColumn
        self.userColumn = userColumn
        self.genres_map = genres_map
        
    
    def get_user_profile_distribution(self, userId: int) -> dict:
    
        # O perfil do usuário inicia como um dicionário vazio
        user_profile_distribution = {}
        # Contador para cálculo de probabilidade
        n = 0
        
        # Percorre os itens avaliados pelo usuário
        for item in self.df[self.df[self.userColumn] == userId][self.itemColumn].to_list():
            # Busca a informação do gênero no dicionário de item: generos
            if self.genres_map.get(item, 0) == 0:
                continue 
            for genre in self.genres_map[item]:
                # se o gênero não estiver no perfil do usuário, inicia ele com 0 para iniciar a contagem nas linhas abaixo
                if genre not in user_profile_distribution:
                    user_profile_distribution[genre] = 0
                # soma 1 unidade ao contador    
                n += 1
                # soma uma unidade à contagem do genero (inicialmente iniciada com 0)
                user_profile_distribution[genre] += 1

        # pega o número da contagem (indicado por v) e divide pelo contador n, para assim fazer a probabilidade. k refere-se ao gênero.
            # então temos, por exemplo -> horror: 0,25
        user_profile_distribution = {k: v/n for k, v in sorted(user_profile_distribution.items(), key=lambda item: item[1])}
        return user_profile_distribution

    def get_user_recommendation_distribution(self, prediction_user_map: dict) -> dict:
        user_rec_distribution = {}

        n = 0
        for (item, score) in prediction_user_map:
            if self.genres_map.get(item, 0) == 0:
                continue 
            for genre in self.genres_map[item]:
                if genre not in user_rec_distribution:
                    user_rec_distribution[genre] = 0
                n += 1
                user_rec_distribution[genre] += 1
                
        user_rec_distribution = {k: v/n for k, v in sorted(user_rec_distribution.items(), key=lambda item: item[1])}
        return user_rec_distribution

    def show_user_profile_distribution_chart(self, user_profile_distribution: dict) -> None:
            plt.figure(figsize=(12, 8))
            sns.barplot(
                x=[i[0] for i in user_profile_distribution.items()],
                y=[i[1]*100 for i in user_profile_distribution.items()], color='gray'
            )
            plt.xticks(rotation=45)
            plt.xlabel("Generos")
            plt.ylabel("Presença do Genero no Perfil (%)")
            plt.grid()
            plt.show()

    def show_userProfileDist_userRecDist(self, prediction_user_map, userId):
        user_rec_distribution = self.get_user_recommendation_distribution(prediction_user_map[userId])
        user_profile_distribution = self.get_user_profile_distribution(userId)

        plt.figure(figsize=(12, 8))

        x_map = {}
        n = 0
        for genre in user_profile_distribution:
            if genre not in x_map:
                x_map[genre] = n
                n += 2
        for genre in user_rec_distribution:
            if genre not in x_map:
                x_map[genre] = n
                n += 2

        plt.bar(
            x=[x_map[i[0]] for i in user_profile_distribution.items()],
            height=[i[1] for i in user_profile_distribution.items()],
            color='blue', label="Perfil", width=0.8, alpha=0.6
        )

        plt.bar(
            x=[x_map[i[0]]+0.8 for i in user_rec_distribution.items()],
            height=[i[1] for i in user_rec_distribution.items()],
            color='gray', label="Recomendações",width=0.8
        )

        plt.xticks(rotation=45)
        plt.xlabel("Generos")
        plt.ylabel("Presença do Genero (%)")
        plt.xticks([x_map[i] for i in x_map], [i for i in x_map])
        plt.grid()
        plt.legend()
        plt.show()