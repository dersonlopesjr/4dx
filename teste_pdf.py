# teste_pdf.py
from langchain.document_loaders import PyPDFLoader
import os

caminho = "arquivos/Building a Second Brain.pdf"  # ⚠️ Mude o nome se for diferente

if not os.path.exists(caminho):
    print("❌ Arquivo não encontrado! Verifique o nome.")
else:
    print("✅ Arquivo encontrado. Carregando...")
    loader = PyPDFLoader(caminho)
    docs = loader.load()
    print(f"\n📄 Total de páginas carregadas: {len(docs)}")

    if len(docs) > 0:
        print(f"\n🔍 Primeira página (primeiros 500 caracteres):\n{docs[0].page_content[:500]}")
    else:
        print("❌ Nenhum texto foi extraído. O PDF pode estar protegido ou com formatação estranha.")