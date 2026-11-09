import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError

from filalivre.bot import criar_tratador
from filalivre.conversa import ConversaEntradaFila
from filalivre.fila import Registrada, estimar_espera
from filalivre.mensagens import texto
from filalivre.modelos import EntradaFila
from tests.conftest import URL_MYSQL

CHAT = 100
QR = "/start REC-SAGUAO"

so_mysql = pytest.mark.skipif(not URL_MYSQL, reason="o SQLite não reproduz os bloqueios do MySQL; defina TEST_DATABASE_URL")


@pytest.fixture
def conversa(fila_service, fabrica_sessoes):
    return ConversaEntradaFila(fila_service, fabrica_sessoes)


def contar_entradas(fabrica_sessoes, chat=CHAT):
    with fabrica_sessoes() as sessao:
        return sessao.scalar(select(func.count()).select_from(EntradaFila).where(EntradaFila.chat_id == chat))


def entrar_na_fila(conversa, chat=CHAT):
    conversa.responder(chat, "Ana", QR)
    conversa.responder(chat, "Ana", "AD4050")
    return conversa.responder(chat, "Ana", "Azul")


def confirmacao(posicao, tempo):
    return texto(
        "entrada_confirmada", posicao=posicao, tempo=tempo, voo="AD4050", companhia="Azul", aeroporto="REC", portao="12"
    )


def test_fluxo_principal_registra_entrada_e_informa_posicao_e_tempo(conversa, fabrica_sessoes):
    assert conversa.responder(CHAT, "Ana", QR) == texto("boas_vindas", local="Saguão de check-in do Aeroporto do Recife")
    assert conversa.responder(CHAT, "Ana", "ad-4050") == texto("pedir_companhia", voo="AD4050")
    assert conversa.responder(CHAT, "Ana", "azul") == confirmacao(posicao=1, tempo=3)
    assert contar_entradas(fabrica_sessoes) == 1


def test_segundo_passageiro_fica_na_posicao_seguinte(conversa):
    entrar_na_fila(conversa, chat=1)
    assert entrar_na_fila(conversa, chat=2) == confirmacao(posicao=2, tempo=5)


@pytest.mark.parametrize("comando", ["/start CODIGO-FALSO", "/start"])
def test_qr_code_invalido_ou_ausente_orienta_procurar_administracao(conversa, comando):
    assert conversa.responder(CHAT, "Ana", comando) == texto("qr_invalido")


def test_mensagem_sem_ter_escaneado_pede_para_escanear(conversa):
    assert conversa.responder(CHAT, "Ana", "AD4050") == texto("sem_sessao")


def test_numero_de_voo_com_formato_invalido_permanece_na_mesma_etapa(conversa):
    conversa.responder(CHAT, "Ana", QR)
    assert conversa.responder(CHAT, "Ana", "voo número 12!") == texto("voo_formato_invalido")
    assert conversa.responder(CHAT, "Ana", "AD4050") == texto("pedir_companhia", voo="AD4050")


def test_voo_nao_encontrado_permite_tentar_novamente(conversa, fabrica_sessoes):
    conversa.responder(CHAT, "Ana", QR)
    conversa.responder(CHAT, "Ana", "XX9999")
    assert conversa.responder(CHAT, "Ana", "Azul") == texto("voo_nao_encontrado", voo="XX9999", companhia="Azul")
    assert conversa.responder(CHAT, "Ana", "AD4050") == texto("pedir_companhia", voo="AD4050")
    assert contar_entradas(fabrica_sessoes) == 0


def test_companhia_diferente_da_do_voo_nao_encontra_voo(conversa):
    conversa.responder(CHAT, "Ana", QR)
    conversa.responder(CHAT, "Ana", "AD4050")
    assert conversa.responder(CHAT, "Ana", "GOL") == texto("voo_nao_encontrado", voo="AD4050", companhia="GOL")


def test_voo_que_ja_partiu_nao_aceita_entrada(conversa, fabrica_sessoes):
    conversa.responder(CHAT, "Ana", QR)
    conversa.responder(CHAT, "Ana", "AD1000")
    assert conversa.responder(CHAT, "Ana", "Azul") == texto("voo_encerrado", voo="AD1000", companhia="Azul")
    assert contar_entradas(fabrica_sessoes) == 0


def test_passageiro_ja_na_fila_nao_entra_de_novo(conversa, fabrica_sessoes):
    entrar_na_fila(conversa)
    esperado = texto("ja_na_fila", posicao=1, tempo=3, voo="AD4050", companhia="Azul")
    assert conversa.responder(CHAT, "Ana", QR) == esperado
    assert conversa.responder(CHAT, "Ana", "qualquer texto") == esperado
    assert contar_entradas(fabrica_sessoes) == 1


