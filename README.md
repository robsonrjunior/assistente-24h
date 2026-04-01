# Assistente 24h

Assistente pessoal em Python, com funcionamento continuo, focado em produtividade e rotina.
Atualmente o projeto oferece:

- gerenciamento de lembretes por agendamento (cron)
- controle de calorias por refeicao
- configuracao de perfil do assistente e do usuario
- atendimento via chat no terminal ou webhook WhatsApp (Evolution)

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
- `services/evolution_webhook.py`: API HTTP com FastAPI para eventos do Evolution.
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
