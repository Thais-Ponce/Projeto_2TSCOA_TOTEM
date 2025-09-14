import streamlit as st
import pandas as pd
import plotly.express as px
import requests


PRIMARY = "#1C3D5A"  # azul petróleo
ACCENT  = "#B49047"  # dourado
BG      = "#F1E5D1"  # areia

st.set_page_config(page_title="KPIs Clientes", layout="wide")

st.markdown(f"""
    <style>
        
    /* Títulos e textos principais */
    h1, h2, h3, .stMetricLabel, .st-emotion-cache-10trblm, .st-emotion-cache-1wmy9hl {{
        color: {ACCENT} !important;
    }}
    
    /* Cards de métricas */
    .metric-card {{
        border: 1px solid {ACCENT}; padding: 1rem; border-radius: 14px; background: white;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {PRIMARY} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: white !important;
    }}
    </style>
""", unsafe_allow_html=True)


st.sidebar.image(r"Projeto/TOTEM_LOGO.png", width=200)

st.title("KPIs Clientes")

df_base = pd.read_csv(r"Projeto/Base_cliente.csv", sep=";")
df_cluster = pd.read_csv(r"Projeto/base_clusterizada.csv", sep=";")
perfil = pd.read_csv(r"Projeto/perfil_clusters.csv", sep=";")

for col in ["RECEITA_RECORRENTE", "RESPOSTA_NPS_RELACIONAL"]:
    if col in df_base.columns:
        df_base[col] = pd.to_numeric(df_base[col], errors="coerce").fillna(0)

st.subheader("Visão Geral")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Clientes", f"{df_base['CD_CLIENTE'].nunique():,}".replace(",", "."))
col2.metric("Clusters", df_cluster["cluster"].nunique())
col3.metric("Receita Média (12M)", f"{df_base['RECEITA_RECORRENTE_media'].mean():,.2f}")
col4.metric("Satisfação Média (NPS)", f"{df_base['RESPOSTA_NPS_RELACIONAL'].mean():.2f}")

st.subheader("Distribuição de Clientes por Segmento")
if "SEGMENTO" in df_base.columns:
    df_counts = df_base["SEGMENTO"].value_counts().reset_index()
    df_counts.columns = ["SEGMENTO", "Clientes"] 

    fig_seg = px.bar(
    df_counts,
    x="SEGMENTO",
    y="Clientes",
    color="Clientes", 
    color_continuous_scale=px.colors.sequential.Blues,
    labels={"SEGMENTO": "Segmento", "Clientes": "Número de Clientes"},
    title="Clientes por Segmento"
)
    fig_seg.update_layout(showlegend=False)
    st.plotly_chart(fig_seg, use_container_width=True)

import json


geojson_path = r"Projeto/brazil-states.geojson"

with open(geojson_path, "r", encoding="utf-8") as f:
    br_states = json.load(f)    

uf_map = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins"
}

df_unique = df_base[['CD_CLIENTE', 'UF_AJUSTADA']].drop_duplicates()

total_brasil = len(df_unique[df_unique['UF_AJUSTADA'] != "EX"])
total_exterior = len(df_unique[df_unique['UF_AJUSTADA'] == "EX"])

df_brasil = df_unique[df_unique['UF_AJUSTADA'] != "EX"].copy()
df_brasil["estado"] = df_brasil["UF_AJUSTADA"].map(uf_map)

estado_counts = df_brasil["estado"].value_counts().reset_index()
estado_counts.columns = ["estado", "Clientes"]

total_global = len(df_unique)
total_brasil = len(df_unique[df_unique['UF_AJUSTADA'] != "EX"])

col1, col2 = st.columns(2)
col1.metric("Clientes Brasil", total_brasil)
col2.metric("Clientes Globais", total_exterior)

estado_counts = df_brasil.groupby("estado").size().reset_index(name="Clientes")

fig_map = px.choropleth(
    estado_counts,
    geojson=br_states,
    locations="estado",
    featureidkey="properties.name",
    color="Clientes",
    color_continuous_scale=px.colors.sequential.Blues,
    title="Distribuição de Clientes no Brasil por Estado"
)

fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(showlegend=False)
st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Tendência de Tempo de Relacionamento")
if "Tempo_Relacionamento_media" in df_base.columns:

    df_base["Tempo_Relacionamento_media"] = (
        df_base["Tempo_Relacionamento_media"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )
    df_base["Tempo_Relacionamento_media"] = pd.to_numeric(df_base["Tempo_Relacionamento_media"], errors="coerce").fillna(0)


    df_base["Tempo_Relacionamento_anos"] = df_base["Tempo_Relacionamento_media"] / 365

    fig_tempo = px.histogram(
        df_base,
        x="Tempo_Relacionamento_anos",
        nbins=20,
        title="Distribuição do Tempo de Relacionamento (anos)",
        labels={"Tempo_Relacionamento_anos": "Tempo de Relacionamento (anos)", "count": "Número de Clientes"},
        color_discrete_sequence=[PRIMARY]
    )
    st.plotly_chart(fig_tempo, use_container_width=True)


st.subheader("Top 5 Segmentos por Receita")
if "SEGMENTO" in df_base.columns and "RECEITA_RECORRENTE_media" in df_base.columns:
    df_receita = (
        df_base.groupby("SEGMENTO")["RECEITA_RECORRENTE_media"]
        .sum()
        .reset_index()
        .sort_values(by="RECEITA_RECORRENTE_media", ascending=False)
        .head(5)
    )

    fig_top5 = px.bar(
        df_receita,
        x="SEGMENTO",
        y="RECEITA_RECORRENTE_media",
        title="Top 5 Segmentos por Receita",
        labels={"SEGMENTO": "Segmento", "RECEITA_RECORRENTE_media": "Receita Média"},
        color="RECEITA_RECORRENTE_media",
        color_continuous_scale=["#FFF5CC", "#FFD700", "#B8860B"]  # escala dourada personalizada
    )

    # Exibe valores em cima das barras
    fig_top5.update_traces(texttemplate="%{y:,.2f}", textposition="outside")
    fig_top5.update_layout(showlegend=False)


    st.plotly_chart(fig_top5, use_container_width=True)
