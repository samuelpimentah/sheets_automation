import os
from dotenv import load_dotenv

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