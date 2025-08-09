# app.py - Chat web completo e autocontido
import os
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# === Configurações ===
PASTA_ARQUIVOS = "Arquivos"
ARQUIVO_TEXTO = "4d.txt"
PASTA_BANCO = "db_chroma"

# === 1. Carregar o conteúdo do TXT ===
@st.cache_data
def carregar_conteudo():
    arquivo_path = os.path.join(PASTA_ARQUIVOS, ARQUIVO_TEXTO)
    if not os.path.exists(arquivo_path):
        st.error(f"❌ Arquivo não encontrado: {arquivo_path}")
        st.error("Verifique se o arquivo '4d.txt' está na pasta 'Arquivos' no GitHub.")
        st.stop()
    try:
        with open(arquivo_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")
        st.stop()

# === 2. Dividir o texto em pedaços ===
@st.cache_resource
def criar_retriever():
    conteudo = carregar_conteudo()
    doc = Document(page_content=conteudo, metadata={"source": ARQUIVO_TEXTO})
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    pedacos = splitter.split_documents([doc])
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Apagar banco antigo
    if os.path.exists(PASTA_BANCO):
        import shutil
        shutil.rmtree(PASTA_BANCO)
    
    db = Chroma.from_documents(pedacos, embeddings, persist_directory=PASTA_BANCO)
    return db.as_retriever(search_kwargs={"k": 4})

# === 3. Configurar IA com prompt em português ===
@st.cache_resource
def criar_chain():
    retriever = criar_retriever()
    llm = OllamaLLM(model="llama3")
    
    prompt_template = """Use APENAS o contexto abaixo para responder em português brasileiro.
Se a informação não estiver no contexto, diga: "Não encontrei isso no texto."
Não invente. Seja claro e direto.

Contexto:
{context}

Pergunta:
{question}

Resposta:
"""
    from langchain.prompts import PromptTemplate
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT}
    )

# === 4. Interface do usuário ===
st.set_page_config(page_title="Assistente 4D", page_icon="🤖")
st.title("💬 Assistente das 4 Disciplinas da Execução")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Inicializar a chain
try:
    qa = criar_chain()
except Exception as e:
    st.error(f"❌ Erro ao inicializar a IA: {e}")
    st.stop()

# Entrada do usuário
if prompt := st.chat_input("Faça uma pergunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            resposta = qa.invoke({"query": prompt})
            texto = resposta["result"]
        except Exception as e:
            texto = "Erro ao gerar resposta. Tente novamente."
        st.markdown(texto)
        st.session_state.messages.append({"role": "assistant", "content": texto})