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
            if column.lower() not in ['descrição', 'sprint', 'clickup_id'] and pd.isna(row[column]):
                useless_rows.append(i)
                break

    cleaned_df = cleaned_df.drop(useless_rows)
    cleaned_df = cleaned_df.replace({np.nan: None})

    return cleaned_df