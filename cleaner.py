import pandas as pd
import numpy as np
import hashlib

def generate_row_hash(row: pd.Series) -> str:
    """
    Gera uma assinatura digital única (MD5) baseada nos valores atuais da linha.
    Se qualquer um desses valores mudar no Excel, o Hash mudará.
    """
    texto_linha = (
        f"{row['Tarefa']}"
        f"{row['Descrição']}"
        f"{row['Status']}"
        f"{row['Prioridade']}"
        f"{row['Responsável']}"
        f"{row['Data de entrega']}"
        f"{row['Sprint']}"
    )
    return hashlib.md5(texto_linha.encode('utf-8')).hexdigest()

def get_cleaned_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Função para limpar o DataFrame, removendo linhas com valores vazios ou nulos, exceto na coluna 'descrição'
    OBS.: Em breve, 'descrição' nula será preenchida por um agente
    """
    cleaned_df: pd.DataFrame = df.replace(r'^\s*$', np.nan, regex=True)

    for column in cleaned_df.columns:
        if cleaned_df[column].dtype == 'string':  # string/text columns
            cleaned_df[column] = cleaned_df[column].str.strip()

    useless_rows = []

    for i, row in cleaned_df.iterrows():
        for column in cleaned_df.columns:
            if column.lower() not in ['descrição', 'sprint', 'clickup_id', 'hash'] and pd.isna(row[column]):
                useless_rows.append(i)
                break

    cleaned_df = cleaned_df.drop(useless_rows)
    cleaned_df = cleaned_df.replace({np.nan: None})

    return cleaned_df