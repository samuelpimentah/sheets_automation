import pandas as pd
import numpy as np

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

def main():
    sheet: pd.DataFrame = pd.read_excel("demandas.xlsx")

    print("=== DADOS ORIGINAIS ===")
    print(f"Total de linhas: {len(sheet)}")
    print(sheet)
    print("\n=== DADOS APÓS LIMPEZA ===")

    df_sheet = get_cleaned_df(sheet)
    print(f"Total de linhas: {len(df_sheet)}")
    print(df_sheet)

if __name__ == "__main__":
    main()