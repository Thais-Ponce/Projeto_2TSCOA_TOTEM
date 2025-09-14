import streamlit as st
import pandas as pd

PRIMARY = "#1C3D5A"
ACCENT = "#B49047"
BG = "#F1E5D1"

st.set_page_config(page_title="Perfis dos Clusters", layout="wide")

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
    .cluster-card {{
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
    }}
    </style>
""", unsafe_allow_html=True)

st.sidebar.image(
    r"Projeto/TOTEM_LOGO.png",
    width=200
)

st.title("Perfis dos Clusters")

df = pd.read_csv(
    r"Projeto/base_clusterizada.csv",
    sep=";"
)

rename_dict = {
    "CD_CLIENTE": "Cliente",
    "cluster": "Cluster",
    "Tempo_Relacionamento_media": "Tempo de Relacionamento (dias)",
    "RECEITA_RECORRENTE_media": "Receita Recorrente Anual (12M)",
    "RESPOSTA_NPS_RELACIONAL": "Satisfação Média (NPS)"
}
df.rename(columns=rename_dict, inplace=True)

for col in ["Receita Recorrente Anual (12M)", "Satisfação Média (NPS)", "Tempo de Relacionamento (dias)"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df["Receita Recorrente Anual (12M)"] = df["Receita Recorrente Anual (12M)"] / 1_000_000

metricas = df.groupby("Cluster").agg({
    "Cliente": "nunique",
    "Receita Recorrente Anual (12M)": "mean",
    "Satisfação Média (NPS)": "mean",
    "Tempo de Relacionamento (dias)": "mean"
}).reset_index()

if metricas.shape[0] == 0:
    st.warning("Nenhum cluster encontrado na base. Verifique a coluna 'cluster' em base_clusterizada.csv")
    st.stop()

cluster_cliente_ideal = int(metricas.loc[metricas["Receita Recorrente Anual (12M)"].idxmax(), "Cluster"])
cluster_premium = int(metricas.loc[metricas["Tempo de Relacionamento (dias)"].idxmax(), "Cluster"])
cluster_risco = int(metricas.loc[metricas["Satisfação Média (NPS)"].idxmin(), "Cluster"])

todos = set(metricas["Cluster"].astype(int).tolist())
restantes = todos - {cluster_cliente_ideal, cluster_premium, cluster_risco}

restantes_metricas = metricas[metricas["Cluster"].astype(int).isin(restantes)].copy()
restantes_metricas["Cluster"] = restantes_metricas["Cluster"].astype(int)
restantes_sorted = restantes_metricas.sort_values("Receita Recorrente Anual (12M)", ascending=False)["Cluster"].tolist()

cluster_crescimento = None
cluster_estavel = None

if len(restantes_sorted) == 1:
    cluster_estavel = restantes_sorted[0]
elif len(restantes_sorted) >= 2:
    cluster_crescimento = restantes_sorted[0]
    cluster_estavel = restantes_sorted[1]

personas = {}

def safe_add(cluster_id, nome, desc, cor):
    if cluster_id is None:
        return
    personas[int(cluster_id)] = (nome, desc, cor)

safe_add(cluster_cliente_ideal, "💎 Cliente Ideal", ["Alta Receita", "Alta Satisfação", "Baixo Churn"], "#1E90FF")
safe_add(cluster_premium, "🏆 Premium", ["Maior Ticket Médio", "Relacionamento Longo", "Satisfação alta"], "#DAA520")
safe_add(cluster_risco, "⚠️ Em Risco", ["Receita Baixa", "NPS Negativo", "Churn elevado"], "#B22222")
safe_add(cluster_crescimento, "📈 Potencial de Crescimento", ["Receita Média", "Alto Engajamento", "Upsell possível"], "#32CD32")

for cid in sorted(todos):
    if int(cid) not in personas:
        personas[int(cid)] = ("🔄 Estável", ["Receita Consistente", "Satisfação Mediana", "Fidelidade média"], "#708090")

explicacoes = {
    "💎 Cliente Ideal": {
        "quem": "Clientes de maior receita, NPS alto e relacionamento longo.",
        "importancia": "São os que mais geram valor para a TOTVS, além de serem promotores da marca.",
        "acao": "Manter engajamento, oferecer programas de fidelidade e transformá-los em cases de sucesso."
    },
    "🏆 Premium": {
        "quem": "Clientes de receita alta e tempo de relacionamento elevado, mas nem sempre com o NPS mais alto.",
        "importancia": "São clientes fiéis e estáveis, que têm alto ticket médio.",
        "acao": "Investir em atendimento personalizado para elevar a satisfação e fortalecer o vínculo."
    },
    "📈 Potencial de Crescimento": {
        "quem": "Clientes com receita e engajamento medianos, mas com espaço para evoluir.",
        "importancia": "Representam a oportunidade de upsell e expansão.",
        "acao": "Estratégias de cross-sell, treinamentos e ofertas personalizadas para aumentar receita e retenção."
    },
    "⚠️ Em Risco": {
        "quem": "Clientes de baixa receita, NPS negativo e sinais de possível churn.",
        "importancia": "Podem impactar negativamente na taxa de retenção.",
        "acao": "Identificar motivos de insatisfação, atuar em recuperação e avaliar custo-benefício do esforço de retenção."
    },
    "🔄 Estável": {
        "quem": "Clientes de receita consistente, satisfação e fidelidade medianas.",
        "importancia": "Garantem estabilidade no faturamento e representam a 'base sólida'.",
        "acao": "Monitorar e engajar para evitar que migrem para o grupo 'Em Risco', ou estimular evolução para 'Crescimento'/'Premium'."
    }
}

for _, row in metricas.iterrows():
    cluster_id = int(row["Cluster"])
    nome, desc, cor = personas.get(cluster_id, ("❓ Indefinido", [], "#000000"))

    explicacao = explicacoes.get(nome, {})

    st.markdown(f"""
        <div class="cluster-card" style="border: 2px solid {cor};">
            <h2>{nome}</h2>
            <p><b>Cluster:</b> {cluster_id}</p>
            <p><b>Clientes:</b> {int(row['Cliente']):,}</p>
            <p><b>Receita Média:</b> R$ {row['Receita Recorrente Anual (12M)']:.2f} M</p>
            <p><b>Satisfação Média (NPS):</b> {row['Satisfação Média (NPS)']:.2f}</p>
            <p><b>Tempo Médio de Relacionamento:</b> {row['Tempo de Relacionamento (dias)']:.0f} dias</p>
            <ul>
                {''.join([f"<li>{item}</li>" for item in desc])}
            </ul>
            <hr>
            <p><b>Quem são:</b> {explicacao.get("quem", "")}</p>
            <p><b>Importância:</b> {explicacao.get("importancia", "")}</p>
            <p><b>Ação recomendada:</b> {explicacao.get("acao", "")}</p>
        </div>

    """, unsafe_allow_html=True)
