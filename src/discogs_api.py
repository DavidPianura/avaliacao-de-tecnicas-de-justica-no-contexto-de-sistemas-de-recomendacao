from time import sleep
import discogs_client
import json

class DiscogsAPI:
    """
    Classe utilizada para gerenciar as interações necessárias com a API Discogs.
    Atributos:
        token (str): token de autenticação para acesso às requisições.
        df (dict): dicionário com id do artista e nome do artista para que seja realizada a busca pelo seus gêneros.
        save_genres_path (str): caminho para salvar o resultado do processo.
        artists_genres (dict): gêneros já obtidos por algum processo prévio, 
                                         para caso não se queira que a busca parta do 0.
    """

    def __init__(self, token: str, df: dict, save_genres_path: str,previous_genres_path: str = None):
        self.d = discogs_client.Client('ExampleApplication/0.1',user_token=token)
        self.df = df
        self.save_genres_path = save_genres_path
        self.artists_genres = {} if previous_genres_path is None else self._get_previous_obtained_genres(previous_genres_path)

    def _get_artist_genre(self, artist):
        results = self.d.search(artist, type='release')

        if len(results) > 0:
            id = results[0].id
            return self.d.release(id).genres
        else:
            print(f'Artista não encontrado: {artist}')
            return []
    
    def _get_previous_obtained_genres(self, path) -> dict:
        with open(path, encoding='utf-8') as json_file:
            artists_genres = json.load(json_file)
        
        return artists_genres
    
    def _save_obtained_genres(self, artists_genres):
        with open(self.save_genres_path, 'w') as fp:
            json.dump(artists_genres, fp, ensure_ascii=False)
    
    def _get_starting_point(self) -> int:
        if len(self.artists_genres) == 0:
            return 0
        else:
            max_key = list(self.artists_genres.keys())[-1]
            partir_position = 0
            for i, id in enumerate(self.df.keys()):
                if id == max_key:
                    partir_position = i     
                    break
            return partir_position
        
    def get_artists_genres(self):
        partir_position = self._get_starting_point()

        lista_artistas = list(self.df.items())[partir_position:]
        artists_dict = dict(lista_artistas)

        for id, artist in artists_dict.items():
            print(len(self.artists_genres))
            genre = self._get_artist_genre(artist)
            print(f'{artist}: {genre}')
            self.artists_genres[id] = (artist, genre)
            sleep(1)
            self._save_obtained_genres()
        
    