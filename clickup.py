import pandas as pd
import requests

def create_clickup_task(
    title: str,
    description: str,
    due_date: str,
    status: str,
    priority: str,
    assignee: str,
    sprint: int,
    subject: str,
    api_key: str,
    lists_ids: dict,
    members_ids: dict,
) -> str | None:
    """
    Função para criar uma tarefa no ClickUp usando a API
    """

    priorities = {
        "baixa": 4,
        "média": 3,
        "alta": 2,
        "urgente": 1
    }

    list_id = int(lists_ids[subject.lower()]) if subject.lower() in lists_ids.keys() else None

    if list_id is not None:
        url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
    else:
        print("Board não encontrado.")
        return None

    assignee_id = int(members_ids[assignee.lower()]) if assignee.lower() in members_ids.keys() else None
    priority_id = int(priorities[priority.lower()]) if priority.lower() in priorities.keys() else -1
    due_date_ms = int(pd.to_datetime(due_date).timestamp() * 1000) if due_date else None

    payload = {
        "name": title,
        "description": description,
        "assignees": [assignee_id] if assignee_id else [],
        "status": status,
        "priority": priority_id,
        "due_date": due_date_ms,
        "tags": [f"sprint {sprint}"],
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        task_data = response.json()
        return task_data["id"]
    else:
        raise ValueError(f"Erro ao criar tarefa: {response.status_code} - {response.text}")