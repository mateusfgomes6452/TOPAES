"""Textos do bot. Suporte multilíngue (RNF03) com pt-BR, en e es."""

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
        "ajuda": (
            "✈️ Comandos disponíveis no Fila Livre:\n\n"
            "📍 /posicao - Consulta sua posição atual na fila e tempo estimado\n"
            "🚪 /sair - Sai da fila virtual de check-in\n"
            "ℹ️ /ajuda - Exibe esta mensagem de ajuda\n\n"
            "Para entrar na fila, escaneie o QR Code no saguão do aeroporto."
        ),
        "indisponivel": "⚠️ O sistema está temporariamente indisponível. Tente novamente em instantes.",
    },
    "en": {
        "boas_vindas": "Hello! Welcome to Fila Livre ✈️\nYou are at: {local}.\n\nWhat is your flight number? (e.g., AD4050)",
        "qr_invalido": "❌ Invalid QR Code. Please contact airport administration.",
        "sem_sessao": "To join the queue, please scan the QR Code available in the airport lobby.",
        "voo_formato_invalido": "❌ Invalid flight number. Must have 2 to 8 letters or numbers (e.g., AD4050). Try again:",
        "pedir_companhia": "What is the airline for flight {voo}?",
        "companhia_invalida": "❌ Please enter the airline name (e.g., Azul):",
        "voo_nao_encontrado": (
            "❌ Flight {voo} by {companhia} was not found at this airport.\n\n"
            "Please check the details and enter the flight number again, or contact airport administration."
        ),
        "voo_encerrado": (
            "❌ Flight {voo} by {companhia} has already departed and is no longer accepting queue entries. "
            "If you need help, please contact airport administration."
        ),
        "entrada_confirmada": (
            "✅ You joined the queue!\n\n"
            "📍 Position: {posicao}\n"
            "⏱️ Estimated wait time: {tempo} min\n\n"
            "✈️ Flight: {voo} ({companhia})\n"
            "🛫 Airport: {aeroporto}\n"
            "🚪 Gate: {portao}\n\n"
            "We will notify you here when your turn arrives."
        ),
        "ja_na_fila": (
            "ℹ️ You are already in the queue.\n\n"
            "📍 Position: {posicao}\n"
            "⏱️ Estimated wait time: {tempo} min\n\n"
            "✈️ Flight: {voo} ({companhia})"
        ),
        "posicao_atualizada": (
            "📍 Current position: {posicao}\n"
            "⏱️ Estimated wait time: {tempo} min\n\n"
            "✈️ Flight: {voo} ({companhia})\n"
            "🛫 Airport: {aeroporto}\n"
            "🚪 Gate: {portao}\n\n"
            "We will notify you here when your turn arrives."
        ),
        "sem_entrada": (
            "📭 You are not in the queue right now.\n\n"
            "To join, scan the QR Code in the airport lobby."
        ),
        "sair_da_fila": (
            "✅ You have left the queue.\n\n"
            "If you need to enter again, scan the lobby QR Code."
        ),
        "ajuda": (
            "✈️ Available commands in Fila Livre:\n\n"
            "📍 /posicao - Check your current position and estimated wait time\n"
            "🚪 /sair - Leave the virtual check-in queue\n"
            "ℹ️ /ajuda - Show this help message\n\n"
            "To join the queue, scan the QR Code in the airport lobby."
        ),
        "indisponivel": "⚠️ The system is temporarily unavailable. Please try again in a few moments.",
    },
    "es": {
        "boas_vindas": "¡Hola! Bienvenido(a) a Fila Livre ✈️\nEstás en: {local}.\n\n¿Cuál es el número de tu vuelo? (ej.: AD4050)",
        "qr_invalido": "❌ Este código QR es inválido. Por favor, dirígete a la administración del aeropuerto.",
        "sem_sessao": "Para entrar a la fila, escanea el código QR disponible en el vestíbulo del aeropuerto.",
        "voo_formato_invalido": "❌ Número de vuelo inválido. Debe tener entre 2 y 8 letras o números (ej.: AD4050). Inténtalo de nuevo:",
        "pedir_companhia": "¿Cuál es la aerolínea del vuelo {voo}?",
        "companhia_invalida": "❌ Indica el nombre de la aerolínea (ej.: Azul):",
        "voo_nao_encontrado": (
            "❌ No encontramos el vuelo {voo} de la aerolínea {companhia} en este aeropuerto.\n\n"
            "Verifica los datos e ingresa el número de vuelo nuevamente, o dirígete a la administración del aeropuerto."
        ),
        "voo_encerrado": (
            "❌ El vuelo {voo} de la aerolínea {companhia} ya partió y no acepta nuevos ingresos. "
            "Si necesitas ayuda, dirígete a la administración del aeropuerto."
        ),
        "entrada_confirmada": (
            "✅ ¡Has entrado a la fila!\n\n"
            "📍 Posición: {posicao}\n"
            "⏱️ Tiempo estimado: {tempo} min\n\n"
            "✈️ Vuelo: {voo} ({companhia})\n"
            "🛫 Aeropuerto: {aeroporto}\n"
            "🚪 Puerta: {portao}\n\n"
            "Te avisaremos aquí cuando sea tu turno."
        ),
        "ja_na_fila": (
            "ℹ️ Ya estás en la fila.\n\n"
            "📍 Posición: {posicao}\n"
            "⏱️ Tiempo estimado: {tempo} min\n\n"
            "✈️ Vuelo: {voo} ({companhia})"
        ),
        "posicao_atualizada": (
            "📍 Posición actual: {posicao}\n"
            "⏱️ Tiempo estimado: {tempo} min\n\n"
            "✈️ Vuelo: {voo} ({companhia})\n"
            "🛫 Aeropuerto: {aeroporto}\n"
            "🚪 Puerta: {portao}\n\n"
            "Te avisaremos aquí cuando sea tu turno."
        ),
        "sem_entrada": (
            "📭 No estás en la fila en este momento.\n\n"
            "Para entrar, escanea el código QR disponible en el vestíbulo del aeropuerto."
        ),
        "sair_da_fila": (
            "✅ Has salido de la fila.\n\n"
            "Si necesitas entrar nuevamente, escanea el código QR del vestíbulo."
        ),
        "ajuda": (
            "✈️ Comandos disponibles en Fila Livre:\n\n"
            "📍 /posicao - Consulta tu posición actual en la fila y tiempo estimado\n"
            "🚪 /sair - Sal de la fila virtual de check-in\n"
            "ℹ️ /ajuda - Muestra este mensaje de ayuda\n\n"
            "Para entrar a la fila, escanea el código QR en el vestíbulo del aeropuerto."
        ),
        "indisponivel": "⚠️ El sistema no está disponible temporalmente. Inténtalo de nuevo en unos momentos.",
    },
}


def texto(chave: str, idioma: str = "pt-BR", **valores: object) -> str:
    mensagens_idioma = MENSAGENS.get(idioma) or MENSAGENS["pt-BR"]
    modelo = mensagens_idioma.get(chave) or MENSAGENS["pt-BR"][chave]
    return modelo.format(**valores)
