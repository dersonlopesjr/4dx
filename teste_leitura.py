# teste_leitura.py
import os

arquivo = "arquivos/4d.txt"

if not os.path.exists(arquivo):
    print("❌ Arquivo não encontrado! Verifique o caminho.")
else:
    print("✅ Arquivo encontrado. Lendo conteúdo...\n")
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
        print("📄 Conteúdo do arquivo:\n")
        print(conteudo)
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo: {e}")