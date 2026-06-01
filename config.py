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
    "bruno": os.getenv("MEMBER_ID"),
    "gabriel": os.getenv("MEMBER_ID"),
    "pietra": os.getenv("MEMBER_ID")
}

LISTS_IDS = {
    "banco de dados": os.getenv("BD_LIST_ID"),
    "inteligência artificial": os.getenv("IA_LIST_ID")
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