#!/usr/bin/env python
# coding: utf-8

import argparse
import csv
from datetime import datetime
import re
import locale


def print_transaction(record):
    print("{} {}".format(
        record['date'].strftime("%Y/%m/%d"),
        record['payee']
    ))
    print("    {0}{1:38.2f} EUR".format("<category>", record['money']))
    print("    {0}".format("Assets:comdirect Giro"))
    print("")


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

    extractor_ueberweisung = re.compile("[\s]*(Empfänger):[\s]*(.+)(Kto\/IBAN|Ueberweisung)")
    extractor_kv = re.compile("[\s]*(Buchungstext:\s*)([A-Za-z]+)")
    extractor_others = re.compile("[\s]*(Auftraggeber):[\s]*(.*)(Buchungstext:)")
    extractor_others_no_text = re.compile("[\s]*(Auftraggeber):[\s]*(.*)(Buchungstext:)?")

    args = parser.parse_args()

    with open(args.file, encoding='latin-1') as csvfile:
        bankreader = csv.reader(csvfile, delimiter=';')
        for row in reversed(list(bankreader)):
            # catch last row and further empty rows
            if len(row) < 1 or row[0] == 'Alter Kontostand' or row[0] == 'offen':
                continue

            # this is the header row, at which point we will want to end this
            if row[0] == 'Buchungstag':
                break

            # from here on out we should only have actual transactions

            # parse date
            dt = datetime.strptime(row[1], '%d.%m.%Y')  # valuta

            # parse payee/creditor
            if row[2] == 'Übertrag / Überweisung':
                result = extractor_ueberweisung.search(row[3])
                if result is None:
                    # this is usually income or something, may want to treat it differently
                    result = extractor_others.search(row[3])

                if result is None:
                    result = extractor_others_no_text.search(row[3])

                if result is None:
                    result = extractor_kv.search(row[3])

                if result is None:
                    print(row)
                payee = result.group(2)
            elif row[2] == 'Auszahlung GAA':
                payee = 'Geldautomat'
            elif row[2] == 'Kartenverfügung':
                result = extractor_kv.search(row[3])
                payee = result.group(2)
            else:
                result = extractor_others.search(row[3])
                payee = result.group(2)

            record = {
                'date': dt,
                'payee': payee,
                'money': abs(locale.atof(row[4].replace('.', '')))  # caveman parsing
            }

            print_transaction(record)
