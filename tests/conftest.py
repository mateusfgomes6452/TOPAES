import os

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

from filalivre.banco import criar_engine, criar_fabrica_sessoes
from filalivre.criar_banco import popular_dados_exemplo
from filalivre.fila import FilaService
from filalivre.modelos import Base

# Defina TEST_DATABASE_URL para rodar num MySQL de testes. ATENÇÃO: as tabelas desse banco são apagadas.
URL_MYSQL = os.environ.get("TEST_DATABASE_URL")


@pytest.fixture
def engine():
    if URL_MYSQL:
        engine = criar_engine(URL_MYSQL)
        Base.metadata.drop_all(engine)
    else:
        engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
        event.listen(engine, "connect", lambda con, _: con.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def fabrica_sessoes(engine):
    fabrica = criar_fabrica_sessoes(engine)
    popular_dados_exemplo(fabrica)
    return fabrica


@pytest.fixture
def fila_service(fabrica_sessoes):
    return FilaService(fabrica_sessoes, tempo_medio_padrao=5)
