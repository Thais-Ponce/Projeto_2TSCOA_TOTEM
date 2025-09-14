import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

df = pd.read_csv(r"Projeto/Base_cliente.csv", sep=";", encoding="utf-8")

for col in df.columns:
    if df[col].dtype == "object":  # se for string
        try:
            # troca vírgula por ponto e converte para float
            df[col] = df[col].str.replace(",", ".").astype(float)
        except:
            pass  # se não der pra converter, deixa como está (provavelmente categórica)

categoricas = ["SEGMENTO"]
numericas   = ["Tempo_Relacionamento_media", "RECEITA_RECORRENTE_media", 
               "RESPOSTA_NPS_RELACIONAL", "QTDE_TICKETS_media"]

categoricas = [c for c in categoricas if c in df.columns]
numericas   = [c for c in numericas if c in df.columns]

#Tratamento de dados
for col in numericas:
    df[col] = df[col].fillna(0)

for col in categoricas:
    df[col] = df[col].fillna("Desconhecido")  

preprocess = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numericas),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categoricas)
    ]
)

X = preprocess.fit_transform(df)

#amostra para silhouette
rng = np.random.default_rng(42)
idx = rng.choice(X.shape[0], size=min(3000, X.shape[0]), replace=False)
X_samp = X[idx]

scores = []
for k_try in [3, 4, 5, 6]:
    km = KMeans(n_clusters=k_try, n_init=10, random_state=42).fit(X)
    labels = km.labels_
    sil = silhouette_score(X, labels)
    scores.append((k_try, sil, km.inertia_))

print("k, silhouette, inertia:", scores)

#clusterização
k_final = 4
km_final = KMeans(n_clusters=k_final, n_init=20, random_state=42)
df["cluster"] = km_final.fit_predict(X)

df.to_csv("base_clusterizada.csv", index=False)
print(df["cluster"].value_counts())

pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X.toarray() if hasattr(X, "toarray") else X)

plt.figure(figsize=(8,6))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df["cluster"], cmap='viridis', s=10)
plt.title("Visualização dos Clusters (PCA)")
plt.xlabel("Componente 1")
plt.ylabel("Componente 2")
plt.colorbar(label="Cluster")
plt.show()

perfil = (
    df.groupby("cluster")
      .agg(
          clientes=("cluster","count"),
          tempo_rel_med=("Tempo_Relacionamento_media","mean"),
          receita_med=("RECEITA_RECORRENTE_media","mean"),
          nps_med=("RESPOSTA_NPS_RELACIONAL","mean"),
          tickets_med=("QTDE_TICKETS_media","mean")
      )
      .reset_index()
)

print(perfil)

perfil.to_csv("perfil_clusters.csv", index=False)