def test_sessao_expirada_pede_para_escanear_novamente(fila_service, fabrica_sessoes):
    inicio = datetime(2026, 11, 3, 12)
    ConversaEntradaFila(fila_service, fabrica_sessoes, relogio=lambda: inicio).responder(CHAT, "Ana", QR)

    depois = inicio + timedelta(minutes=31)
    conversa_depois = ConversaEntradaFila(fila_service, fabrica_sessoes, relogio=lambda: depois)
    assert conversa_depois.responder(CHAT, "Ana", "AD4050") == texto("sem_sessao")


def test_estimativa_arredonda_para_cima_e_suporta_zero_balcoes():
    assert estimar_espera(1, 5, 2) == 3
    assert estimar_espera(2, 5, 1) == 10
    assert estimar_espera(2, 5, 0) == 10


def test_get_posicao_retorna_a_posicao_atual_da_fila(conversa):
    assert conversa.responder(CHAT, "Ana", QR) == texto("boas_vindas", local="Saguão de check-in do Aeroporto do Recife")
    assert conversa.responder(CHAT, "Ana", "AD4050") == texto("pedir_companhia", voo="AD4050")
    assert conversa.responder(CHAT, "Ana", "Azul") == confirmacao(posicao=1, tempo=3)

    assert conversa.responder(CHAT, "Ana", "/posicao") == texto(
        "posicao_atualizada",
        posicao=1,
        tempo=3,
        voo="AD4050",
        companhia="Azul",
        aeroporto="REC",
        portao="12",
    )


def test_get_posicao_do_segundo_passageiro_retorna_posicao_dois(conversa):
    entrar_na_fila(conversa, chat=1)
    entrar_na_fila(conversa, chat=2)
    assert conversa.responder(2, "Bia", "/posicao") == texto(
        "posicao_atualizada",
        posicao=2,
        tempo=5,
        voo="AD4050",
        companhia="Azul",
        aeroporto="REC",
        portao="12",
    )


def test_get_posicao_sem_entrada_retorna_mensagem_sem_entrada(conversa):
    assert conversa.responder(CHAT, "Ana", "/posicao") == texto("sem_entrada")


def test_sair_da_fila_remove_entrada_e_recalcula_posicoes(conversa, fabrica_sessoes):
    entrar_na_fila(conversa, chat=1)
    entrar_na_fila(conversa, chat=2)
    assert conversa.responder(2, "Bia", "/sair") == texto("sair_da_fila")

    assert conversa.responder(1, "Ana", "/posicao") == texto(
        "posicao_atualizada",
        posicao=1,
        tempo=3,
        voo="AD4050",
        companhia="Azul",
        aeroporto="REC",
        portao="12",
    )


def test_sair_sem_entrada_retorna_mensagem_sem_entrada(conversa):
    assert conversa.responder(CHAT, "Ana", "/sair") == texto("sem_entrada")


def _update(texto_mensagem):
    return SimpleNamespace(
        effective_message=SimpleNamespace(text=texto_mensagem, reply_text=AsyncMock()),
        effective_chat=SimpleNamespace(id=CHAT),
        effective_user=SimpleNamespace(first_name="Ana"),
    )


def test_bot_responde_com_o_texto_da_conversa(conversa):
    update = _update(QR)
    asyncio.run(criar_tratador(conversa)(update, None))
    update.effective_message.reply_text.assert_awaited_once_with(
        texto("boas_vindas", local="Saguão de check-in do Aeroporto do Recife")
    )


def test_bot_avisa_quando_o_banco_falha():
    conversa_com_falha = Mock()
    conversa_com_falha.responder.side_effect = OperationalError("SELECT 1", {}, Exception("banco fora do ar"))
    update = _update(QR)
    asyncio.run(criar_tratador(conversa_com_falha)(update, None))
    update.effective_message.reply_text.assert_awaited_once_with(texto("indisponivel"))


@so_mysql
def test_entradas_simultaneas_recebem_posicoes_diferentes(fila_service):
    total = 20
    with ThreadPoolExecutor(total) as executor:
        resultados = list(executor.map(lambda chat: fila_service.entrar(chat, "Ana", "REC", "AD4050", "Azul"), range(1, total + 1)))
    assert sorted(r.dados.posicao for r in resultados) == list(range(1, total + 1))


@so_mysql
def test_mensagens_simultaneas_do_mesmo_passageiro_geram_uma_entrada(fila_service, fabrica_sessoes):
    with ThreadPoolExecutor(10) as executor:
        resultados = list(executor.map(lambda _: fila_service.entrar(CHAT, "Ana", "REC", "AD4050", "Azul"), range(10)))
    assert sum(isinstance(r, Registrada) for r in resultados) == 1
    assert contar_entradas(fabrica_sessoes) == 1
