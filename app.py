import streamlit as st
import pandas as pd
import requests


# CONFIG

st.set_page_config(page_title="Agente de Futebol", page_icon="⚽")

st.title("⚽ Agente de IA - Premier League")

st.write("Faça perguntas sobre jogadores da Premier League.")


# BOTÃO LIMPAR CONVERSA

if st.button("🗑 Limpar conversa"):
    st.session_state.mensagens = []
    st.rerun()


# HISTÓRICO DE CHAT

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []


# CARREGAR DATASET

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


# ENCONTRAR JOGADORES

def encontrar_jogadores(pergunta):

    pergunta = pergunta.lower()

    jogadores_encontrados = []

    for nome in df["Name"]:

        partes_nome = nome.lower().split()

        for parte in partes_nome:

            if len(parte) > 2 and parte in pergunta:

                if nome not in jogadores_encontrados:
                    jogadores_encontrados.append(nome)

    return jogadores_encontrados


# FUNÇÃO PRINCIPAL

def perguntar(pergunta):

    jogadores = encontrar_jogadores(pergunta)

    if len(jogadores) == 0:
        return "❌ Nenhum jogador encontrado no dataset."

    contexto = ""

    for jogador in jogadores:

        filtro = df[df["Name"] == jogador].head(1)

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
Você é um especialista em jogadores da Premier League.

Use apenas os dados abaixo para responder.

{contexto}

Pergunta: {pergunta}

Se for uma comparação:
- compare os jogadores corretamente
- diga quem tem melhores números

Seja claro, direto e objetivo.
Se a informação não estiver disponível, diga isso.
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        data = response.json()

        return data.get("response", "❌ Erro na resposta do modelo.")

    except Exception as e:
        return f"❌ Erro: {e}"


# MOSTRAR HISTÓRICO

for mensagem in st.session_state.mensagens:

    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])


# INPUT DO USUÁRIO

pergunta = st.chat_input("Digite sua pergunta...")

if pergunta:

    # salvar pergunta
    st.session_state.mensagens.append({
        "role": "user",
        "content": pergunta
    })

    # mostrar pergunta
    with st.chat_message("user"):
        st.markdown(pergunta)

    # gerar resposta
    with st.chat_message("assistant"):

        with st.spinner("Pensando..."):

            resposta = perguntar(pergunta)

            st.markdown(resposta)

    # salvar resposta
    st.session_state.mensagens.append({
        "role": "assistant",
        "content": resposta
    })
