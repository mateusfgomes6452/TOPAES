"""Textos do bot. Novos idiomas (RNF03) entram como novas chaves em MENSAGENS."""

MENSAGENS = {
    "pt-BR": {
        "boas_vindas": "Olá! Bem-vindo(a) ao Fila Livre ✈️\nVocê está em: {local}.\n\nQual é o número do seu voo? (ex.: AD4050)",
        "qr_invalido": "❌ Este QR Code é inválido. Por favor, dirija-se à administração do aeroporto.",
        "sem_sessao": "Para entrar na fila, escaneie o QR Code disponível no saguão do aeroporto.",
        "voo_formato_invalido": "❌ Número de voo inválido. Ele deve ter de 2 a 8 letras ou números (ex.: AD4050). Tente novamente:",
        "pedir_companhia": "Qual é a companhia aérea do voo {voo}?",
        "companhia_invalida": "❌ Informe o nome da companhia aérea (ex.: Azul):",
        "voo_nao_encontrado": (
            "❌ Não encontramos o voo {voo} da companhia {companhia} neste aeroporto.\n\n"
            "Confira os dados e informe o número do voo novamente, ou dirija-se à administração do aeroporto."
        ),
        "voo_encerrado": (
            "❌ O voo {voo} da companhia {companhia} já partiu e não aceita novas entradas. "
            "Se precisar de ajuda, dirija-se à administração do aeroporto."
        ),
        "entrada_confirmada": (
            "✅ Você entrou na fila!\n\n"
            "📍 Posição: {posicao}\n"
            "⏱️ Tempo estimado: {tempo} min\n\n"
            "✈️ Voo: {voo} ({companhia})\n"
            "🛫 Aeroporto: {aeroporto}\n"
            "🚪 Portão: {portao}\n\n"
            "Avisaremos aqui quando chegar a sua vez."
        ),
        "ja_na_fila": (
            "ℹ️ Você já está na fila.\n\n"
            "📍 Posição: {posicao}\n"
            "⏱️ Tempo estimado: {tempo} min\n\n"
            "✈️ Voo: {voo} ({companhia})"
        ),
        "posicao_atualizada": (
            "📍 Posição atual: {posicao}\n"
            "⏱️ Tempo estimado: {tempo} min\n\n"
            "✈️ Voo: {voo} ({companhia})\n"
            "🛫 Aeroporto: {aeroporto}\n"
            "🚪 Portão: {portao}\n\n"
            "Avisaremos aqui quando chegar a sua vez."
        ),
        "sem_entrada": (
            "📭 Você não está na fila no momento.\n\n"
            "Para entrar, escaneie o QR Code disponível no saguão do aeroporto."
        ),
        "sair_da_fila": (
            "✅ Você saiu da fila.\n\n"
            "Se precisar entrar novamente, escaneie o QR Code do saguão."
        ),
        "indisponivel": "⚠️ O sistema está temporariamente indisponível. Tente novamente em instantes.",
    }
}


def texto(chave: str, **valores: object) -> str:
    return MENSAGENS["pt-BR"][chave].format(**valores)
