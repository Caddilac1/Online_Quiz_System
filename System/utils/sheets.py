import gspread
from google.oauth2.service_account import Credentials
from django.conf import settings

from System.models import Question, QuestionBank

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_gspread_client():
    creds = Credentials.from_service_account_file(
        settings.GOOGLE_SHEET_CREDENTIALS,
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def create_and_share_sheet(sheet_title):
    try:
        gc = get_gspread_client()

        # Create the sheet in your specific Drive folder
        spreadsheet = gc.create(sheet_title, folder_id='1UtPc7TcIv7nWtb8QQ6Hk9SUknzXpyrul')

        # Share with a single hardcoded email
        spreadsheet.share('nabaradirector@gmail.com', perm_type='user', role='writer')

        return spreadsheet.url

    except Exception as e:
        print(f"❌ Error creating or sharing sheet: {e}")
        return None


def import_questions_from_sheet(sheet_id, course, created_by):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.get_worksheet(0)  # First worksheet
        rows = worksheet.get_all_values()[1:]  # Skip header row

        bank, _ = QuestionBank.objects.get_or_create(
            course=course,
            is_general=False,
            created_by=created_by,
            title=f"{course.code} Questions from Sheet"
        )

        imported_count = 0
        for row in rows:
            if len(row) < 6:
                continue

            try:
                Question.objects.create(
                    bank=bank,
                    text=row[0],
                    option_a=row[1],
                    option_b=row[2],
                    option_c=row[3],
                    option_d=row[4],
                    correct_option=row[5].strip().upper(),
                    tag=row[6] if len(row) > 6 else ''
                )
                imported_count += 1
            except Exception as e:
                print(f"⚠️ Could not import row: {row} | Error: {e}")
                continue

        return imported_count

    except Exception as e:
        print(f"❌ Error importing questions from sheet: {e}")
        return 0
