import os

import gspread
from google.oauth2.service_account import Credentials

filename = os.path.join(os.path.dirname(__file__),
                        "Credentials", "google.json")

if not filename:
    raise RuntimeError(
        "Defina a variável GOOGLE_APPLICATION_CREDENTIALS com o caminho do JSON")

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    filename=filename,
    scopes=scopes,  # type: ignore
)

client = gspread.authorize(creds)  # type: ignore

spreadsheet = client.open("leiloes_com_lances").get_worksheet(0)


def find_row_by_link(link):
    links_column = spreadsheet.col_values(4)

    for index, value in enumerate(links_column, start=1):
        if value == link:
            return index

    return None


def upsert_line(data):

    row = [
        str(data["titulo"]),
        str(data["ultimo_lance"]),
        int(data["quantidade_lances"]),
        str(data["link"]),
        str(data["usuario"]),
        str(data["tempo_restante"]),
        data["data_coleta"].strftime("%d/%m/%Y")
    ]
    row_number = find_row_by_link(data["link"])

    if row_number:
        spreadsheet.update(f"A{row_number}:G{row_number}", [
                           row])  # type: ignore
        print("Atualizou:", data["titulo"])

    else:
        spreadsheet.append_row(
            row, value_input_option="USER_ENTERED")  # type: ignore
        print("Criou:", data["titulo"])
        print("Criou:", data["titulo"])
