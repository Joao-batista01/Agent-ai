
import streamlit as st
import pandas as pd
import requests

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Agente de Futebol", page_icon="⚽")

st.title("⚽ Agente de IA - Premier League")

# =========================
# CARREGAR DATASET
# =========================
df = pd.read_csv("dataset - 2020-09-24.csv", on_bad_lines='skip')

colunas = [
    "Name",
    "Club",
    "Position",
    "Nationality",
    "Age",
    "Appearances",
    "Goals",
    "Assists",
    "Shots",
    "Passes",
    "Tackles",
    "Yellow cards",
    "Red cards"
]

df = df[colunas]

# =========================
# ENCONTRAR JOGADOR
# =========================
def encontrar_jogador(pergunta):
    pergunta = pergunta.lower()

    for nome in df["Name"]:
        if nome.lower() in pergunta:
            return nome

    return None

# =========================
# FUNÇÃO DO AGENTE
# =========================
def perguntar(pergunta):

    jogador = encontrar_jogador(pergunta)

    if not jogador:
        return "❌ Jogador não encontrado no dataset."

    filtro = df[df["Name"] == jogador].head(1)

    contexto = ""

    for _, row in filtro.iterrows():
        contexto += f"""
Player: {row['Name']}
Club: {row['Club']}
Position: {row['Position']}
Nationality: {row['Nationality']}
Age: {row['Age']}
Appearances: {row['Appearances']}
Goals: {row['Goals']}
Assists: {row['Assists']}
Shots: {row['Shots']}
Passes: {row['Passes']}
Tackles: {row['Tackles']}
Yellow cards: {row['Yellow cards']}
Red cards: {row['Red cards']}
---
"""

    prompt = f"""
Você é um assistente especialista em jogadores da Premier League.

Use apenas os dados abaixo para responder.

{contexto}

Pergunta: {pergunta}

Responda usando os dados fornecidos.
Seja claro e direto.
Se a informação não estiver disponível, diga isso.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    try:
        return response.json().get("response", "Erro na resposta")
    except:
        return "Erro ao processar resposta"


# =========================
# INTERFACE
# =========================
pergunta = st.text_input("Faça sua pergunta sobre um jogador:")

if st.button("Perguntar"):
    if pergunta:
        with st.spinner("Pensando..."):
            resposta = perguntar(pergunta)
        st.success(resposta)
    else:
        st.warning("Digite uma pergunta primeiro.")