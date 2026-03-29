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
```

Significado das variaveis:

- `GOOGLE_API_KEY`: chave de acesso ao provedor do modelo.
- `DB_PATH`: pasta onde os bancos SQLite serao criados.
- `WEBHOOK_TOKEN`: token obrigatorio para autenticar no endpoint HTTP.
- `ASSISTANT_MODE`: se for `TERMINAL_CHAT`, roda chat no terminal.

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
- webhook HTTP em `http://127.0.0.1:8000`

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
