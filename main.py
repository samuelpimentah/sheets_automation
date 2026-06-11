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
    FASE 1: Procura por atualizações recentes nas listas do ClickUp, corrige
    divergências e adiciona tarefas totalmente novas criadas direto na nuvem.
    Retorna o DataFrame atualizado.
    """
    print(f"\n{GREEN}=== FASE 1: INICIANDO FLUXO REVERSO (CLICKUP -> SHEETS) ==={RESET}")

    priority_map = {1: "Urgente", 2: "Alta", 3: "Normal", 4: "Baixa"}
    subject_map = {
        "banco de dados": "Banco de dados",
        "inteligência artificial": "Inteligência artificial"
    }

    all_clickup_tasks = {}

    # Busca as tarefas de todas as listas registadas no arquivo de configuração
    for subject_name, list_id in LISTS_IDS.items():
        if not list_id:
            continue
        print(f"Procurando atualizações na lista do ClickUp: '{subject_name}'...")
        raw_tasks = get_clickup_list_tasks(list_id=list_id, api_key=API_KEY)
        cleaned_tasks = get_cleaned_tasks(raw_tasks)

        for task in cleaned_tasks:
            task["subject_context"] = subject_name
            all_clickup_tasks[task["clickup_id"]] = task

    print(f"Total de tarefas ativas encontradas no ClickUp: {len(all_clickup_tasks)}")

    # Mapeia os IDs que já existem na planilha para identificar o que é novo
    existing_ids = set(sheet_df["ClickUp_ID"].dropna().astype(str).tolist())
    has_updates = False

    # 1. Atualiza tarefas já existentes linha por linha
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
                print(f"🔄 Divergência encontrada! Atualizando a linha da tarefa: '{remote_task['title']}'")

                sheet_df.at[index, "Tarefa"] = remote_task["title"]
                sheet_df.at[index, "Descrição"] = remote_task["description"]
                sheet_df.at[index, "Status"] = remote_task["status"]
                sheet_df.at[index, "Prioridade"] = mapped_priority
                sheet_df.at[index, "Responsável"] = remote_task["assignee"].capitalize() if remote_task[
                    "assignee"] else ""
                sheet_df.at[index, "Data de entrega"] = remote_task["due_date"]

                # Recalcula o Hash imediatamente para alinhar com o estado atual do ClickUp
                updated_row = sheet_df.loc[index]
                sheet_df.at[index, "Hash"] = generate_row_hash(updated_row)
                has_updates = True

    # 2. Identifica e adiciona tarefas completamente novas criadas direto no ClickUp
    new_rows_to_append = []
    for clickup_id, remote_task in all_clickup_tasks.items():
        if clickup_id not in existing_ids:
            print(f"➕ Nova tarefa remota encontrada no ClickUp! Adicionando à planilha: '{remote_task['title']}'")

            mapped_priority = priority_map.get(remote_task["priority_id"], "Normal")

            # Extrai o número da sprint baseado nas tags da tarefa
            sprint_number = ""
            for tag in remote_task.get("tags", []):
                if "sprint" in tag.lower():
                    parts = tag.lower().split()
                    if len(parts) > 1 and parts[1].isdigit():
                        sprint_number = int(parts[1])

            new_row_dict = {
                "ClickUp_ID": clickup_id,
                "Tarefa": remote_task["title"],
                "Responsável": remote_task["assignee"].capitalize() if remote_task["assignee"] else "",
                "Data de entrega": remote_task["due_date"],
                "Matéria": subject_map.get(remote_task["subject_context"], remote_task["subject_context"].capitalize()),
                "Sprint": sprint_number,
                "Descrição": remote_task["description"],
                "Status": remote_task["status"],
                "Prioridade": mapped_priority,
                "Hash": ""
            }

            # Calcula o Hash inicial para este novo registro de linha
            dummy_series = pd.Series(new_row_dict)
            new_row_dict["Hash"] = generate_row_hash(dummy_series)

            new_rows_to_append.append(new_row_dict)
            has_updates = True

    if new_rows_to_append:
        new_tasks_df = pd.DataFrame(new_rows_to_append)
        sheet_df = pd.concat([sheet_df, new_tasks_df], ignore_index=True)

    if has_updates:
        print(f"{GREEN}✓ Ciclo de fluxo reverso concluído com atualizações em memória.{RESET}")
    else:
        print(f"{GREEN}✓ O Google Sheets já estava totalmente sincronizado com o ClickUp.{RESET}")

    return sheet_df


def run_forward_sync(spread, sheet_df, sheet_name: str):
    """
    FASE 2: Varre a planilha à procura de novas linhas criadas manualmente
    ou modificações locais, enviando os dados atualizados para o ClickUp.
    """
    print(f"\n{GREEN}=== FASE 2: INICIANDO FLUXO DE IDA (SHEETS -> CLICKUP) ==={RESET}")

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
            # Se a tarefa existe mas o hash mudou, envia a atualização para a API
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
                    print(f"✓ Tarefa '{row['Tarefa']}' atualizada com sucesso no ClickUp.")
        else:
            # Cria uma tarefa totalmente nova no ClickUp
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
                print(f"➕ Tarefa '{row['Tarefa']}' criada com sucesso! ID no ClickUp: {task_id}")

    return sheet_df


def main():
    print("=== CONECTANDO AO ECOSSISTEMA DO GOOGLE ===")
    spreadsheet_name = "demandas"
    sheet_name = "demandas1o"

    spread, sheet = get_google_sheet_as_df(spreadsheet_name=spreadsheet_name, sheet_name=sheet_name)
    print(f"Total de linhas encontradas na planilha: {len(sheet)}")

    # Isola e limpa os dados ativos do ecossistema
    cleaned_df = get_cleaned_df(sheet)

    # 1. Executa a Fase do Fluxo Reverso (ClickUp -> DataFrame)
    working_df = run_reverse_sync(spread, cleaned_df, sheet_name)

    # 2. Executa a Fase do Fluxo de Ida (DataFrame -> ClickUp)
    final_df = run_forward_sync(spread, working_df, sheet_name)

    # 3. Grava o estado absoluto final de volta no Google Sheets em uma única operação segura
    print(f"\n{GREEN}=== FASE DE COMMIT: SALVANDO ALTERAÇÕES NO GOOGLE SHEETS ==={RESET}")
    try:
        spread.df_to_sheet(final_df, index=False, sheet=sheet_name, replace=True)
        print(f"{GREEN}✓ Sincronização bidirecional concluída com sucesso!{RESET}")
    except Exception as error:
        print(f"{RED}Erro crítico ao sobrescrever dados no Google Sheets: {error}{RESET}")


if __name__ == "__main__":
    main()