"""Liga o Telegram à conversa. Execute com: python -m filalivre.bot"""

import asyncio
import logging
import os

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from filalivre.banco import criar_engine, criar_fabrica_sessoes
from filalivre.conversa import ConversaEntradaFila
from filalivre.fila import FilaService
from filalivre.mensagens import texto

LOG = logging.getLogger(__name__)


def criar_tratador(conversa: ConversaEntradaFila):
    async def tratar(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        mensagem = update.effective_message
        chat_id = update.effective_chat.id
        nome = update.effective_user.first_name
        try:
            # O acesso ao banco é síncrono; em outra thread, não trava o recebimento de mensagens.
            resposta = await asyncio.to_thread(conversa.responder, chat_id, nome, mensagem.text)
        except SQLAlchemyError:
            LOG.exception("Falha ao processar mensagem do chat %s", chat_id)
            resposta = texto("indisponivel")
        await mensagem.reply_text(resposta)

    return tratar


def criar_aplicacao(token: str, conversa: ConversaEntradaFila) -> Application:
    aplicacao = Application.builder().token(token).build()
    aplicacao.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, criar_tratador(conversa)))
    return aplicacao


def _obrigatorio(chave: str) -> str:
    valor = os.environ.get(chave, "").strip()
    if not valor:
        raise SystemExit(f"Configuração ausente: {chave} (veja o .env.example)")
    return valor


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    # O token faz parte da URL das requisições, que o httpx registraria no log em nível INFO.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    token = _obrigatorio("BOT_TOKEN")
    fabrica_sessoes = criar_fabrica_sessoes(criar_engine(_obrigatorio("DATABASE_URL")))
    tempo_medio = int(os.environ.get("TEMPO_MEDIO_PADRAO_MINUTOS") or 5)
    conversa = ConversaEntradaFila(FilaService(fabrica_sessoes, tempo_medio), fabrica_sessoes)

    criar_aplicacao(token, conversa).run_polling()


if __name__ == "__main__":
    main()
