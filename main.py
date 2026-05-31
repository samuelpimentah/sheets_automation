import pandas as pd
from dotenv import load_dotenv
import os
from cleaner import get_cleaned_df
from clickup import create_clickup_task

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

    for _, row in df_sheet.iterrows():
        try:
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
                print(api_success)
            else:
                print(f"Falha lógica ao tentar criar: '{row['Tarefa']}'")
        except Exception as e:
            print(f"Erro crítico na tarefa '{row['Tarefa']}': {e}")

if __name__ == "__main__":
    main()