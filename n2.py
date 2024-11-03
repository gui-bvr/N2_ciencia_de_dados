# -*- coding: utf-8 -*-
"""N2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ibGshGcbSXw7-Dp1G-Z8vFbWFL44ZE9R

# **N2 - Exercício Eleições 2024**
"""

import pandas as pd
import os
from google.colab import files

# Função para carregar arquivos CSV enviados diretamente
def load_csv_files_via_upload():
    uploaded = files.upload()  # Essa linha abre a interface para upload de arquivos no Colab
    dataframes = []

    for file_name in uploaded.keys():
        # Tentar abrir com a codificação correta e delimitador adequado (ponto e vírgula)
        try:
            df = pd.read_csv(file_name, sep=';', encoding='ISO-8859-1')  # Delimitador ajustado para ponto e vírgula
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, sep=';', encoding='utf-8')  # Se falhar, tenta com UTF-8

        dataframes.append(df)

    # Concatenar todos os DataFrames em um só
    return pd.concat(dataframes, ignore_index=True)

# Recarregar os dados com a função de upload
bem_candidato_df = load_csv_files_via_upload()
consulta_candidato_df = load_csv_files_via_upload()

# Função específica para carregar CSVs e ignorar linhas malformadas
def load_csv_files_with_ignored_errors():
    uploaded = files.upload()  # Abre a interface para upload de arquivos no Colab
    dataframes = []

    for file_name in uploaded.keys():
        try:
            # Ignorar linhas malformadas usando 'on_bad_lines' ao invés de 'error_bad_lines'
            df = pd.read_csv(file_name, sep='\t', on_bad_lines='skip', engine='python')
            dataframes.append(df)
        except Exception as e:
            print(f"Erro ao ler o arquivo {file_name}: {e}")

    # Verificar se a lista não está vazia antes de concatenar
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        raise ValueError("Nenhum arquivo CSV válido foi encontrado.")

# Função para extrair a rede social do URL
def extract_social_network(url):
    if 'instagram' in url.lower():
        return 'Instagram'
    elif 'facebook' in url.lower():
        return 'Facebook'
    elif 'twitter' in url.lower():
        return 'Twitter'
    elif 'linkedin' in url.lower():
        return 'LinkedIn'
    elif 'youtube' in url.lower():
        return 'YouTube'
    else:
        return 'Other'

# Carregar dados da rede social e aplicar função de extração
try:
    rede_social_df = load_csv_files_with_ignored_errors()

    # Aplicar a função de extração de rede social para a coluna DS_URL
    rede_social_df['Rede_Social'] = rede_social_df['DS_URL'].apply(extract_social_network)

    # Verificar o carregamento com a coluna extraída
    print(rede_social_df[['DS_URL', 'Rede_Social']].head())
except ValueError as e:
    print(f"Erro ao carregar os dados de rede social: {e}")

"""## 1. O candidato eleito para prefeito (2024) é o que declarou maior quantidade de bens (influência do poder econômico nas eleições)"""

# 1. Fazer o merge dos dados de candidatos com os dados de bens
merged_df = pd.merge(consulta_candidato_df, bem_candidato_df, on='SQ_CANDIDATO', how='left')

# 2. Filtrar apenas os candidatos eleitos para prefeito
# Remove espaços em branco antes e depois do texto na coluna DS_SIT_TOT_TURNO
merged_df['DS_SIT_TOT_TURNO'] = merged_df['DS_SIT_TOT_TURNO'].str.strip()

# Filtrar apenas candidatos eleitos para PREFEITO com as situações corretas
situacoes_validas = ['ELEITO', 'ELEITO POR QP', 'ELEITO POR MÉDIA']
eleitos_prefeito = merged_df[
    (merged_df['DS_SIT_TOT_TURNO'].isin(situacoes_validas)) &
    (merged_df['DS_CARGO'] == 'PREFEITO')
]

# 3. Renomear a coluna NM_UE_x para evitar conflitos
eleitos_prefeito = eleitos_prefeito.copy()  # Fazendo uma cópia para evitar o aviso SettingWithCopyWarning
eleitos_prefeito.rename(columns={'NM_UE_x': 'NM_UE'}, inplace=True)

# 4. Converter a coluna 'VR_BEM_CANDIDATO' para numérico, substituindo vírgulas por pontos
eleitos_prefeito['VR_BEM_CANDIDATO'] = pd.to_numeric(eleitos_prefeito['VR_BEM_CANDIDATO'].str.replace(',', '.'), errors='coerce')

