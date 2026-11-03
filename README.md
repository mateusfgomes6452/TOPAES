# Fila Livre

Fila virtual de check-in em aeroportos, com bot do Telegram como canal do passageiro.

Implementado até agora: **[RF02] Entrar na Fila Virtual via QR Code**.

## Fluxo

1. O passageiro escaneia o QR Code do saguão, que abre `https://t.me/<bot>?start=<codigo_do_ponto>`.
2. O bot valida o código e pede o número do voo e a companhia aérea.
3. O sistema registra a entrada e informa a posição e o tempo estimado.

Tempo estimado: `posição × tempo médio de atendimento ÷ balcões abertos da companhia`, arredondado para cima.

## Estrutura

| Módulo em `filalivre/` | Responsabilidade |
|---|---|
| `bot.py` | Integração com o Telegram e início da aplicação |
| `conversa.py` | Etapas da conversa com o passageiro |
| `fila.py` | Regras de entrada e cálculo do tempo estimado |
| `modelos.py` | Entidades do diagrama de classes e tabelas |
| `mensagens.py` | Textos do bot |
| `criar_banco.py` | Criação das tabelas e dados fictícios |
| `gerar_qrcode.py` | Geração da imagem do QR Code |

## Como executar

Requisitos: Python 3.12 (no Ubuntu, também o pacote `python3.12-venv`) e MySQL 8.

1. Crie o bot no [@BotFather](https://t.me/BotFather) com `/newbot` e guarde o token e o nome de usuário.

2. Instale as dependências:

   ```bash
   python3 -m venv .venv
   ```

   ```bash
   .venv/bin/pip install -r requirements.txt
   ```

3. Crie o banco e o usuário no MySQL:

   ```bash
   sudo mysql -e "CREATE DATABASE fila_livre CHARACTER SET utf8mb4; CREATE USER 'fila_livre'@'localhost' IDENTIFIED BY 'troque_esta_senha'; GRANT ALL ON fila_livre.* TO 'fila_livre'@'localhost';"
   ```

4. Copie `.env.example` para `.env` e preencha. O `.env` guarda o token e nunca deve ser enviado ao Git.

   ```bash
   cp .env.example .env
   ```

5. Crie as tabelas e os dados fictícios:

   ```bash
   .venv/bin/python -m filalivre.criar_banco
   ```

6. Inicie o bot:

   ```bash
   .venv/bin/python -m filalivre.bot
   ```

7. Gere o QR Code, trocando `<usuario_do_bot>` pelo nome de usuário do bot:

   ```bash
   .venv/bin/python -m filalivre.gerar_qrcode <usuario_do_bot> REC-SAGUAO qrcodes/rec-saguao.png
   ```

Para testar, escaneie o QR Code e informe o voo `AD4050` e a companhia `Azul`. Os outros voos fictícios estão em `filalivre/criar_banco.py`.

## Testes

```bash
.venv/bin/pip install -r requirements-dev.txt
```

```bash
.venv/bin/python -m pytest
```

Por padrão, os testes usam SQLite em memória e não precisam de MySQL nem de token. Os testes de entradas simultâneas só rodam em MySQL, porque o SQLite não reproduz os bloqueios. Para incluí-los, aponte para um banco **exclusivo de testes**, pois as tabelas dele são apagadas:

```bash
TEST_DATABASE_URL='mysql+pymysql://fila_livre:troque_esta_senha@localhost:3306/fila_livre_teste?charset=utf8mb4' .venv/bin/python -m pytest
```
