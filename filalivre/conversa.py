"""Fluxo do RF02: recebe o texto do passageiro e devolve a resposta do bot, sem depender da API do Telegram."""

import re
from collections.abc import Callable
from datetime import datetime

from sqlalchemy.orm import sessionmaker

from filalivre.banco import agora_utc
from filalivre.fila import DadosEntrada, FilaService, JaNaFila, Registrada, VooEncerrado, VooNaoEncontrado
from filalivre.mensagens import texto as msg
from filalivre.modelos import Etapa, PontoQr, SessaoBot

COMANDO_START = "/start"
COMANDO_POSICAO = "/posicao"
COMANDO_SAIR = "/sair"
NUMERO_VOO = re.compile(r"[A-Z0-9]{2,8}")
TAMANHO_MAXIMO_COMPANHIA = 64


class ConversaEntradaFila:
    def __init__(
        self,
        fila_service: FilaService,
        fabrica_sessoes: sessionmaker,
        relogio: Callable[[], datetime] = agora_utc,
    ) -> None:
        self._fila_service = fila_service
        self._fabrica_sessoes = fabrica_sessoes
        self._relogio = relogio

    def responder(self, chat_id: int, nome: str | None, texto: str) -> str:
        mensagem = texto.strip()
        comando, _, argumento = mensagem.partition(" ")
        if comando == COMANDO_START:
            return self._iniciar(chat_id, argumento.strip())
        if comando == COMANDO_POSICAO:
            return self._posicao(chat_id)
        if comando == COMANDO_SAIR:
            return self._sair(chat_id)

        sessao = self._buscar_sessao(chat_id)
        if sessao is None or not sessao.is_valida(self._relogio()):
            return self._responder_sem_sessao(chat_id)
        if sessao.etapa == Etapa.AGUARDANDO_VOO:
            return self._receber_voo(sessao, mensagem)
        return self._receber_companhia(sessao, nome, mensagem)

    def _iniciar(self, chat_id: int, codigo_qr: str) -> str:
        entrada = self._fila_service.buscar_entrada_ativa(chat_id)
        if entrada is not None:
            self._remover_sessao(chat_id)
            return _ja_na_fila(entrada)

        ponto = self._buscar_ponto(codigo_qr) if codigo_qr else None
        if ponto is None:
            self._remover_sessao(chat_id)
            return msg("qr_invalido")

        self._salvar_sessao(chat_id, Etapa.AGUARDANDO_VOO, ponto.codigo, None)
        return msg("boas_vindas", local=ponto.descricao)

    def _posicao(self, chat_id: int) -> str:
        """Retorna a posição atual do passageiro na fila, se ele estiver nela."""
        entrada = self._fila_service.buscar_entrada_ativa(chat_id)
        if entrada is None:
            return msg("sem_entrada")
        return msg(
            "posicao_atualizada",
            posicao=entrada.posicao,
            tempo=entrada.tempo_estimado,
            voo=entrada.numero_voo,
            companhia=entrada.companhia,
            aeroporto=entrada.aeroporto,
            portao=entrada.portao,
        )

    def _sair(self, chat_id: int) -> str:
        """Retira o passageiro da fila, se ele estiver nela, e recalcula as posições dos demais."""
        if self._fila_service.sair(chat_id):
            return msg("sair_da_fila")
        return msg("sem_entrada")

    def _responder_sem_sessao(self, chat_id: int) -> str:
        entrada = self._fila_service.buscar_entrada_ativa(chat_id)
        return _ja_na_fila(entrada) if entrada is not None else msg("sem_sessao")

    def _receber_voo(self, sessao: SessaoBot, texto: str) -> str:
        numero_voo = re.sub(r"[\s-]", "", texto).upper()
        if not NUMERO_VOO.fullmatch(numero_voo):
            return msg("voo_formato_invalido")
        self._salvar_sessao(sessao.chat_id, Etapa.AGUARDANDO_COMPANHIA, sessao.codigo_qr, numero_voo)
        return msg("pedir_companhia", voo=numero_voo)

    def _receber_companhia(self, sessao: SessaoBot, nome: str | None, companhia: str) -> str:
        if not companhia or len(companhia) > TAMANHO_MAXIMO_COMPANHIA:
            return msg("companhia_invalida")

        ponto = self._buscar_ponto(sessao.codigo_qr)
        if ponto is None:
            self._remover_sessao(sessao.chat_id)
            return msg("qr_invalido")

        resultado = self._fila_service.entrar(sessao.chat_id, nome, ponto.aeroporto, sessao.numero_voo, companhia)
        match resultado:
            case Registrada(dados):
                self._remover_sessao(sessao.chat_id)
                return msg(
                    "entrada_confirmada",
                    posicao=dados.posicao,
                    tempo=dados.tempo_estimado,
                    voo=dados.numero_voo,
                    companhia=dados.companhia,
                    aeroporto=dados.aeroporto,
                    portao=dados.portao,
                )
            case JaNaFila(dados):
                self._remover_sessao(sessao.chat_id)
                return _ja_na_fila(dados)
            case VooNaoEncontrado():
                self._salvar_sessao(sessao.chat_id, Etapa.AGUARDANDO_VOO, sessao.codigo_qr, None)
                return msg("voo_nao_encontrado", voo=sessao.numero_voo, companhia=companhia)
            case VooEncerrado():
                self._remover_sessao(sessao.chat_id)
                return msg("voo_encerrado", voo=sessao.numero_voo, companhia=companhia)

    def _buscar_ponto(self, codigo: str) -> PontoQr | None:
        with self._fabrica_sessoes() as sessao:
            return sessao.get(PontoQr, codigo)

    def _buscar_sessao(self, chat_id: int) -> SessaoBot | None:
        with self._fabrica_sessoes() as sessao:
            return sessao.get(SessaoBot, chat_id)

    def _salvar_sessao(self, chat_id: int, etapa: Etapa, codigo_qr: str, numero_voo: str | None) -> None:
        with self._fabrica_sessoes.begin() as sessao:
            sessao.merge(
                SessaoBot(
                    chat_id=chat_id,
                    etapa=etapa,
                    codigo_qr=codigo_qr,
                    numero_voo=numero_voo,
                    ultima_mensagem=self._relogio(),
                )
            )

    def _remover_sessao(self, chat_id: int) -> None:
        with self._fabrica_sessoes.begin() as sessao:
            registro = sessao.get(SessaoBot, chat_id)
            if registro is not None:
                sessao.delete(registro)


def _ja_na_fila(dados: DadosEntrada) -> str:
    return msg(
        "ja_na_fila",
        posicao=dados.posicao,
        tempo=dados.tempo_estimado,
        voo=dados.numero_voo,
        companhia=dados.companhia,
    )