# 5. Somar os valores de bens por candidato
bens_por_candidato = eleitos_prefeito.groupby(['SQ_CANDIDATO', 'NM_UE'], as_index=False)['VR_BEM_CANDIDATO'].sum()

# 6. Encontrar o prefeito eleito de cada município
prefeitos = eleitos_prefeito[['SQ_CANDIDATO', 'NM_UE']].drop_duplicates()

# 7. Juntar os dados dos bens com os prefeitos
bens_prefeitos = pd.merge(prefeitos, bens_por_candidato, on='SQ_CANDIDATO', how='left')

# Renomear as colunas para que NM_UE seja a mesma
bens_prefeitos.rename(columns={'NM_UE_x': 'NM_UE', 'NM_UE_y': 'NM_UE'}, inplace=True)

# Remover a coluna NM_UE_y, pois já foi renomeada para NM_UE
bens_prefeitos = bens_prefeitos.loc[:, ~bens_prefeitos.columns.duplicated()]

# 8. Encontrar o maior valor de bens por município
maior_bens_por_municipio = bens_por_candidato.loc[bens_por_candidato.groupby('NM_UE')['VR_BEM_CANDIDATO'].idxmax()]

# 9. Verificar se o prefeito eleito é o que declarou mais bens
resultado = pd.merge(maior_bens_por_municipio, bens_prefeitos, on='NM_UE', suffixes=('_maior_bem', '_prefeito'))

# 10. Comparar os candidatos
resultado['prefeito_maior_bem'] = resultado['SQ_CANDIDATO_maior_bem'] == resultado['SQ_CANDIDATO_prefeito']

# 11. Contar os resultados como SIM ou NÃO
resultado_final = resultado['prefeito_maior_bem'].value_counts().rename({True: 'SIM', False: 'NÃO'})

# 12. Exibir os resultados
print(resultado_final)

"""## 2. As maiores coligações (em número de partidos) foram as que mais ganharam disputas?"""

import pandas as pd
import os

# Função para carregar todos os arquivos CSV de uma pasta local
def load_csvs_from_folder(folder_path):
    df_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            try:
                # Tente ler o arquivo com o delimitador correto (pode ser necessário ajustar)
                df = pd.read_csv(file_path, encoding='latin1', sep=';', on_bad_lines='skip')
                df_list.append(df)
            except Exception as e:
                print(f"Erro ao ler o arquivo {filename}: {e}")
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    else:
        raise ValueError("Nenhum arquivo CSV válido foi encontrado.")

# Definir o caminho local para a pasta onde os arquivos CSV estão
consulta_candidato_path = '/caminho/para/a/sua/pasta/local/consulta_cand_2024'

# Carregar os dados de candidatos
consulta_candidato_df = load_csvs_from_folder(consulta_candidato_path)

# Filtrar apenas as situações de "ELEITO", "ELEITO POR QP", e "ELEITO POR MÉDIA"
situacoes_validas = ['ELEITO', 'ELEITO POR QP', 'ELEITO POR MÉDIA']
vencedores = consulta_candidato_df[consulta_candidato_df['DS_SIT_TOT_TURNO'].isin(situacoes_validas)]

# Calcular o número de partidos em cada coligação
vencedores['NUM_PARTIDOS'] = vencedores['DS_COMPOSICAO_COLIGACAO'].apply(lambda x: len(x.split(' / ')))

# Agrupar os vencedores por coligação e contar o número distinto de candidatos vencedores
resultado_coligacoes = vencedores.groupby('DS_COMPOSICAO_COLIGACAO').agg(
    GANHOS=('SQ_CANDIDATO', 'nunique'),       # Contar o número distinto de candidatos eleitos
    NUM_PARTIDOS=('NUM_PARTIDOS', 'first')    # Pegar o número de partidos da primeira ocorrência
).reset_index()

# Obter as top 5 coligações por número de candidatos eleitos
top_coligacoes_ganhos = resultado_coligacoes.sort_values(by='GANHOS', ascending=False).head(5)

# Obter as top 5 coligações por número de partidos
top_coligacoes_partidos = resultado_coligacoes.sort_values(by='NUM_PARTIDOS', ascending=False).head(5)

# Exibir os resultados
print("\nTop 5 coligações por número de candidatos eleitos (Coligação, Partidos, Eleitos):")
for _, row in top_coligacoes_ganhos.iterrows():
    print(f"{row['DS_COMPOSICAO_COLIGACAO']} ({row['NUM_PARTIDOS']} partidos): {row['GANHOS']} eleitos")

