# coding: utf-8
import locale
import argparse
import csv
import pandas as pd
from datetime import datetime


def print_transaction(date, payee, account, category, amount):
    print("{} {}".format(date.strftime("%Y/%m/%d"), payee))
    print("    {0:<50}{1:.2f} EUR".format(category, amount))
    print("    {0}".format(account))
    print("")

def parse_money(money):
    return abs(locale.atof(money.replace(".", "")))

def main(gls_filename):
    with open(gls_filename, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        df_l = []
        for row in reader:
            if len(row) > 0 and row[0] == 'Bezeichnung Auftragskonto':
                df_l.append(row)
                continue

            if len(df_l) > 0 and len(row) == 0:
                break

            if len(df_l) > 0 and len(row[1]) > 0:
                df_l.append(row)

        df = pd.DataFrame(df_l[1:], columns=df_l[0])

    print('#### Added by GLS importer. Please check the transactions below very carefully.')

    for index, row in df.iterrows():
        if row["Valutadatum"] == '30.02.2022':
            row["Valutadatum"] = '28.02.2022'

        dt = datetime.strptime(row["Valutadatum"], "%d.%m.%Y")

        # from here we could literally print as is, or
        # add some business logic to automate certain workflows
        #
        # for now, I think we'll do the categories by hand

        money = parse_money(row['Betrag'])

        if row['Betrag'][0] == '-': # Outflow
            print_transaction(
                dt,
                row['Name Zahlungsbeteiligter'],
                'Assets:GLS Giro',
                'Expenses:TODO',
                money
            )
        else: # Haben = Income
            print_transaction(
                dt,
                row['Name Zahlungsbeteiligter'],
                'Income:TODO',
                'Assets:GLS Giro',
                money
            )


if __name__ == "__main__":
    locale.setlocale(locale.LC_NUMERIC, "de_DE")

    parser = argparse.ArgumentParser(
        description="Converts GLS Export to ledger output",
    )

    parser.add_argument(
        "-f", "--file", type=str, nargs="?", required=True, help="File to parse",
    )

    args = parser.parse_args()

    main(args.file)
