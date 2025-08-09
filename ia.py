# ia.py - IA que responde com base no seu arquivo TXT
import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Configurações
PASTA_ARQUIVOS = "arquivos"
PASTA_BANCO = "db"
ARQUIVO_TEXTO = "4d.txt"

# 1. Carregar o arquivo TXT com múltiplos encodings
print("📚 Carregando o arquivo 4d.txt...")
documentos = []
caminho = os.path.join(PASTA_ARQUIVOS, ARQUIVO_TEXTO)

if not os.path.exists(caminho):
    print(f"❌ Arquivo não encontrado: {caminho}")
    print("Verifique se o arquivo '4d.txt' está dentro da pasta 'arquivos'")
    exit()

encodings = ["utf-8", "latin1", "iso-8859-1", "cp1252"]
conteudo = None

for enc in encodings:
    try:
        with open(caminho, "r", encoding=enc) as f:
            conteudo = f.read()
        print(f"✅ Carregado com encoding: {enc}")
        break
    except Exception as e:
        print(f"⚠️ Falha ao ler com {enc}: {e}")
        continue

if conteudo is None:
    print("❌ Erro: Não foi possível ler o arquivo com nenhum encoding.")
    exit()

# Criar documento LangChain
from langchain.docstore.document import Document
doc = Document(page_content=conteudo, metadata={"source": ARQUIVO_TEXTO})
documentos = [doc]

# 2. Dividir o texto
print("✂️ Dividindo o texto...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""]
)
pedacos = splitter.split_documents(documentos)
print(f"✅ {len(pedacos)} pedaços criados")

# 3. Apagar banco antigo e criar novo
print("🧠 Criando banco de conhecimento...")
if os.path.exists(PASTA_BANCO):
    import shutil
    shutil.rmtree(PASTA_BANCO)
    print("🗑️ Banco antigo apagado")

# Usar embeddings local (sem depender do Ollama)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma.from_documents(pedacos, embeddings, persist_directory=PASTA_BANCO)
retriever = db.as_retriever(search_kwargs={"k": 4})

# 4. Configurar IA com Llama 3 (resposta) + Prompt em português
print("🤖 IA pronta! Pode fazer perguntas (digite 'sair' para encerrar)\n")

llm = OllamaLLM(model="llama3")

prompt_template = """Use APENAS o contexto abaixo para responder em português brasileiro.
Se a informação não estiver no contexto, diga exatamente: "Não encontrei isso no texto."
Não invente, não adivinhe. Seja claro e direto.

Contexto:
{context}

Pergunta:
{question}

Resposta (baseada apenas no texto):
"""
PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": PROMPT}
)

# 5. Loop de perguntas
while True:
    pergunta = input("Você: ").strip()
    if pergunta.lower() in ["sair", "exit", "quit", "parar"]:
        print("Até logo! 👋")
        break
    if not pergunta:
        continue
    try:
        resposta = qa.invoke({"query": pergunta})
        print(f"IA: {resposta['result']}\n")
    except Exception as e:
        print(f"❌ Erro ao gerar resposta: {e}\n")