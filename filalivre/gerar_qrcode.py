"""Gera a imagem do QR Code físico, que abre o bot já com o código do ponto de entrada.

Uso: python -m filalivre.gerar_qrcode <usuario_do_bot> <codigo_do_ponto> <arquivo.png>
"""

import re
import sys
from pathlib import Path

import qrcode

# Limites do Telegram para o parâmetro start.
CODIGO_VALIDO = re.compile(r"[A-Za-z0-9_-]{1,64}")


def montar_link(usuario_bot: str, codigo: str) -> str:
    if not CODIGO_VALIDO.fullmatch(codigo):
        raise ValueError("Código inválido: use até 64 letras, números, _ ou -")
    return f"https://t.me/{usuario_bot}?start={codigo}"


def gerar(link: str, arquivo: Path) -> None:
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    qrcode.make(link).save(arquivo)


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    usuario_bot, codigo, arquivo = sys.argv[1:]
    link = montar_link(usuario_bot, codigo)
    gerar(link, Path(arquivo))
    print(f"QR Code de {link} salvo em {arquivo}")


if __name__ == "__main__":
    main()
