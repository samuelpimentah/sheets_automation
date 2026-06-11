import pandas as pd
from cleaner import generate_row_hash, get_cleaned_df
from clickup import (
    build_base_request,
    create_clickup_task,
    update_clickup_task,
    get_clickup_list_tasks,
    get_cleaned_tasks
)
from colors import GREEN, RED, RESET
from config import API_KEY, LISTS_IDS, MEMBERS_IDS, get_google_sheet_as_df


def run_reverse_sync(spread, sheet_df, sheet_name: str) -> pd.DataFrame:
    """
    FASE 1: Extrai as atualizações recentes das listas do ClickUp e sobrescreve os dados desatualizados da planilha.
    Retorna o DataFrame atualizado.
    """
    print(f"\n{GREEN}=== FASE 1: CLICKUP -> SHEETS ==={RESET}")

    priority_map = {1: "Urgente", 2: "Alta", 3: "Normal", 4: "Baixa"}
    all_clickup_tasks = {}

    # Fetch tasks from all registered ClickUp lists
    for subject_name, list_id in LISTS_IDS.items():
        if not list_id:
            continue
        print(f"Atualizando dados da Lista do ClickUp: '{subject_name}'...")
        raw_tasks = get_clickup_list_tasks(list_id=list_id, api_key=API_KEY)
        cleaned_tasks = get_cleaned_tasks(raw_tasks)

        for task in cleaned_tasks:
            all_clickup_tasks[task["clickup_id"]] = task

    print(f"Total de tarefas atualizadas: {len(all_clickup_tasks)}")
    has_updates = False

    # Check for differences row by row
    for index, row in sheet_df.iterrows():
        clickup_id = row["ClickUp_ID"]

        if clickup_id and clickup_id in all_clickup_tasks:
            remote_task = all_clickup_tasks[clickup_id]
            mapped_priority = priority_map.get(remote_task["priority_id"], "Normal")

            has_changed = (
                    row["Tarefa"] != remote_task["title"] or
                    row["Descrição"] != remote_task["description"] or
                    row["Status"] != remote_task["status"] or
                    row["Prioridade"] != mapped_priority or
                    row["Responsável"].lower() != remote_task["assignee"].lower() or
                    str(row["Data de entrega"]) != str(remote_task["due_date"])
            )

            if has_changed:
                print(f"Sincronizando atualizações do ClickUp no Sheets: '{remote_task['title']}'")

                sheet_df.at[index, "Tarefa"] = remote_task["title"]
                sheet_df.at[index, "Descrição"] = remote_task["description"]
                sheet_df.at[index, "Status"] = remote_task["status"]
                sheet_df.at[index, "Prioridade"] = mapped_priority
                sheet_df.at[index, "Responsável"] = remote_task["assignee"].capitalize()
                sheet_df.at[index, "Data de entrega"] = remote_task["due_date"]

                # Recalculate hash immediately to align with ClickUp's current state
                updated_row = sheet_df.loc[index]
                sheet_df.at[index, "Hash"] = generate_row_hash(updated_row)
                has_updates = True

    if has_updates:
        print(f"{GREEN}Sincronização ClickUp -> Sheets concluída.{RESET}")
    else:
        print(f"{GREEN}Google Sheets já estava de acordo com o board.{RESET}")

    return sheet_df


def run_forward_sync(spread, sheet_df, sheet_name: str):
    """
    FASE 2: Analisa novas linhas ou atualizações manuais locais dentro da planilha,
    e então envia as alterações para o ClickUp.
    """
    print(f"\n{GREEN}=== FASE 2: SHEETS -> CLICKUP ==={RESET}")

    # Process modifications or creations row by row
    for index, row in sheet_df.iterrows():
        headers, base_payload = build_base_request(
            title=row["Tarefa"],
            description=row["Descrição"],
            due_date=row["Data de entrega"],
            status=row["Status"],
            priority=row["Prioridade"],
            api_key=API_KEY
        )

        new_hash = generate_row_hash(row)
        current_id = row["ClickUp_ID"]
        old_hash = row["Hash"]

        if current_id:
            # If task exists but hash differs, push local update
            if old_hash != new_hash:
                api_success = update_clickup_task(
                    base_payload=base_payload,
                    headers=headers,
                    task_id=current_id,
                    assignee=row["Responsável"],
                    sprint=row["Sprint"],
                    members_ids=MEMBERS_IDS
                )
                if api_success:
                    sheet_df.at[index, "Hash"] = new_hash
                    print(f"Tarefa '{row['Tarefa']}' atualizada no ClickUp.")
        else:
            # Create new task
            task_id = create_clickup_task(
                base_payload=base_payload,
                headers=headers,
                assignee=row["Responsável"],
                sprint=row["Sprint"],
                subject=row["Matéria"],
                lists_ids=LISTS_IDS,
                members_ids=MEMBERS_IDS
            )
            if task_id:
                sheet_df.at[index, "ClickUp_ID"] = task_id
                sheet_df.at[index, "Hash"] = new_hash
                print(f"Tarefa '{row['Tarefa']}' criada com sucesso! ClickUp ID: {task_id}")

    return sheet_df


def main():
    print("=== CONECTANDO AO GOOGLE ===")
    spreadsheet_name = "demandas"
    sheet_name = "demandas1o"

    spread, sheet = get_google_sheet_as_df(spreadsheet_name=spreadsheet_name, sheet_name=sheet_name)
    print(f"Total de linhas no Google Sheets: {len(sheet)}")

    # Isolate and sanitize active ecosystem data
    cleaned_df = get_cleaned_df(sheet)

    # 1. Run Reverse Sync Phase
    working_df = run_reverse_sync(spread, cleaned_df, sheet_name)

    # 2. Run Forward Sync Phase
    final_df = run_forward_sync(spread, working_df, sheet_name)

    # 3. Save absolute state back to Google Sheets in a single safe database write
    print(f"\n{GREEN}=== SALVANDO TODAS AS ALTERAÇÕES NO SHEETS ==={RESET}")
    try:
        spread.df_to_sheet(final_df, index=False, sheet=sheet_name, replace=True)
        print(f"{GREEN}PROCESSO CONCLUÍDO!{RESET}")
    except Exception as error:
        print(f"{RED}ERRO AO CONCLUIR PROCESSO: {error}{RESET}")

if __name__ == "__main__":
    main()