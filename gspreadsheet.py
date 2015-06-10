__author__ = 'jph'

import json
import time
import sys

import gspread
from oauth2client.client import SignedJwtAssertionCredentials


class Google_Spreadsheet2(object):
    def __init__(self, keyfile='spreadsheet.json', spreadsheet="Tradedata_raw"):
        json_key = json.load(open(keyfile))
        scope = ['https://spreadsheets.google.com/feeds']
        self.credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
        self.spreadsheet = spreadsheet
        self.login()
        self.cur_row = len(self.wks.col_values(1)) + 1

    def login(self):
        self.gc = gspread.authorize(self.credentials)
        self.wks = self.gc.open(self.spreadsheet).sheet1

    def write_log(self, *args):
        try:
            self.login()
            column = 1
            for arg in args:
                self.wks.update_cell(self.cur_row, column, arg)
                column += 1
                time.sleep(0.1)
            self.cur_row += 1
        except:
            e = sys.exc_info()[0]
            print "Error: %s" % e

