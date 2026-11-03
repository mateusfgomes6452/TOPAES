"""Cria as tabelas e os dados fictícios de desenvolvimento. Execute com: python -m filalivre.criar_banco"""

import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from filalivre.banco import criar_engine, criar_fabrica_sessoes
from filalivre.modelos import Balcao, Base, PontoQr, Voo


def popular_dados_exemplo(fabrica_sessoes: sessionmaker) -> None:
    """Não há integração com as companhias aéreas, então os voos são fictícios."""
    with fabrica_sessoes.begin() as sessao:
        if sessao.get(PontoQr, "REC-SAGUAO") is not None:
            return
        sessao.add(PontoQr(codigo="REC-SAGUAO", aeroporto="REC", descricao="Saguão de check-in do Aeroporto do Recife"))
        sessao.add_all(
            [
                Voo(numero="AD4050", companhia="Azul", portao="12", horario_partida=datetime(2030, 12, 31, 12), aeroporto="REC"),
                Voo(numero="LA3321", companhia="LATAM", portao="7", horario_partida=datetime(2030, 12, 31, 15, 30), aeroporto="REC"),
                Voo(numero="G31234", companhia="GOL", portao="3", horario_partida=datetime(2030, 12, 31, 18, 45), aeroporto="REC"),
                Voo(numero="AD1000", companhia="Azul", portao="1", horario_partida=datetime(2020, 1, 1, 8), aeroporto="REC"),
            ]
        )
        sessao.add_all(
            [
                Balcao(numero=1, aberto=True, companhia="Azul", aeroporto="REC", terminal="T1"),
                Balcao(numero=2, aberto=True, companhia="Azul", aeroporto="REC", terminal="T1"),
                Balcao(numero=3, aberto=False, companhia="Azul", aeroporto="REC", terminal="T1"),
                Balcao(numero=4, aberto=True, companhia="LATAM", aeroporto="REC", terminal="T1"),
                Balcao(numero=5, aberto=True, companhia="GOL", aeroporto="REC", terminal="T1"),
            ]
        )


def main() -> None:
    load_dotenv()
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise SystemExit("Configuração ausente: DATABASE_URL (veja o .env.example)")
    engine = criar_engine(url)
    Base.metadata.create_all(engine)
    popular_dados_exemplo(criar_fabrica_sessoes(engine))
    print("Banco pronto.")


if __name__ == "__main__":
    main()
