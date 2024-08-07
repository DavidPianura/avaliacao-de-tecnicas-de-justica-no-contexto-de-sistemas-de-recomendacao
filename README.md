# Avalicação de técnicas de justiça no contexto de sistemas de recomendação

<center><img src="https://upload.wikimedia.org/wikipedia/commons/e/ee/Ufabc_logo.png" alt="Logo UFABC" width="30%"/></center>

Repositório criado para armazenamento dos códigos utilizados no meu PGC (projeto de graduação em computação) na Universidade Federal do ABC (UFABC) para conclusão do curso de bacharelado em ciência da computação.

****
Conteúdo

1. [Conjuntos de dados utilizados ](#conjuntos-de-dados-utilizados)
2. [Preparação do ambiente](#preparação-do-ambiente)

    * [Instalação das dependêndencias](#instalação-das-dependêndencias)
    * [Instalação e configuração do Spark](#instalação-e-configuração-do-spark)
3. [Conteúdo do repositório](#conteúdo-do-repositório)
****

## Conjuntos de dados utilizados {#conjuntos-de-dados}

Alguns conjuntos de dados necessitam de autorização para download, portanto, não foram disponibilizadas no repositório. Abaixo, cada base é listada juntamente com seu respectivo link para download.

- [Yahoo! Music](https://webscope.sandbox.yahoo.com/catalog.php?datatype=r&guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAAJLf1rtxyCQPeZ6Yavh4M0N7WSnmgsu2GJMnQTPzT9H3Ae9-K3HydONgd-JITMlFWpSo7DY0Z3Mgkb_oHT1YtxqrqzfEw1UlrNo0Vy2oVACCH_BuZb5cMFHJ9aJ5AS-boImtsKf1Bh-yqn1EakW7vTQUsrOSBiNId5YmDsFohcJK)
- [Yahoo! Movies](https://webscope.sandbox.yahoo.com/catalog.php?datatype=r&guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAAJLf1rtxyCQPeZ6Yavh4M0N7WSnmgsu2GJMnQTPzT9H3Ae9-K3HydONgd-JITMlFWpSo7DY0Z3Mgkb_oHT1YtxqrqzfEw1UlrNo0Vy2oVACCH_BuZb5cMFHJ9aJ5AS-boImtsKf1Bh-yqn1EakW7vTQUsrOSBiNId5YmDsFohcJK)
- [Netflix Prize](https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data)
- [Last.fm](https://www.upf.edu/web/mtg/lastfm360k)
- [MovieLens](https://grouplens.org/datasets/movielens/)
- [IMDb](https://datasets.imdbws.com/)

Após o download dos conjuntos listados, extraia-os na pasta data/raw em suas respectivas pastas.

## Preparação do ambiente

<div id = 'preparacao-ambiente'>

<div id='instalacao-dependencias'>

### Instalação das dependêndencias 

Para instalar as dependências necessárias, utilize o comando:

```python
pip install -r requirements.txt
```

<div id='instalacao-spark'>

### Instalação e configuração do Spark

Também faz-se necessário baixar o **Spark** neste [link](https://www.apache.org/dyn/closer.lua/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz). 

Além disso, é necessário criar um arquivo na pasta raiz com o nome de ".env". Esse arquivo deve ter as seguintes variáveis:

```python
SPARK_HOME=...
PYSPARK_DRIVER_PYTHON=python
PYSPARK_PYTHON=...
```

na qual a variável **SPARK_HOME** deve conter o caminho onde o Spark foi extraído, **PYSPARK_DRIVER_PYTHON** contém o valor padrão *python* e **PYSPARK_PYTHON** deve conter o caminho onde a biblioteca pyspark está instalada.

<div id='conteudo-repositorio'>

## Conteúdo do repositório 

- **data**: contém os conjuntos de dados utilizados, tanto processados quanto em sua forma pura. 
- **src**: contém as classes e funcionalidades desenvolvidas para execução dos experimentos. 
- **notebooks**: diretório que armazena os notebooks utilizados para pré-visualização dos códigos. 
- **tests**: testes utilizados para garantir o funcionamento correto das funcionalidades.
