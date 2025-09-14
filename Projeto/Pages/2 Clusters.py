import streamlit as st
import plotly.express as px
import pandas as pd

PRIMARY = "#1C3D5A"  # azul petróleo
ACCENT  = "#B49047"  # dourado
BG      = "#F1E5D1"  # areia

st.set_page_config(page_title="Visualização de Clusters", layout="wide")

st.markdown(f"""
    <style>
    h1, h2, h3, .stMetricLabel {{
        color: {ACCENT} !important;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {PRIMARY} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: white !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.sidebar.image(r"C:\Users\thais\OneDrive\Documentos\Faculdade\2º Ano\Challenge\Projeto\TOTEM_LOGO.png", width=200)

df = pd.read_csv(r"C:\Users\thais\OneDrive\Documentos\Faculdade\2º Ano\Challenge\Projeto\base_clusterizada.csv", sep=";")

rename_dict = {
    "CD_CLIENTE": "Cliente",
    "cluster": "Cluster",
    "Tempo_Relacionamento_media": "Tempo de Relacionamento (dias)",
    "RECEITA_RECORRENTE_media": "Receita Recorrente Anual (12M)",
    "RESPOSTA_NPS_RELACIONAL": "Satisfação Média dos Clientes (NPS)",
    "SEGMENTO": "Segmento",
    "REGIAO": "Região"
}

df.rename(columns=rename_dict, inplace=True)

for col in ["Receita Recorrente Anual (12M)", "Satisfação Média dos Clientes (NPS)", "Tempo de Relacionamento (dias)"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

cluster_sel = st.selectbox("Selecione um Cluster", sorted(df["Cluster"].unique()))
df_sel = df[df["Cluster"] == cluster_sel]

st.subheader(f"Resumo do Cluster {cluster_sel}")
col1, col2, col3 = st.columns(3)
col1.metric("Qtd. Clientes", f"{df_sel['Cliente'].nunique():,}".replace(",", "."))
col2.metric("Receita Recorrente Anual (12M)", f"{df_sel['Receita Recorrente Anual (12M)'].mean():,.2f}")
col3.metric("Satisfação Média dos Clientes (NPS)", f"{df_sel['Satisfação Média dos Clientes (NPS)'].mean():.2f}")

st.subheader(f"Distribuição do Cluster {cluster_sel}")

st.subheader(f"Distribuição de Clientes por Segmento - Cluster {cluster_sel}")
if "Segmento" in df_sel.columns:
    df_seg = df_sel["Segmento"].value_counts().reset_index()
    df_seg.columns = ["Segmento", "count"]

    fig_seg = px.bar(
        df_seg,
        x="Segmento",
        y="count",
        title="Clientes por Segmento",
        labels={"Segmento": "Segmento", "count": "Quantidade de Clientes"},
        color="count",
        color_continuous_scale=px.colors.sequential.Blues
    )
    st.plotly_chart(fig_seg, use_container_width=True)

st.subheader(f"Distribuição de Clientes por Região - Cluster {cluster_sel}")
if "Região" in df_sel.columns:
    df_reg = df_sel["Região"].value_counts().reset_index()
    df_reg.columns = ["Região", "count"]

    fig_reg = px.bar(
        df_reg,
        x="Região",
        y="count",
        title="Clientes por Região",
        labels={"Região": "Região", "count": "Quantidade de Clientes"},
        color="count",
        color_continuous_scale=px.colors.sequential.Teal
    )
    st.plotly_chart(fig_reg, use_container_width=True)

    st.subheader(f"Mapa de Calor: Segmentos x Regiões - Cluster {cluster_sel}")
if "Segmento" in df_sel.columns and "Região" in df_sel.columns:
    df_heat = df_sel.groupby(["Segmento", "Região"]).size().reset_index(name="count")
    fig_heat = px.density_heatmap(
        df_heat,
        x="Região",
        y="Segmento",
        z="count",
        color_continuous_scale=px.colors.sequential.Blues,  # degrade azul
        title=f"Distribuição Segmento x Região - Cluster {cluster_sel}"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

st.subheader("Distribuição de Clientes por Cluster")
fig_pie = px.pie(
    df,
    names="Cluster",
    title="Proporção de Clientes por Cluster",
    color="Cluster",
    color_discrete_sequence=[
        "#FAF3E0",  # bege claro
        "#F5DEB3",  # trigo/dourado suave
        "#FFD700",  # dourado clássico
        "#DAA520",  # dourado mais escuro
        "#8B7500"   # dourado intenso
    ]
)
st.plotly_chart(fig_pie, use_container_width=True)

metricas_cluster = df.groupby("Cluster").agg({
    "Receita Recorrente Anual (12M)": "mean",
    "Satisfação Média dos Clientes (NPS)": "mean",
    "Tempo de Relacionamento (dias)": "mean"
}).reset_index()

st.title("Métricas por Cluster")

# Receita
fig1 = px.bar(metricas_cluster, x="Cluster", y="Receita Recorrente Anual (12M)", color="Cluster",
              text="Receita Recorrente Anual (12M)", title="Receita Recorrente Anual (12M) por Cluster")
fig1.update_traces(texttemplate='%{text:.2f}', textposition='outside')
st.plotly_chart(fig1, use_container_width=True)

# NPS
fig2 = px.bar(metricas_cluster, x="Cluster", y="Satisfação Média dos Clientes (NPS)", color="Cluster",
              text="Satisfação Média dos Clientes (NPS)", title="Satisfação Média dos Clientes (NPS) por Cluster")
fig2.update_traces(texttemplate='%{text:.2f}', textposition='outside')
st.plotly_chart(fig2, use_container_width=True)

# Tempo de Relacionamento
fig3 = px.bar(metricas_cluster, x="Cluster", y="Tempo de Relacionamento (dias)", color="Cluster",
              text="Tempo de Relacionamento (dias)", title="Tempo Médio de Relacionamento (dias) por Cluster")
fig3.update_traces(texttemplate='%{text:.0f}', textposition='outside')
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Ticket Médio por Cluster")
df_ticket = df.groupby("Cluster").agg({"Receita Recorrente Anual (12M)": "mean"}).reset_index()
fig_ticket = px.bar(df_ticket, x="Cluster", y="Receita Recorrente Anual (12M)", color="Cluster",
                    text="Receita Recorrente Anual (12M)", title="Ticket Médio Anual por Cluster")
fig_ticket.update_traces(texttemplate='%{text:.2f}', textposition='outside')
st.plotly_chart(fig_ticket, use_container_width=True)