import pandas as pd
import numpy as np
import requests
from numpy.f2py.auxfuncs import throw_error
from datetime import datetime
from dotenv import load_dotenv
import os

def get_cleaned_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Função para limpar o DataFrame, removendo linhas com valores vazios ou nulos, exceto na coluna 'descrição'
    OBS.: Em breve, 'descrição' nula será preenchida por um agente
    """
    cleaned_df: pd.DataFrame = df.replace(r'^\s*$', np.nan, regex=True)

    for column in cleaned_df.columns:
        if cleaned_df[column].dtype == 'string':
            cleaned_df[column] = cleaned_df[column].str.strip()

    useless_rows = []

    for i, row in cleaned_df.iterrows():
        for column in cleaned_df.columns:
            if column.lower() != 'descrição' and pd.isna(row[column]):
                useless_rows.append(i)
                break

    cleaned_df = cleaned_df.drop(useless_rows)

    return cleaned_df

def nan_to_none(value):
    return None if pd.isna(value) else value

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
) -> bool:
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
        return False

    assignee_id = int(members_ids[assignee.lower()]) if assignee.lower() in members_ids.keys() else None
    priority_id = int(priorities[priority.lower()]) if priority.lower() in priorities.keys() else -1
    due_date_ms = int(pd.to_datetime(due_date).timestamp() * 1000) if due_date else None

    payload = {
        "name": nan_to_none(title),
        "description": nan_to_none(description),
        "assignees": [assignee_id] if assignee_id else [],
        "status": nan_to_none(status),
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

    if response.status_code == 200:
        return True
    else:
        raise ValueError(f"Erro ao criar tarefa: {response.status_code} - {response.text}")

def main():
    sheet: pd.DataFrame = pd.read_excel("demandas.xlsx")

    print("=== DADOS ORIGINAIS ===")
    print(f"Total de linhas: {len(sheet)}")
    print(sheet)
    print("\n=== DADOS APÓS LIMPEZA ===")

    df_sheet = get_cleaned_df(sheet)
    print(f"Total de linhas: {len(df_sheet)}")
    print(df_sheet)

    load_dotenv()

    API_KEY = os.getenv("CLICKUP_API_KEY")

    MEMBERS_IDS = {
        "bruno": os.getenv("MEMBER_ID"),
        "gabriel": os.getenv("MEMBER_ID"),
        "pietra": os.getenv("MEMBER_ID")
    }

    LISTS_IDS = {
        "banco de dados": os.getenv("BD_LIST_ID"),
        "inteligência artificial": os.getenv("IA_LIST_ID")
    }

    try:
        for _, row in df_sheet.iterrows():
            api_success = create_clickup_task(
                title=row["Tarefa"],
                description=row["Descrição"],
                due_date=row["Data de entrega"],
                status=row["Status"],
                priority=row["Prioridade"],
                assignee=row["Responsável"],
                sprint=row["Sprint"],
                subject=row["Matéria"],
                api_key=API_KEY,
                lists_ids=LISTS_IDS,
                members_ids=MEMBERS_IDS
            )

            if api_success:
                print(f"Tarefa '{row['Tarefa']}' criada com sucesso!")
            else:
                print("Erro ao criar tarefa!")
    except Exception as e:
        print(f"Erro com a API: {e}")

if __name__ == "__main__":
    main()