#!/usr/bin/python


import sys
import getopt
import os
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import proteosafe_summary_library

def usage():
    print "<json auth key> <spreadsheet key>"

def main():
    json_key = json.load(open(sys.argv[1]))
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
    gc = gspread.authorize(credentials)

    sht1 = gc.open_by_key(sys.argv[2])

    worksheet = sht1.worksheet("Sheet1")

    #Looping through first column until we find something empty
    columns_list = worksheet.col_values(1)
    for i in range(1, len(columns_list)):
        task_id = columns_list[i]
        if len(task_id) > 0:
            val = worksheet.cell(i+1, 1).value
            total_psms = proteosafe_summary_library.count(task_id, "group_by_spectrum", {})

            worksheet.update_cell(i+1, 2, total_psms)






if __name__ == "__main__":
    main()
