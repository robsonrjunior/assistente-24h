import sqlite3
from database_utils.assistant_database_utils import (
	ASSISTANT_DB_PATH,
	ensure_assistant_database,
	initialize_assistant_database,
)

ASSISTANT_FIELDS = (
	"name",
	"personality",
	"user_name",
	"user_preferred_name",
	"language",
	"time_zone",
	"current_mood",
)

def _get_assistant_configuration() -> dict:
	ensure_assistant_database(ASSISTANT_DB_PATH)
	initialize_assistant_database(ASSISTANT_DB_PATH)
	connection = sqlite3.connect(ASSISTANT_DB_PATH)

	try:
		cursor = connection.cursor()
		cursor.execute(
			"SELECT name, personality, user_name, user_preferred_name, language, time_zone, current_mood FROM assistant WHERE rowid = 1"
		)
		row = cursor.fetchone()
		if not row:
			return {}

		return dict(zip(ASSISTANT_FIELDS, row))
	finally:
		connection.close()


def _save_assistant_configuration(configuration: dict) -> None:
	ensure_assistant_database(ASSISTANT_DB_PATH)
	initialize_assistant_database(ASSISTANT_DB_PATH)
	connection = sqlite3.connect(ASSISTANT_DB_PATH)

	try:
		cursor = connection.cursor()
		cursor.execute(
			"""
			UPDATE assistant
			SET name = ?, personality = ?, user_name = ?, user_preferred_name = ?, language = ?, time_zone = ?, current_mood = ?, last_interaction_at = CURRENT_TIMESTAMP
			WHERE rowid = 1
			""",
			(
				configuration["name"],
				configuration["personality"],
				configuration["user_name"],
				configuration["user_preferred_name"],
				configuration["language"],
				configuration["time_zone"],
				configuration["current_mood"],
			),
		)
		connection.commit()
	finally:
		connection.close()


def _normalize_text(field_name: str, value: str) -> str:
	normalized_value = value.strip()
	if not normalized_value:
		raise ValueError(f"{field_name} não pode estar vazio")
	return normalized_value


def _update_assistant_field(field_name: str, value: str, success_message: str) -> dict:
	assistant_info = _get_assistant_configuration()
	if not assistant_info:
		raise ValueError("Configuração do assistente não encontrada")

	updated_value = _normalize_text(field_name=field_name, value=value)
	updated_info = {**assistant_info, field_name: updated_value}

	_save_assistant_configuration(updated_info)

	return {
		"message": success_message,
		field_name: updated_value,
	}


def update_assistant_name(name: str) -> dict:
	"""Updates the assistant name."""
	return _update_assistant_field(
		field_name="name",
		value=name,
		success_message="Nome do assistente atualizado com sucesso",
	)


def update_assistant_personality(personality: str) -> dict:
	"""Updates the assistant personality."""
	return _update_assistant_field(
		field_name="personality",
		value=personality,
		success_message="Personalidade do assistente atualizada com sucesso",
	)


def update_user_name(user_name: str) -> dict:
	"""Updates the user name."""
	return _update_assistant_field(
		field_name="user_name",
		value=user_name,
		success_message="Nome do usuário atualizado com sucesso",
	)


def update_user_preferred_name(user_preferred_name: str) -> dict:
	"""Updates how the assistant should address the user."""
	return _update_assistant_field(
		field_name="user_preferred_name",
		value=user_preferred_name,
		success_message="Nome preferido do usuário atualizado com sucesso",
	)


def update_assistant_language(language: str) -> dict:
	"""Updates the user's preferred language."""
	return _update_assistant_field(
		field_name="language",
		value=language,
		success_message="Idioma do assistente atualizado com sucesso",
	)


def update_assistant_time_zone(time_zone: str) -> dict:
	"""Updates the time zone used by the assistant."""
	return _update_assistant_field(
		field_name="time_zone",
		value=time_zone,
		success_message="Fuso horário do assistente atualizado com sucesso",
	)


def update_assistant_current_mood(current_mood: str) -> dict:
	"""Updates the assistant's current mood."""
	return _update_assistant_field(
		field_name="current_mood",
		value=current_mood,
		success_message="Humor do assistente atualizado com sucesso",
	)


def get_assistant_configuration() -> dict:
	"""Returns the current assistant configuration."""
	assistant_info = _get_assistant_configuration()
	if not assistant_info:
		raise ValueError("Configuração do assistente não encontrada")
	return assistant_info


tools = [
	update_assistant_name,
	update_assistant_personality,
	update_user_name,
	update_user_preferred_name,
	update_assistant_language,
	update_assistant_time_zone,
	update_assistant_current_mood,
	get_assistant_configuration,
]