print("\nTop 5 coligações por número de partidos (Coligação, Partidos, Eleitos):")
for _, row in top_coligacoes_partidos.iterrows():
    print(f"{row['DS_COMPOSICAO_COLIGACAO']} ({row['NUM_PARTIDOS']} partidos): {row['GANHOS']} eleitos")

"""## 3. Qual partido tem a maior quantidade de candidatos por UF?"""

# Agrupar os dados por SG_UF e SG_PARTIDO, contando o número de candidatos
candidatos_por_partido = consulta_candidato_df.groupby(['SG_UF', 'SG_PARTIDO'])['SQ_CANDIDATO'].count().reset_index()

# Renomear a coluna de contagem para um nome mais descritivo
candidatos_por_partido.rename(columns={'SQ_CANDIDATO': 'Quantidade_Candidatos'}, inplace=True)

# Encontrar o partido com o maior número de candidatos em cada UF
partido_maior_candidato_por_uf = candidatos_por_partido.loc[candidatos_por_partido.groupby('SG_UF')['Quantidade_Candidatos'].idxmax()]

# Exibir os resultados
print(partido_maior_candidato_por_uf)

"""## 4. Existe uma tendência regional para maior número de candidaturas por partido?"""

# Contar o número de candidatos por partido e por UF
candidaturas_por_partido_uf = consulta_candidato_df.groupby(['SG_UF', 'SG_PARTIDO']).agg(candidatos=('SQ_CANDIDATO', 'count')).reset_index()

# Criar um dicionário para armazenar as informações de tendência por UF
tendencia = {}

# Defina um limite para identificar a tendência, ajuste conforme necessário
threshold = 10

# Verificar a tendência em cada estado
for uf in candidaturas_por_partido_uf['SG_UF'].unique():
    partidos = candidaturas_por_partido_uf[candidaturas_por_partido_uf['SG_UF'] == uf]

    # Filtra os partidos com tendência
    partidos_tendencia = partidos[partidos['candidatos'] >= threshold]

    # Verifica se há partidos com tendência
    if not partidos_tendencia.empty:
        partidos_lista = ', '.join(partidos_tendencia['SG_PARTIDO'])
        tendencia[uf] = f"Existe tendência: {partidos_lista}"
    else:
        tendencia[uf] = "Não existe tendência"

# Converter o dicionário para DataFrame
tendencia_df = pd.DataFrame(list(tendencia.items()), columns=['SG_UF', 'Tendência'])

# Exibir o resultado final
print(tendencia_df)

"""## 5. Qual o maior partido por UF em termos de candidatos (Prefeito+Vice+Vereadores)"""

# Contar o número de candidatos distintos por partido e por UF
candidaturas_por_partido_uf = consulta_candidato_df.groupby(['SG_UF', 'SG_PARTIDO']).agg(candidatos=('SQ_CANDIDATO', 'nunique')).reset_index()

# Encontrar o maior partido por UF
maior_partido_por_uf = candidaturas_por_partido_uf.loc[candidaturas_por_partido_uf.groupby('SG_UF')['candidatos'].idxmax()]

# Renomear a coluna para deixar claro
maior_partido_por_uf = maior_partido_por_uf.rename(columns={'candidatos': 'Número de Candidatos'})

# Exibir o resultado final
print(maior_partido_por_uf[['SG_UF', 'SG_PARTIDO', 'Número de Candidatos']])

"""## 6. Qual a região que mais registrou candidatos Indígenas e Quilombolas?"""

# Defina as categorias de interesse
categorias_interesse = ['INDÍGENA', 'QUILOMBOLA']

# Filtrar os dados para incluir apenas candidatos Indígenas e Quilombolas
candidatos_especial = consulta_candidato_df[consulta_candidato_df['DS_COR_RACA'].isin(categorias_interesse)]

# Verificar se o DataFrame está vazio após a filtragem
if candidatos_especial.empty:
    print("Não há candidatos Indígenas ou Quilombolas registrados.")
