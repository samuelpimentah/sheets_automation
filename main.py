import pandas as pd
from dotenv import load_dotenv
import os
from cleaner import generate_row_hash, get_cleaned_df
from clickup import build_base_request, create_clickup_task, update_clickup_task
from colors import GREEN, RED, RESET

def main():
    sheet: pd.DataFrame = pd.read_excel("demandas.xlsx")

    print(f"{GREEN}=== DADOS ORIGINAIS ==={RESET}")
    print(f"Total de linhas: {len(sheet)}")
    print(sheet)
    print(f"\n{GREEN}=== DADOS APÓS LIMPEZA ==={RESET}")

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
                print(f"{GREEN}[Ignorado] Tarefa '{row['Tarefa']}' não sofreu alterações no Excel.{RESET}")
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
    print(f"{GREEN}Gravando os novos IDs gerados e Hash de volta no arquivo Excel...{RESET}")

    try:
        df_sheet.to_excel("demandas.xlsx", index=False)
        print(f"{GREEN}Arquivo 'demandas.xlsx' atualizado e salvo com sucesso!{RESET}")
    except Exception as e:
        print(f"{RED}Erro ao tentar gravar dados: {e}{RESET}")

if __name__ == "__main__":
    main()