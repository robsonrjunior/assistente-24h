# Assistente 24h

Assistente pessoal em Python, com funcionamento continuo, focado em produtividade e rotina.
Atualmente o projeto oferece:

- gerenciamento de lembretes por agendamento (cron)
- controle de calorias por refeicao
- configuracao de perfil do assistente e do usuario
- atendimento via chat no terminal ou webhook HTTP

## Funcionalidades Atuais

### 1) Lembretes e tarefas agendadas

- Cadastro de tarefas com expressao cron.
- Execucao automatica via scheduler.
- Controle de ativacao, limite de execucoes e contagem de execucoes.

### 2) Controle de calorias

- Registro de alimento e calorias consumidas.
- Consulta de totais e historico.
- Consulta por data especifica.
- Atualizacao de registros existentes.

### 3) Configuracao do assistente

- Nome e personalidade do assistente.
- Nome do usuario e nome preferido para tratamento.
- Idioma, fuso horario e humor atual.

### 4) Data e hora atual

- Ferramenta interna para leitura de data/hora (util no contexto das respostas).

## Arquitetura (resumo)

- `main.py`: ponto de entrada da aplicacao.
- `assistant/`: regras de IA e ferramentas (tools) do agente.
- `assistant/on_first_run.py`: onboarding da primeira execucao para configurar parametros iniciais.
- `services/webhook.py`: API HTTP com FastAPI.
- `services/cron.py`: scheduler de tarefas com APScheduler.
- `database_utils/`: criacao e inicializacao dos bancos SQLite.
- `assistant/*_tools.py`: logicas de leitura e escrita direto no banco.
- `databases/`: diretorio padrao dos arquivos SQLite.

Bancos utilizados:

- `assistant.db`
- `cron.db`
- `calories.db`

## Requisitos

- Python 3.11+ (recomendado)
- Chave de API do modelo Gemini

Dependencias do projeto estao no arquivo:

- `requiriments`

## Configuracao de ambiente

Crie um arquivo `.env` com base no `.env.example`:

```env
GOOGLE_API_KEY=sua_chave_aqui
DB_PATH=databases
WEBHOOK_TOKEN=um_token_seguro
ASSISTANT_MODE=
EVOLUTION_SEND_MESSAGE_ENDPOINT=http://72.61.41.33:63186/
EVOLUTION_API_TOKEN=
EVOLUTION_INSTANCE_NAME=
EVOLUTION_TARGET_NUMBER=5519982870602
EVOLUTION_PROCESSED_RETENTION_DAYS=30
```

Significado das variaveis:

- `GOOGLE_API_KEY`: chave de acesso ao provedor do modelo.
- `DB_PATH`: pasta onde os bancos SQLite serao criados.
- `WEBHOOK_TOKEN`: token obrigatorio para autenticar no endpoint HTTP.
- `ASSISTANT_MODE`: controla o modo de execucao. `TERMINAL_CHAT` roda chat no terminal e `WHATSAPP` usa o webhook do Evolution.
- `EVOLUTION_SEND_MESSAGE_ENDPOINT`: endpoint de envio do Evolution. Pode ser a rota completa (ex.: `http://host:8080/message/sendText/{instanceName}`) ou apenas a base (ex.: `http://host:8080`).
- `EVOLUTION_API_TOKEN`: token de autenticacao usado no envio de mensagens para o Evolution API.
- `EVOLUTION_INSTANCE_NAME`: nome da instancia usada quando o endpoint informado nao inclui a rota completa com `sendText`.
- `EVOLUTION_TARGET_NUMBER`: numero padrao (somente digitos) para testes de envio do assistente.
- `EVOLUTION_PROCESSED_RETENTION_DAYS`: quantidade de dias para manter os IDs de mensagens processadas no SQLite (evita reprocessar duplicados).

## Como executar

### 1) Criar e ativar ambiente virtual

No Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No Windows (Git Bash):

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 2) Instalar dependencias

```bash
pip install -r requiriments
```

### 3) Rodar a aplicacao

```bash
python main.py
```

## Modos de execucao

### Modo terminal

Defina no `.env`:

```env
ASSISTANT_MODE=TERMINAL_CHAT
```

Nesse modo, o assistente roda em chat local no terminal.

### Modo servicos (padrao)

Se `ASSISTANT_MODE` estiver vazio (ou diferente de `TERMINAL_CHAT`), o sistema inicia:

- scheduler de tarefas (cron)
- webhook HTTP em `http://127.0.0.1:8000` (quando `ASSISTANT_MODE` nao for `WHATSAPP`)
- webhook Evolution em `http://127.0.0.1:8001/evolution/webhook` (quando `ASSISTANT_MODE=WHATSAPP`)

## Webhook HTTP

Endpoint:

- `POST /send_message`

Autenticacao:

- query param `token` deve ser igual ao `WEBHOOK_TOKEN` do `.env`

Body JSON:

```json
{
	"message": "Qual e minha agenda de hoje?"
}
```

Exemplo com curl:

```bash
curl -X POST "http://127.0.0.1:8000/send_message?token=SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Oi, o que tenho para hoje?"}'
```

## Webhook Evolution (WhatsApp)

Para ativar, defina no `.env`:

```env
ASSISTANT_MODE=WHATSAPP
EVOLUTION_SEND_MESSAGE_ENDPOINT=http://72.61.41.33:63186/
EVOLUTION_API_TOKEN=seu_token_do_evolution
EVOLUTION_INSTANCE_NAME=minha_instancia
EVOLUTION_TARGET_NUMBER=5519982870602
EVOLUTION_PROCESSED_RETENTION_DAYS=30
```

Endpoint local para receber eventos do Evolution:

- `POST /evolution/webhook`

Autenticacao:

- query param `token` deve ser igual ao `WEBHOOK_TOKEN` do `.env`

Observacao:

- Mensagens recebidas sao deduplicadas por ID e salvas em SQLite em `databases/evolution.db` para evitar processar o mesmo evento mais de uma vez.

## Lembretes (cron)

As tarefas usam expressoes cron no formato padrao de 5 campos:

```text
minuto hora dia_do_mes mes dia_da_semana
```

Exemplo:

- `0 9 * * *` -> executa todos os dias as 09:00.

## Estrutura de pastas

```text
assistente-24h/
├─ main.py
├─ requiriments
├─ .env.example
├─ assistant/
├─ services/
├─ database_utils/
└─ databases/
```
