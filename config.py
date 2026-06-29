import os
from typing import Any

from dotenv import load_dotenv
from gspread_pandas import Spread
from google.oauth2.service_account import Credentials

load_dotenv()

PRIORITIES = {
    "baixa": 4,
    "normal": 3,
    "alta": 2,
    "urgente": 1
}

API_KEY = os.getenv("CLICKUP_API_KEY")

MEMBERS_IDS = {
    "ana": os.getenv("ANA_MEMBER_ID"),
    "davi": os.getenv("DAVI_MEMBER_ID"),
    "joão": os.getenv("JOAO_MEMBER_ID"),
    "mariana": os.getenv("MARIANA_MEMBER_ID"),
    "rahquel": os.getenv("RAHQUEL_MEMBER_ID"),
    "samuel": os.getenv("SAMUEL_MEMBER_ID")
}

LISTS_IDS = {
    "MODELAGEM": os.getenv("MODELAGEM_BOARD_ID"),
    "BD2": os.getenv("BD2_BOARD_ID"),
    "IA2": os.getenv("IA2_BOARD_ID"),
    "BI": os.getenv("BI_BOARD_ID"),
    "DEVOPS": os.getenv("DEVOPS_BOARD_ID"),
    "EQS": os.getenv("EQS_BOARD_ID"),
    "DS2": os.getenv("DS2_BOARD_ID"),
    "DAD": os.getenv("DAD_BOARD_ID"),
    "MOBILE": os.getenv("MOBILE_BOARD_ID"),
    "UX2": os.getenv("UX2_BOARD_ID"),
}

def get_google_sheet_as_df(spreadsheet_name: str, sheet_name: str) -> Spread | Any:
    """
    Conecta ao Google Sheets usando o arquivo credenciais.json e
    retorna um objeto 'Spread' e o DataFrame do Pandas pronto.
    """
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    spread = Spread(spreadsheet_name, creds=credentials)

    df = spread.sheet_to_df(sheet=sheet_name, index=None)
    df = df.reset_index(drop=True)

    return spread, df