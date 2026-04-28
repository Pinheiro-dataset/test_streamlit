import streamlit as st
import geopandas as gpd
import pandas as pd
from streamlit_folium import st_folium

# 1. Configuração inicial da página (Layout "wide" usa a tela toda)
st.set_page_config(page_title="Painel de Inteligência", layout="wide")

# 2. Carregar os dados (com cache para velocidade)
@st.cache_data
def carregar_dados():
    url_geojson = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
    mapa_brasil = gpd.read_file(url_geojson)
    
    df_dados = pd.read_excel('dados-desigualdade-racial-br-02.xlsx', engine='openpyxl')
    df_dados['UF'] = df_dados['UF'].str.strip()
    
    return mapa_brasil, df_dados

mapa_brasil, df_dados = carregar_dados()

# ==========================================
# 3. MENU LATERAL (SIDEBAR)
# ==========================================
st.sidebar.header("Filtros do Boletim")
st.sidebar.write("Utilize os controles abaixo para ajustar a visualização espacial.")

# Pega todos os anos únicos e cria o seletor DENTRO da barra lateral
anos_disponiveis = sorted(df_dados['ano'].unique())
ano_selecionado = st.sidebar.selectbox("Ano de Referência:", anos_disponiveis)

st.sidebar.markdown("---")
st.sidebar.caption("Dados de Monitoramento da Desigualdade")


# ==========================================
# 4. ÁREA PRINCIPAL DO PAINEL
# ==========================================
st.title("Distribuição Espacial: Taxa de Homicídio")
st.markdown("---") # Linha horizontal para separar o título do mapa

# Cruzar os dados baseados no ano selecionado
df_filtrado = df_dados[df_dados['ano'] == ano_selecionado]
mapa_com_dados = mapa_brasil.merge(df_filtrado, left_on='name', right_on='UF', how='left')

# Fixar a escala de cores baseada no histórico total
vmin_historico = df_dados['%_taxa_homicidio_preta'].min()
vmax_historico = df_dados['%_taxa_homicidio_preta'].max()

# Gerar o mapa interativo
mapa_interativo = mapa_com_dados.explore(
    column='%_taxa_homicidio_preta',
    cmap='YlOrRd',
    vmin=vmin_historico,
    vmax=vmax_historico,
    tooltip=['UF', '%_taxa_homicidio_preta', '%_taxa_homicidio_branca'],
    name=f"Taxa em {ano_selecionado}"
)

# Exibir o mapa ocupando a largura total disponível
st_folium(mapa_interativo, width=1200, height=600, returned_objects=[])