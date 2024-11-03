# Avaliação N2 - Ciência de Dados

## Alunos

- Guilherme Banzati Viana Ribeiro
- Rafael Cerival da Cruz

## Instruções para Rodar a Aplicação

Este projeto é uma aplicação em Python que gera um mapa interativo utilizando dados de candidatos eleitos, armazenados em arquivos CSV. É possivel rodá-lo em seu ambiente local (como um arquivo .py) ou em um ambiente de desenvolvimento interativo, como Google Colab ou Visual Studio Code com Jupyter Notebook.

Para rodar esta aplicação, primeiro instale as bibliotecas necessárias: `pandas`, `folium`, `random` e `unicodedata`, usando `pip install`. A aplicação utiliza arquivos CSV contendo dados de candidatos e informações de latitude e longitude dos municípios. Esses arquivos devem estar disponíveis no início da execução e no mesmo diretório indicado pelo código.

### Script .py

Para rodar o código como um arquivo .py, siga estes passos:

- 1. Salve o código em um arquivo Python
- 2. Certifique-se de que os arquivos CSV com os dados estejam na pasta correta. Defina os caminhos `consulta_candidato_path` e `lat_long_path` para os diretórios exatos onde os arquivos estão localizados no seu computador.
- 3. Abra o terminal, navegue até o diretório onde o arquivo está salvo e execute o comando: `python aplicacao.py`

O script irá carregar os dados dos arquivos CSV, processá-los e salvar os resultados de acordo com o que foi configurado no código. 

### Script .ipynb

Em um ambiente interativo, como Google Colab ou Visual Studio Code com Jupyter Notebook, cole o código em uma célula e faça o upload dos arquivos CSV no início. No Colab, use `from google.colab import files` e `files.upload()` para carregar os arquivos. No Visual Studio Code, utilize o botão de upload do Jupyter. Depois, ajuste as variáveis de caminho para os nomes dos arquivos carregados e execute o código.
