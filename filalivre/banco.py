from datetime import datetime, timezone

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker


def criar_engine(url: str) -> Engine:
    if url.startswith("mysql"):
        # No padrão do MySQL (REPEATABLE READ), a contagem feita após esperar o bloqueio
        # leria dados antigos e dois passageiros poderiam receber a mesma posição.
        return create_engine(url, isolation_level="READ COMMITTED", pool_pre_ping=True, pool_recycle=3600)
    return create_engine(url)


def criar_fabrica_sessoes(engine: Engine) -> sessionmaker:
    return sessionmaker(engine, expire_on_commit=False)


def agora_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
