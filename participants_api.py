from apiclient import discovery
from google.oauth2 import service_account

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets",
]
SECRET_FILE = "participants-api.json"
SPREADSHEET_ID = "1Ysgz_rL_xrx2FNUfQMnI4Oxc3sLo-Oi1c9WaTWWyZZc"
RANGE_NAME = "Sheet1!A:F"

HEADER = ["id", "email", "password", "displayName", "downloaded locus", "balance"]
ID = 0
EMAIL = 1
PASSWORD = 2
DISPLAY_NAME = 3
DOWNLOADED_LOCUS = 4
BALANCE = 5


class ParticipatsAPI:
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            SECRET_FILE, scopes=SCOPES
        )
        service = discovery.build("sheets", "v4", credentials=credentials)
        self.sheet = service.spreadsheets()

    def get_rows(self):
        result = (
            self.sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
            .execute()
        )
        return result.get("values", [])

    def get_authenticated_user(self, email, password):
        rows = self.get_rows()

        for row in rows:
            if row[EMAIL] == email:
                if row[PASSWORD] == password:
                    return {
                        "id": row[ID],
                        "email": row[EMAIL],
                        "displayName": row[DISPLAY_NAME],
                        "balance": row[BALANCE],
                    }
                else:
                    return {}
        return {}

    def get_balance(self, email):
        rows = self.get_rows()

        for row in rows:
            if row[EMAIL] == email:
                return row[BALANCE]

    def update_balance(self, email, amount):
        rows = self.get_rows()

        for row in rows:
            if row[EMAIL] == email:
                row[BALANCE] = int(row[BALANCE]) + amount
                break

        self.sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            body={"values": rows},
            range=RANGE_NAME,
            valueInputOption="USER_ENTERED",
        ).execute()
    
    def update_downloaded_locus(self, id_):
        rows = self.get_rows()

        for row in rows[1:]:
            if int(row[ID]) == int(id_):
                if row[DOWNLOADED_LOCUS] == "yes":
                    return
                else:
                    row[DOWNLOADED_LOCUS] = "yes"
                    row[BALANCE] = int(row[BALANCE]) + 10
                    break
        
        self.sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            body={"values": rows},
            range=RANGE_NAME,
            valueInputOption="USER_ENTERED",
        ).execute()




