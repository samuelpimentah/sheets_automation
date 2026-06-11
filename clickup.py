import pandas as pd
import requests
from colors import RED, RESET
from config import PRIORITIES

def build_base_request(
    title: str,
    description: str,
    due_date: str,
    status: str,
    priority: str,
    api_key: str,
) -> list[dict] | None:
    """Função que se conecta à API do ClickUp e gera o payload padrão para criar ou atualizar task"""

    priority_id = int(PRIORITIES[priority.lower()]) if priority.lower() in PRIORITIES.keys() else -1
    due_date_ms = int(pd.to_datetime(due_date).timestamp() * 1000) if due_date else None

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key
    }

    payload = {
        "name": title,
        "description": description,
        "status": status,
        "priority": priority_id,
        "due_date": due_date_ms
    }

    return [headers, payload]

def create_clickup_task(
    base_payload: dict,
    headers: dict,
    assignee: str,
    sprint: int,
    subject: str,
    lists_ids: dict,
    members_ids: dict,
) -> str | None:
    """
    Função híbrida para criar (POST) uma task no ClickUp.
    Retorna o ID da tarefa processada.
    """

    list_id = int(lists_ids[subject.lower()]) if subject.lower() in lists_ids.keys() else None
    assignee_id = int(members_ids[assignee.lower()]) if assignee.lower() in members_ids.keys() else None

    if list_id is not None:
        url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
    else:
        print(f"{RED}Board não encontrado para a matéria: {subject}{RESET}")
        return None

    # Campos exclusivos de criação
    base_payload["assignees"] = [assignee_id] if assignee_id else []
    base_payload["tags"] = [f"sprint {sprint}"] if sprint else []

    response = requests.post(url, json=base_payload, headers=headers)

    if response.status_code in [200, 201]:
        task_data = response.json()
        return task_data["id"]
    else:
        raise ValueError(f"{RED}Erro ao criar tarefa: {response.status_code} - {response.text}{RESET}")


def update_clickup_task(
        base_payload: dict,
        headers: dict,
        task_id: str,
        assignee: str,
        sprint: int,
        members_ids: dict,
) -> bool:
    """
    Atualiza (PUT) uma tarefa existente no ClickUp com base no ID gerado pelo ClickUp
    """
    url_task = f"https://api.clickup.com/api/v2/task/{task_id}"

    assignee_id = int(members_ids[assignee.lower()]) if assignee.lower() in members_ids.keys() else None

    if assignee_id:
        all_members_ids = [int(member_id) for member_id in members_ids.values()]
        ids_to_remove = [member_id for member_id in all_members_ids if member_id != assignee_id]

        base_payload["assignees"] = {
            "add": [assignee_id],
            "removes": ids_to_remove
        }

    response = requests.put(url_task, json=base_payload, headers=headers)

    if response.status_code not in [200, 201]:
        raise ValueError(f"{RED}Erro ao atualizar task {task_id}: {response.status_code} - {response.text}{RESET}")

    if sprint:
        tag_name = f"sprint {sprint}"
        url_tag = f"https://api.clickup.com/api/v2/task/{task_id}/tag/{tag_name}"

        response_tag = requests.post(url_tag, headers=headers)

        if response_tag.status_code not in [200, 201]:
            print(f"{RED}Os dados mudaram, mas não foi possível adicionar a tag '{tag_name}' na tarefa {task_id}.{RESET}")

    return True

def get_clickup_list_tasks(list_id: str, api_key: str) -> list[dict]:
    """Busca os detalhes de uma tarefa específica do ClickUp."""

    url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    query_params = {
        "archived": "false",
        "include_markdown_description": "false"
    }

    response = requests.get(url, headers=headers, params=query_params)

    if response.status_code == 200:
        return response.json().get("tasks", [])
    else:
        print(f"{RED}Erro ao tentar receber as tarefas do ClickUp: {response.status_code} - {response.text}{RESET}")
        return []


def get_cleaned_tasks(tasks: list[dict]) -> list[dict]:
    """Recebe o json da resposta da API e separa apenas os dados úteis para o Sheets"""
    cleaned_tasks: list[dict] = []

    for task in tasks:
        priority_data = task.get("priority")
        priority_id = int(priority_data["id"]) if priority_data and priority_data.get("id") else None

        due_date_raw = task.get("due_date")
        formatted_date = ""
        if due_date_raw:
            formatted_date = pd.to_datetime(due_date_raw, unit='ms').strftime('%Y-%m-%d')

        assignees = task.get("assignees", [])
        primary_assignee = assignees[0]["username"] if assignees else ""

        cleaned_task = {
            "clickup_id": task.get("id"),
            "title": task.get("name", ""),
            "description": task.get("description", ""),
            "status": task["status"]["status"].capitalize() if task.get("status") else "",
            "priority_id": priority_id,
            "due_date": formatted_date,
            "assignee": primary_assignee
        }
        cleaned_tasks.append(cleaned_task)

    return cleaned_tasks
