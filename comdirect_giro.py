#!/usr/bin/env python
# coding: utf-8

import argparse
import csv
from datetime import datetime
import re
import locale


def print_transaction(record):
    print("{} * {}".format(
        record['date'].strftime("%Y/%m/%d"),
        record['payee']
    ))
    print("    {0}{1:38.2f} EUR".format("<category>", record['money']))
    print("    {0}".format("Assets:Comdirect Giro"))


if __name__ == '__main__':
    locale.setlocale(locale.LC_NUMERIC, "de_DE")

    parser = argparse.ArgumentParser(
        description='Parse CSV export from comdirect giro and output in Ledger format'
    )

    parser.add_argument(
        '-f',
        '--file',
        type=str,
        help='Filepath for export file'
    )

    extractor_ueberweisung = re.compile("[\s]*(Empfänger):[\s]*(.+)(Kto\/IBAN)")
    extractor_others = re.compile("[\s]*(Auftraggeber):[\s]*(.*)(Buchungstext:)")

    args = parser.parse_args()

    with open(args.file, encoding='latin-1') as csvfile:
        bankreader = csv.reader(csvfile, delimiter=';')
        for row in bankreader:
            # the first couple of rows have a summary or are empty
            if bankreader.line_num < 6:
                continue

            # catch last row and further empty rows
            if len(row) < 1 or row[0] == 'Alter Kontostand':
                continue

            # from here on out we should only have actual transactions

            # parse date
            dt = datetime.strptime(row[1], '%d.%m.%Y')  # valuta

            # parse payee/creditor
            if row[2] == 'Übertrag / Überweisung':
                result = extractor_ueberweisung.search(row[3])
            else:
                result = extractor_others.search(row[3])

            record = {
                'date': dt,
                'payee': result.group(2),
                'money': abs(locale.atof(row[4].replace('.', '')))  # caveman parsing
            }

            print_transaction(record)
