# bot.py - Bot do Telegram que usa sua IA
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio

# === COLE SEU TOKEN AQUI ===
TOKEN = "8153800431:AAFa7_Pfc7IoGOiCErl0y6HUXSfFDCRqsXs"  # Ex: 731281293:AAHd8c9a8sda8s7d8as7d8a7s8d7a8s7d8a

# Reutiliza sua IA do ia.py
from ia import qa  # Importa a chain de perguntas e respostas

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = update.message.text
    print(f"Pergunta de {update.effective_user.first_name}: {pergunta}")
    
    try:
        resposta = qa.invoke({"query": pergunta})
        texto = resposta["result"]
    except Exception as e:
        texto = "Erro ao gerar resposta. Tente novamente."
        print(f"Erro: {e}")
    
    await update.message.reply_text(texto)

def main():
    print("🚀 Bot do Telegram iniciado. Escutando mensagens...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    
    app.run_polling()

if __name__ == "__main__":
    main()