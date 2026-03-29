import sys

from database_utils.assistant_database_utils import (
    DEFAULT_ASSISTANT_CONFIGURATION,
    has_assistant_configuration,
    save_initial_assistant_configuration,
)


def _prompt_configuration_value(label: str, default_value: str) -> str:
    while True:
        user_input = input(f"{label} (exemplo: {default_value}): ").strip()
        if user_input:
            return user_input
        if default_value:
            return default_value
        print("Valor nao pode ser vazio. Tente novamente.")


def setup_assistant_on_first_run() -> None:
    if has_assistant_configuration():
        return

    if not sys.stdin.isatty():
        raise RuntimeError(
            "Primeira configuracao do assistente requer terminal interativo. "
            "Execute uma vez em modo terminal para informar os parametros iniciais."
        )

    print("Primeira execucao detectada. Vamos configurar o assistente.")

    configuration = {
        "name": _prompt_configuration_value("Nome do assistente", DEFAULT_ASSISTANT_CONFIGURATION["name"]),
        "personality": _prompt_configuration_value("Personalidade do assistente", DEFAULT_ASSISTANT_CONFIGURATION["personality"]),
        "user_name": _prompt_configuration_value("Seu nome", DEFAULT_ASSISTANT_CONFIGURATION["user_name"]),
        "user_preferred_name": _prompt_configuration_value("Como devo te chamar", DEFAULT_ASSISTANT_CONFIGURATION["user_preferred_name"]),
        "language": _prompt_configuration_value("Idioma", DEFAULT_ASSISTANT_CONFIGURATION["language"]),
        "time_zone": _prompt_configuration_value("Fuso horario", DEFAULT_ASSISTANT_CONFIGURATION["time_zone"]),
        "current_mood": _prompt_configuration_value("Humor atual do assistente", DEFAULT_ASSISTANT_CONFIGURATION["current_mood"]),
    }

    save_initial_assistant_configuration(configuration)
    print("Configuracao inicial salva com sucesso.")
