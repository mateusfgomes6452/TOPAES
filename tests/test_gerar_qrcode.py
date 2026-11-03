import pytest
from PIL import Image

from filalivre.gerar_qrcode import gerar, montar_link


def test_monta_link_do_bot_com_o_codigo():
    assert montar_link("fila_livre_bot", "REC-SAGUAO") == "https://t.me/fila_livre_bot?start=REC-SAGUAO"


@pytest.mark.parametrize("codigo", ["codigo com espaço", "a" * 65, ""])
def test_codigo_fora_do_padrao_do_telegram_e_recusado(codigo):
    with pytest.raises(ValueError):
        montar_link("bot", codigo)


def test_gera_imagem_criando_a_pasta(tmp_path):
    arquivo = tmp_path / "qrcodes" / "rec.png"
    gerar("https://t.me/bot?start=REC", arquivo)
    assert Image.open(arquivo).format == "PNG"
