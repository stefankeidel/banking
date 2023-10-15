# coding: utf-8
import locale
import argparse
import pandas as pd
import numpy as np
from datetime import datetime


def print_transaction(date, payee, account, category, amount):
    print("{} {}".format(date.strftime("%Y/%m/%d"), payee))
    print("    {0:<50}{1:.2f} EUR".format(category, amount))
    print("    {0}".format(account))
    print("")


def parse_money(money):
    return locale.atof(money.replace(".", ""))


def main(filename):
    df_raw = pd.read_excel(filename)

    df_l = []
    for index, row in df_raw.iterrows():
        if len(row) > 0 and row[0] == "Referenznummer":
            df_l.append(list(row))
            continue

        if len(df_l) > 0 and len(row) == 0:
            break

        if len(df_l) > 0 and len(row[1]) > 0:
            df_l.append(list(row))

    df = pd.DataFrame(df_l[1:], columns=df_l[0])

    print(
        "#### Added by Barclays importer. Please check the transactions below very carefully."
    )

    for index, row in df.iterrows():
        if pd.isna(row["Buchungsdatum"][1]):
            continue

        dt = datetime.strptime(row["Buchungsdatum"][1], "%d.%m.%Y")

        # from here we could literally print as is, or
        # add some business logic to automate certain workflows
        #
        # for now, I think we'll do the categories by hand

        money = parse_money(row["Betrag"].replace(" €", ""))

        if money > 0:
            print_transaction(
                dt,
                row["Beschreibung"],
                "Liabilities:Eurowings Gold",
                "Income:TODO",
                -1 * money
            )
        else:
            print_transaction(
                dt,
                row["Beschreibung"],
                "Liabilities:Eurowings Gold",
                "Expenses:TODO",
                abs(money),
            )


if __name__ == "__main__":
    locale.setlocale(locale.LC_NUMERIC, "de_DE")

    parser = argparse.ArgumentParser(
        description="Converts Barclays Excel Export to ledger output",
    )

    parser.add_argument(
        "-f", "--file", type=str, nargs="?", required=True, help="File to parse",
    )

    args = parser.parse_args()

    main(args.file)