else:
    # Mapear as unidades da federação (UF) para suas respectivas regiões
    regioes = {
        'AC': 'Norte', 'AL': 'Nordeste', 'AP': 'Norte', 'AM': 'Norte', 'BA': 'Nordeste',
        'CE': 'Nordeste', 'DF': 'Centro-Oeste', 'ES': 'Sudeste', 'GO': 'Centro-Oeste',
        'MA': 'Nordeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MG': 'Sudeste',
        'PA': 'Norte', 'PB': 'Nordeste', 'PR': 'Sul', 'PE': 'Nordeste', 'PI': 'Nordeste',
        'RJ': 'Sudeste', 'RN': 'Nordeste', 'RS': 'Sul', 'RO': 'Norte', 'RR': 'Norte',
        'SC': 'Sul', 'SP': 'Sudeste', 'SE': 'Nordeste', 'TO': 'Norte'
    }

    # Adicionar a coluna de região ao DataFrame
    candidatos_especial['Região'] = candidatos_especial['SG_UF'].map(regioes)

    # Contar o número de candidatos por região
    candidatos_por_regiao = candidatos_especial['Região'].value_counts().reset_index()
    candidatos_por_regiao.columns = ['Região', 'Número de Candidatos']

    # Identificar a região com o maior número de candidatos
    regiao_maxima = candidatos_por_regiao.loc[candidatos_por_regiao['Número de Candidatos'].idxmax()]

    # Exibir o resultado
    print(f"A região que mais registrou candidatos Indígenas e Quilombolas é: {regiao_maxima['Região']} com {regiao_maxima['Número de Candidatos']} candidatos.")

"""## 7. Qual a rede social preferida dos candidatos? Separe por partido e por UF."""

import pandas as pd
import os

# Função para carregar todos os arquivos CSV de uma pasta local
def load_csvs_from_folder(folder_path):
    df_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            try:
                # Ler o arquivo com o delimitador correto (ponto e vírgula)
                df = pd.read_csv(file_path, encoding='latin1', sep=';', on_bad_lines='skip')
                df_list.append(df)
            except Exception as e:
                print(f"Erro ao ler o arquivo {filename}: {e}")
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    else:
        raise ValueError("Nenhum arquivo CSV válido foi encontrado.")

# Defina o caminho local onde estão os arquivos CSV
consulta_candidato_path = 'caminho/para/sua/pasta/consulta_cand_2024'  # Altere para o caminho local

# Carregar os dados de candidatos
consulta_candidato_df = load_csvs_from_folder(consulta_candidato_path)

# Filtrar apenas as situações de "ELEITO", "ELEITO POR QP", e "ELEITO POR MÉDIA"
situacoes_validas = ['ELEITO', 'ELEITO POR QP', 'ELEITO POR MÉDIA']
vencedores = consulta_candidato_df[consulta_candidato_df['DS_SIT_TOT_TURNO'].isin(situacoes_validas)]

# Calcular o número de partidos em cada coligação
vencedores['NUM_PARTIDOS'] = vencedores['DS_COMPOSICAO_COLIGACAO'].apply(lambda x: len(x.split(' / ')))

# Agrupar os vencedores por coligação e contar o número distinto de candidatos vencedores
resultado_coligacoes = vencedores.groupby('DS_COMPOSICAO_COLIGACAO').agg(
    GANHOS=('SQ_CANDIDATO', 'nunique'),       # Contar o número distinto de candidatos eleitos
    NUM_PARTIDOS=('NUM_PARTIDOS', 'first')    # Pegar o número de partidos da primeira ocorrência
).reset_index()

# Obter as top 5 coligações por número de candidatos eleitos
top_coligacoes_ganhos = resultado_coligacoes.sort_values(by='GANHOS', ascending=False).head(5)

# Obter as top 5 coligações por número de partidos
top_coligacoes_partidos = resultado_coligacoes.sort_values(by='NUM_PARTIDOS', ascending=False).head(5)

# Exibir os resultados
print("\nTop 5 coligações por número de candidatos eleitos (Coligação, Partidos, Eleitos):")
for _, row in top_coligacoes_ganhos.iterrows():
    print(f"{row['DS_COMPOSICAO_COLIGACAO']} ({row['NUM_PARTIDOS']} partidos): {row['GANHOS']} eleitos")

print("\nTop 5 coligações por número de partidos (Coligação, Partidos, Eleitos):")
for _, row in top_coligacoes_partidos.iterrows():
    print(f"{row['DS_COMPOSICAO_COLIGACAO']} ({row['NUM_PARTIDOS']} partidos): {row['GANHOS']} eleitos")

"""## 8. Utilize técnicas de NLP para determinar quais os principais termos (propostas) presentes nos planos de governo de cada UF."""

import os
import PyPDF2
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import re

# Defina o caminho local para os arquivos PDF
proposta_candidato_path = 'caminho/para/sua/pasta/propostas_governo_2024/SC'  # Altere para o caminho local

