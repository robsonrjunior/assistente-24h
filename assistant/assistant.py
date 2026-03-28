import os
from typing import Any
from deepagents import create_deep_agent
from dotenv import load_dotenv
import assistant.assistant_tools
import assistant.calories_tools
import assistant.cron_tools
import assistant.datetime_tools

load_dotenv()

AGENT_TOOLS = [
    *assistant.assistant_tools.tools,
    *assistant.calories_tools.tools,
    *assistant.cron_tools.tools,
    *assistant.datetime_tools.tools,
]

def _get_answer(agent_result: Any) -> str:
    """Extracts the answer text from the agent result."""
    return agent_result["messages"][-1].content[0].get("text", "")

def create_system_prompt() -> str:
    """
    Creates a system prompt for the assistant.
    Returns:
        str: The system prompt.
    """
    assistant_info = assistant.assistant_tools.get_assistant_configuration()
    system_prompt = "Você é um assistente pessoal."

    if assistant_info:
        system_prompt += f"\nSeu nome é: {assistant_info['name']}."
        system_prompt += f"\nSua personalidade é: {assistant_info['personality']}."
        system_prompt += f"\nO nome do usuário é: {assistant_info['user_name']}."
        system_prompt += f"\nChame o usuário como: {assistant_info['user_preferred_name']}."
        system_prompt += f"\nO idioma do usuário é: {assistant_info['language']}."
        system_prompt += f"\nUse o seguinte fuso horário: {assistant_info['time_zone']}."
        system_prompt += f"\nSeu humor atual é: {assistant_info['current_mood']}."

    return system_prompt

def answer_question(question: str) -> str:
    """
    Uses the Tavily API to answer a question.
    Args:
        question (str): The question to be answered.
    Returns:
        str: The answer to the question.
    """
    system_prompt = create_system_prompt()

    agent = create_deep_agent(
        model="google_genai:gemini-3.1-pro-preview",
        tools=AGENT_TOOLS,
        system_prompt=system_prompt,
    )
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    return _get_answer(result)

def execute_task(task_id: int) -> str:
    """
    Executes a task using the Tavily API.
    Args:
        task_id (int): The ID of the task to be executed.
    Returns:
        str: The result of the task execution.
    """
    task = assistant.cron_tools.get_cron_record(task_id)
    if not task:
        return f"Tarefa com id {task_id} não encontrada."

    system_prompt = create_system_prompt()
    agent = create_deep_agent(
        model="google_genai:gemini-3.1-pro-preview",
        tools=AGENT_TOOLS,
        system_prompt=system_prompt,
    )
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"Execute a tarefa '{task.name}': {task.description}",
                }
            ]
        }
    )
    return _get_answer(result)