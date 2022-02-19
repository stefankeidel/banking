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
    with open(gls_filename, encoding='ISO-8859-1') as f:
        reader = csv.reader(f, delimiter=';')
        df_l = []
        for row in reader:
            if len(row) > 0 and row[0] == 'Buchungstag':
                df_l.append(row)
                continue

            if len(df_l) > 0 and len(row) == 0:
                break

            if len(df_l) > 0 and len(row[1]) > 0:
                df_l.append(row)

        df = pd.DataFrame(df_l[1:], columns=df_l[0])

    print('#### Added by GLS importer. Please check the transactions below very carefully.')

    for index, row in df.iterrows():
        if row["Valuta"] == '30.02.2021':
            row["Valuta"] = '28.02.2021'

        dt = datetime.strptime(row["Valuta"], "%d.%m.%Y")

        # from here we could literally print as is, or
        # add some business logic to automate certain workflows
        #
        # for now, I think we'll do the categories by hand

        if row['Soll/Haben'] == 'S': # Soll == Outflow
            print_transaction(
                dt,
                row['Zahlungsempfänger'],
                'Assets:GLS Giro',
                'Expenses:TODO',
                parse_money(row['Umsatz'])
            )
        elif row['Soll/Haben'] == 'H': # Haben = Income
            print_transaction(
                dt,
                row['Zahlungsempfänger'],
                'Income:TODO',
                'Assets:GLS Giro',
                parse_money(row['Umsatz'])
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