def extrair_texto_pdf(caminho_pdf):
    texto = ''
    with open(caminho_pdf, 'rb') as arquivo:
        leitor_pdf = PyPDF2.PdfReader(arquivo)
        for pagina in leitor_pdf.pages:
            texto += pagina.extract_text()
    return texto

def limpar_texto(texto):
    # Remover caracteres especiais e colocar tudo em maiúsculas
    texto = re.sub(r'[^a-zA-Z0-9\s]', '', texto)
    return texto.upper()

# Listar todos os arquivos PDF no diretório local
arquivos_pdf = [f for f in os.listdir(proposta_candidato_path) if f.endswith('.pdf')]
todos_textos = []

# Limitar a leitura a 1000 arquivos PDF
limite = 1000
contador = 0

# Extração e limpeza do texto com progresso
total_arquivos = min(len(arquivos_pdf), limite)  # Garantir que o total não exceda o limite
for i, arquivo in enumerate(arquivos_pdf[:limite]):
    caminho_pdf = os.path.join(proposta_candidato_path, arquivo)
    texto = extrair_texto_pdf(caminho_pdf)
    texto_limpo = limpar_texto(texto)
    todos_textos.append(texto_limpo)

    # Calculando e exibindo o progresso
    percentual_lido = ((i + 1) / total_arquivos) * 100
    print(f'\rArquivo {i + 1} de {total_arquivos} lido. Progresso: {percentual_lido:.2f}%', end='')

# Concatenar todos os textos
texto_concatenado = ' '.join(todos_textos)

# Lista aprimorada de stop words
stop_words_aprimorada = [
    'a', 'e', 'o', 'as', 'os', 'da', 'de', 'do', 'em', 'para', 'com', 'que', 'na', 'no',
    'um', 'uma', 'me', 'te', 'se', 'meu', 'minha', 'seu', 'sua', 'nos', 'vos', 'todos',
    'tudo', 'mais', 'muito', 'nada', 'sim', 'nao', 'como', 'que', 'por', 'pela', 'pelo',
    'isso', 'aquilo', 'tal', 'este', 'esta', 'esses', 'essas', 'se', 'só', 'mais', 'mas',
    'nas', 'meio', 'so', 'aos', 'aes', 'ao', 'das', 'sade', 'dos'
]

# Usar CountVectorizer com a lista aprimorada de stop words
vectorizer = CountVectorizer(stop_words=stop_words_aprimorada, max_features=100, lowercase=True)

X = vectorizer.fit_transform([texto_concatenado])
contagem_palavras = X.toarray().sum(axis=0)

# Criar um DataFrame para visualizar os resultados
termos = vectorizer.get_feature_names_out()
resultado = pd.DataFrame({'Termo': termos, 'Frequência': contagem_palavras})
resultado = resultado.sort_values(by='Frequência', ascending=False)

# Exibir os principais termos
print('\nPrincipais termos encontrados:')
print(resultado[['Termo', 'Frequência']].head(20))  # Exibir os 20 termos mais frequentes

"""## 9. Baixe os dados totalizados da eleição de 2024, utilize uma cor para cada partido, e crie um mapa colorido para cada UF do Brasil, pintando o município de acordo com a legenda do partido vencedor no município. Você pode colocar uma “bolinha” ou marcador na cidade com a cor desejada (use a biblioteca folium para isso).

"""

import os
import pandas as pd
import folium
import random
import unicodedata

# Função para corrigir formatação de latitude e longitude
def corrigir_lat_long(value):
    if isinstance(value, str):
        partes = value.split('.')
        if len(partes) > 2:
            value = partes[0] + '.' + partes[1]
        return float(value.replace(',', '.'))
    return value

# Função para carregar CSVs de uma pasta local
def load_csvs_from_folder(folder_path):
    all_files = os.listdir(folder_path)
    dataframes = []
    for file in all_files:
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(folder_path, file), sep=';', encoding='ISO-8859-1')
            dataframes.append(df)
    return pd.concat(dataframes, ignore_index=True)

