# app.py - Chat web para o seu assistente
import streamlit as st
from ia import qa

st.set_page_config(page_title="Assistente 4D", page_icon="🤖")
st.title("💬 Assistente das 4 Disciplinas da Execução")

# Instrução clara
st.markdown("Pergunte algo sobre as 4 Disciplinas da Execução. Ex: *'Quais são as 4 disciplinas?'*")

# Histórico de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário
if prompt := st.chat_input("Faça uma pergunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = qa.invoke({"query": prompt})
            resposta = response["result"]
        except Exception as e:
            resposta = "Erro ao gerar resposta. Tente novamente."
        st.markdown(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
