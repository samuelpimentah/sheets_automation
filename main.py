from cleaner import generate_row_hash, get_cleaned_df
from clickup import build_base_request, create_clickup_task, update_clickup_task
from colors import GREEN, RED, RESET
from config import API_KEY, LISTS_IDS, MEMBERS_IDS, get_google_sheet_as_df

def main():
    print("=== CONECTANDO AO GOOGLE SHEETS ===")
    # Nome exato da sua planilha na nuvem e o nome da aba (Página1, etc)
    spreadsheet_name = "demandas"
    sheet_name = "demandas1o"

    spread, sheet = get_google_sheet_as_df(spreadsheet_name=spreadsheet_name, sheet_name=sheet_name)

    print(f"Total de linhas encontradas na nuvem: {len(sheet)}")

    print(f"{GREEN}=== DADOS ORIGINAIS ==={RESET}")
    print(f"Total de linhas: {len(sheet)}")
    print(sheet)
    print(f"\n{GREEN}=== DADOS APÓS LIMPEZA ==={RESET}")

    df_sheet = get_cleaned_df(sheet)
    print(f"Total de linhas: {len(df_sheet)}")
    print(df_sheet)

    for index, row in df_sheet.iterrows():
        headers, base_payload = build_base_request(
            title=row["Tarefa"],
            description=row["Descrição"],
            due_date=row["Data de entrega"],
            status=row["Status"],
            priority=row["Prioridade"],
            api_key=API_KEY
        )

        current_id: str = row["ClickUp_ID"]
        row_hash: str = row["Hash"]

        new_hash: str = generate_row_hash(row)

        if current_id:
            if row_hash and row_hash == new_hash:
                print(f"{GREEN}[Ignorado] Tarefa '{row['Tarefa']}' não sofreu alterações no Sheets.{RESET}")
                continue

            api_success = update_clickup_task(
                base_payload=base_payload,
                headers=headers,
                task_id=current_id,
                assignee=row["Responsável"],
                sprint=row["Sprint"],
                members_ids=MEMBERS_IDS
            )
            if api_success:
                df_sheet.at[index, "Hash"] = new_hash
                print(f"{GREEN}Tarefa '{row['Tarefa']}' atualizada com sucesso!{RESET}")
        else:
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
                df_sheet.at[index, "ClickUp_ID"] = task_id
                df_sheet.at[index, "Hash"] = new_hash
                print(f"{GREEN}Tarefa '{row['Tarefa']}' criada com sucesso! ID: {task_id}{RESET}")

    print(f"\n{GREEN}=== SINCRONIZAÇÃO CONCLUÍDA ==={RESET}")
    print(f"{GREEN}Gravando os novos IDs gerados e Hash de volta no Google Sheets...{RESET}")

    try:
        spread.df_to_sheet(df_sheet, index=False, sheet=sheet_name, replace=True)
        print("\n=== ALTERAÇÕES SALVAS DIRETO NO GOOGLE SHEETS ===")
    except Exception as e:
        print(f"{RED}Erro ao tentar gravar dados: {e}{RESET}")

if __name__ == "__main__":
    main()