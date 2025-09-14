import streamlit as st

PRIMARY = "#1C3D5A"  # azul petróleo
ACCENT  = "#B49047"  # dourado
BG      = "#F1E5D1"  # areia

st.set_page_config(page_title="TOTEM", layout="wide")


st.markdown(f"""
    <style>
    .stApp {{
        background-color: {BG};
    }}
    h1, h2, h3, h4, h5, h6, p, li, span {{
        color: {PRIMARY} !important;
    }}
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {PRIMARY} !important;
    }}
    section[data-testid="stSidebar"] *  {{ 
        color: white !important;
     }}
    /* Remove fundo e sombra de blocos */
    .stMarkdown {{
        background: transparent !important;
    }}
    .stMarkdown div {{
        background: transparent !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
    }}
    </style>
""", unsafe_allow_html=True)


st.image(
    r"C:\Users\thais\OneDrive\Documentos\Faculdade\2º Ano\Challenge\Projeto\banner.png",
    use_column_width=True
)

st.title("Apresentação")
st.header("Clusterização de Clientes TOTEM")

st.markdown(
    """
<div style="text-align: center; font-size:20px; line-height:1.6; color:#1C3D5A;">
A TOTEM é uma empresa especializada em inteligência de dados voltada à 
personalização do relacionamento com o cliente.<br><br>

Nosso propósito é transformar grandes volumes de dados em insights estratégicos, 
permitindo que empresas compreendam melhor seus públicos e entreguem experiências mais 
<b>relevantes, eficientes e direcionadas.</b><br><br>

Combinamos tecnologia, ciência de dados e conhecimento de comportamento do consumidor
para ajudar nossos parceiros a tomarem decisões mais inteligentes, aumentarem a fidelização 
e criarem conexões mais significativas com seus clientes.
</div>
    """,
    unsafe_allow_html=True
)