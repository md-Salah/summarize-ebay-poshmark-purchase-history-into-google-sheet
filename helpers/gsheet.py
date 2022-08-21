import gspread
from helpers.files import read_contact_info

def gsheet():
    info = read_contact_info('inputs/gsheet_info.txt', '=')
    sa = gspread.service_account(filename=info['json_filename'])

    file = sa.open(info['sheet_name'])
    worksheet = file.worksheet(info['sheet_tab_name'])

    return worksheet

    # print(worksheet.get_all_values())
    # worksheet.insert_rows()