# Função para normalizar strings, remover acentos e converter para maiúsculas
def normalize_string(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').upper()

# Defina os caminhos locais dos dados
consulta_candidato_path = 'caminho/para/sua/pasta/consulta_cand_2024'  # Substitua pelo caminho local
lat_long_path = 'caminho/para/sua/pasta/Latitude_Longitude_cidades_corrigido.csv'  # Substitua pelo caminho local

# Carregar dados dos candidatos (CSV)
print("Carregando dados dos candidatos...")
consulta_candidato_df = load_csvs_from_folder(consulta_candidato_path)
print(f"Número total de registros em consulta_candidato: {consulta_candidato_df.shape[0]}")

# Carregar dados de latitude e longitude (CSV)
print("Carregando dados de latitude e longitude...")
lat_long_df = pd.read_csv(lat_long_path, sep=';', encoding='ISO-8859-1')
print(f"Número total de registros em latitude e longitude: {lat_long_df.shape[0]}")

# Corrigir nomes dos municípios e normalizar strings
lat_long_df['municipio'] = lat_long_df['municipio'].apply(normalize_string)
consulta_candidato_df['NM_UE'] = consulta_candidato_df['NM_UE'].apply(normalize_string)

# Filtrar apenas prefeitos eleitos
print("Filtrando prefeitos eleitos...")
vencedores = consulta_candidato_df[(consulta_candidato_df['DS_CARGO'] == 'PREFEITO') &
                                   (consulta_candidato_df['DS_SIT_TOT_TURNO'].isin(['ELEITO', 'ELEITO POR QP', 'ELEITO POR MÉDIA']))]
print(f"Número de prefeitos eleitos encontrados: {vencedores.shape[0]}")

# Agrupar para garantir que haja apenas um prefeito por município
vencedores = vencedores.groupby('NM_UE').first().reset_index()
print(f"Número de prefeitos únicos por município: {vencedores.shape[0]}")

# Mesclar dados de latitude e longitude
print("Mesclando dados de latitude e longitude...")
vencedores_lat_long = vencedores.merge(lat_long_df, left_on='NM_UE', right_on='municipio', how='left')
print(f"Número de registros após mesclagem: {vencedores_lat_long.shape[0]}")

# Corrigir colunas de latitude e longitude
print("Corrigindo colunas de latitude e longitude...")
vencedores_lat_long['latitude'] = vencedores_lat_long['latitude'].apply(corrigir_lat_long)
vencedores_lat_long['longitude'] = vencedores_lat_long['longitude'].apply(corrigir_lat_long)

# Verificar e filtrar linhas com latitude e longitude válidas
vencedores_lat_long = vencedores_lat_long[
    (vencedores_lat_long['latitude'].notnull()) &
    (vencedores_lat_long['longitude'].notnull())
]
print(f"Número de registros após verificar latitudes e longitudes válidas: {vencedores_lat_long.shape[0]}")

# Criar um dicionário de cores aleatórias para os partidos
partido_colors = {}
for partido in vencedores_lat_long['SG_PARTIDO'].unique():
    partido_colors[partido] = "#{:06x}".format(random.randint(0, 0xFFFFFF))

# Criar mapa
print("Criando o mapa...")
mapa = folium.Map(location=[-15.7801, -47.9292], zoom_start=4)

# Adicionar marcadores ao mapa
print("Adicionando marcadores ao mapa...")
marker_group = folium.FeatureGroup(name="Marcadores").add_to(mapa)

for _, row in vencedores_lat_long.iterrows():
    if -90 <= row['latitude'] <= 90 and -180 <= row['longitude'] <= 180:
        popup_text = f"{row['NM_URNA_CANDIDATO']} - {row['SG_PARTIDO']} ({row['NR_CANDIDATO']})"
        folium.CircleMarker(
            location=(row['latitude'], row['longitude']),
            radius=5,
            color=partido_colors.get(row['SG_PARTIDO'], '#000000'),
            fill=True,
            fill_color=partido_colors.get(row['SG_PARTIDO'], '#000000'),
            fill_opacity=0.6,
            popup=popup_text
        ).add_to(marker_group)
    else:
        print(f"Coordenadas inválidas: {row['latitude']}, {row['longitude']} para o candidato {row['NM_URNA_CANDIDATO']}")

# Criar legenda HTML para os partidos
print("Adicionando legenda...")
legend_html = f"""
<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid black;">
    <h4>Legenda dos Partidos</h4>
    <ul style="list-style: none; padding: 0;">
        {''.join([f'<li><span style="color:{color};">&#9679;</span> {partido}</li>' for partido, color in partido_colors.items()])}
    </ul>
</div>
"""

# Adicionar legenda no mapa
mapa.get_root().html.add_child(folium.Element(legend_html))

# Salvar o mapa
mapa.save('mapa_prefeitos_eleitos.html')
print("Mapa salvo como 'mapa_prefeitos_eleitos.html'")