"""Regras de entrada na fila virtual (RF02)."""

import math
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from filalivre.banco import agora_utc
from filalivre.modelos import Balcao, EntradaFila, FilaVirtual, Passageiro, StatusFila, Voo


@dataclass(frozen=True)
class DadosEntrada:
    posicao: int
    tempo_estimado: int
    numero_voo: str
    companhia: str
    aeroporto: str
    portao: str


@dataclass(frozen=True)
class Registrada:
    dados: DadosEntrada


@dataclass(frozen=True)
class JaNaFila:
    dados: DadosEntrada


@dataclass(frozen=True)
class VooNaoEncontrado:
    pass


@dataclass(frozen=True)
class VooEncerrado:
    pass


ResultadoEntrada = Registrada | JaNaFila | VooNaoEncontrado | VooEncerrado


def estimar_espera(posicao: int, tempo_medio_minutos: int, balcoes_abertos: int) -> int:
    """Posição × tempo médio ÷ balcões abertos, arredondado para cima.

    Sem balcão aberto, calcula como se houvesse um, pois ainda não há previsão de abertura.
    """
    return math.ceil(posicao * tempo_medio_minutos / max(balcoes_abertos, 1))


class FilaService:
    def __init__(
        self,
        fabrica_sessoes: sessionmaker,
        tempo_medio_padrao: int,
        relogio: Callable[[], datetime] = agora_utc,
    ) -> None:
        self._fabrica_sessoes = fabrica_sessoes
        self._tempo_medio_padrao = tempo_medio_padrao
        self._relogio = relogio

    def buscar_entrada_ativa(self, chat_id: int) -> DadosEntrada | None:
        with self._fabrica_sessoes() as sessao:
            return self._entrada_ativa(sessao, chat_id)

    def entrar(self, chat_id: int, nome: str | None, aeroporto: str, numero_voo: str, companhia: str) -> ResultadoEntrada:
        with self._fabrica_sessoes.begin() as sessao:
            return self._registrar(sessao, chat_id, nome, aeroporto, numero_voo, companhia)

    def _registrar(
        self, sessao: Session, chat_id: int, nome: str | None, aeroporto: str, numero_voo: str, companhia: str
    ) -> ResultadoEntrada:
        agora = self._relogio()

        voo = sessao.scalar(
            select(Voo).where(
                Voo.numero == numero_voo,
                func.lower(Voo.companhia) == companhia.lower(),
                Voo.aeroporto == aeroporto,
            )
        )
        if voo is None:
            return VooNaoEncontrado()
        if not voo.is_ativo(agora):
            return VooEncerrado()

        # A ordem dos bloqueios é sempre passageiro e depois fila, para evitar deadlock.
        self._bloquear_passageiro(sessao, chat_id, nome)
        existente = self._entrada_ativa(sessao, chat_id)
        if existente is not None:
            return JaNaFila(existente)

        fila = self._bloquear_fila(sessao, voo, agora)
        aguardando = sessao.scalar(
            select(func.count())
            .select_from(EntradaFila)
            .where(EntradaFila.fila_id == fila.id, EntradaFila.status == StatusFila.AGUARDANDO)
        )
        balcoes = sessao.scalar(
            select(func.count())
            .select_from(Balcao)
            .where(Balcao.aberto.is_(True), Balcao.companhia == voo.companhia, Balcao.aeroporto == voo.aeroporto)
        )
        posicao = aguardando + 1
        tempo_estimado = estimar_espera(posicao, fila.tempo_medio_atend, balcoes)

        sessao.add(
            EntradaFila(
                id=str(uuid.uuid4()),
                fila_id=fila.id,
                chat_id=chat_id,
                posicao=posicao,
                horario_entrada=agora,
                status=StatusFila.AGUARDANDO,
                tempo_estimado=tempo_estimado,
            )
        )
        fila.ultima_atualizacao = agora
        return Registrada(_dados(posicao, tempo_estimado, voo))

    def _bloquear_passageiro(self, sessao: Session, chat_id: int, nome: str | None) -> None:
        """Garante que o passageiro existe e bloqueia seu registro, evitando entrada duplicada em mensagens simultâneas."""
        consulta = select(Passageiro).where(Passageiro.chat_id == chat_id).with_for_update()
        if sessao.scalar(consulta) is None:
            self._inserir_se_ausente(sessao, Passageiro(chat_id=chat_id, nome=nome))
            sessao.scalar(consulta.execution_options(populate_existing=True))

    def _bloquear_fila(self, sessao: Session, voo: Voo, agora: datetime) -> FilaVirtual:
        """Obtém ou cria a fila do voo e a bloqueia, para que duas entradas não recebam a mesma posição."""
        consulta = (
            select(FilaVirtual)
            .where(FilaVirtual.numero_voo == voo.numero, FilaVirtual.companhia == voo.companhia)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        fila = sessao.scalar(consulta)
        if fila is not None:
            return fila
        self._inserir_se_ausente(
            sessao,
            FilaVirtual(
                id=str(uuid.uuid4()),
                numero_voo=voo.numero,
                companhia=voo.companhia,
                tempo_medio_atend=self._tempo_medio_padrao,
                ultima_atualizacao=agora,
            ),
        )
        return sessao.scalars(consulta).one()

    @staticmethod
    def _inserir_se_ausente(sessao: Session, registro: Passageiro | FilaVirtual) -> None:
        """Outra transação pode ter criado o mesmo registro ao mesmo tempo; nesse caso, usa o dela."""
        try:
            with sessao.begin_nested():
                sessao.add(registro)
        except IntegrityError:
            pass

    @staticmethod
    def _entrada_ativa(sessao: Session, chat_id: int) -> DadosEntrada | None:
        linha = sessao.execute(
            select(EntradaFila, Voo)
            .join(FilaVirtual, FilaVirtual.id == EntradaFila.fila_id)
            .join(Voo, and_(Voo.numero == FilaVirtual.numero_voo, Voo.companhia == FilaVirtual.companhia))
            .where(EntradaFila.chat_id == chat_id, EntradaFila.status.in_([StatusFila.AGUARDANDO, StatusFila.CHAMADO]))
        ).first()
        if linha is None:
            return None
        entrada, voo = linha
        return _dados(entrada.posicao, entrada.tempo_estimado, voo)


def _dados(posicao: int, tempo_estimado: int, voo: Voo) -> DadosEntrada:
    return DadosEntrada(posicao, tempo_estimado, voo.numero, voo.companhia, voo.aeroporto, voo.portao)
