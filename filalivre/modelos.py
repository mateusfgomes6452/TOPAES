"""Entidades do diagrama de classes usadas pelo RF02. Horários sempre em UTC (RNF08)."""

import enum
from datetime import datetime, timedelta

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, ForeignKeyConstraint, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

VALIDADE_SESSAO = timedelta(minutes=30)


class Base(DeclarativeBase):
    pass


class StatusFila(enum.Enum):
    AGUARDANDO = "AGUARDANDO"
    CHAMADO = "CHAMADO"
    ATENDIDO = "ATENDIDO"
    DESISTIU = "DESISTIU"


class Etapa(enum.Enum):
    AGUARDANDO_VOO = "AGUARDANDO_VOO"
    AGUARDANDO_COMPANHIA = "AGUARDANDO_COMPANHIA"


class Passageiro(Base):
    __tablename__ = "passageiro"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    nome: Mapped[str | None] = mapped_column(String(255))
    idioma: Mapped[str] = mapped_column(String(8), default="pt-BR")


class PontoQr(Base):
    """Cada QR Code físico aponta para um registro desta tabela."""

    __tablename__ = "ponto_qr"

    codigo: Mapped[str] = mapped_column(String(64), primary_key=True)
    aeroporto: Mapped[str] = mapped_column(String(8))
    descricao: Mapped[str] = mapped_column(String(255))


class Voo(Base):
    __tablename__ = "voo"

    numero: Mapped[str] = mapped_column(String(8), primary_key=True)
    companhia: Mapped[str] = mapped_column(String(64), primary_key=True)
    portao: Mapped[str] = mapped_column(String(8))
    horario_partida: Mapped[datetime] = mapped_column(DateTime)
    aeroporto: Mapped[str] = mapped_column(String(8))

    def is_ativo(self, agora: datetime) -> bool:
        return self.horario_partida > agora


class Balcao(Base):
    __tablename__ = "balcao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    aberto: Mapped[bool] = mapped_column(Boolean, default=False)
    companhia: Mapped[str] = mapped_column(String(64))
    aeroporto: Mapped[str] = mapped_column(String(8))
    terminal: Mapped[str] = mapped_column(String(16))


class FilaVirtual(Base):
    __tablename__ = "fila_virtual"
    __table_args__ = (
        UniqueConstraint("numero_voo", "companhia", name="uq_fila_voo"),
        ForeignKeyConstraint(["numero_voo", "companhia"], ["voo.numero", "voo.companhia"], name="fk_fila_voo"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    numero_voo: Mapped[str] = mapped_column(String(8))
    companhia: Mapped[str] = mapped_column(String(64))
    tempo_medio_atend: Mapped[int] = mapped_column(Integer)
    ultima_atualizacao: Mapped[datetime] = mapped_column(DateTime)


class EntradaFila(Base):
    __tablename__ = "entrada_fila"
    __table_args__ = (
        Index("idx_entrada_chat_status", "chat_id", "status"),
        Index("idx_entrada_fila_status", "fila_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    fila_id: Mapped[str] = mapped_column(ForeignKey("fila_virtual.id"))
    chat_id: Mapped[int] = mapped_column(ForeignKey("passageiro.chat_id"))
    posicao: Mapped[int] = mapped_column(Integer)
    horario_entrada: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[StatusFila] = mapped_column(Enum(StatusFila, native_enum=False, length=16))
    tempo_estimado: Mapped[int] = mapped_column(Integer)


class SessaoBot(Base):
    """Etapa da conversa enquanto o passageiro ainda não entrou na fila."""

    __tablename__ = "sessao_bot"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    etapa: Mapped[Etapa] = mapped_column(Enum(Etapa, native_enum=False, length=32))
    codigo_qr: Mapped[str] = mapped_column(String(64))
    numero_voo: Mapped[str | None] = mapped_column(String(8))
    ultima_mensagem: Mapped[datetime] = mapped_column(DateTime)

    def is_valida(self, agora: datetime) -> bool:
        return self.ultima_mensagem + VALIDADE_SESSAO > agora
