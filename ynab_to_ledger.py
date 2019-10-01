#!/usr/bin/env python
# coding: utf-8

import argparse
import csv
import locale
from datetime import datetime


def print_transaction(date, payee, account, category, amount):
    print("{} {}".format(date.strftime("%Y/%m/%d"), payee))
    print("    {0}{1:38.2f} EUR".format(category, amount))
    print("    {0}".format(account))
    print("")


def parse_money(money):
    return abs(locale.atof(money.replace('.', '').replace('€', '')))


if __name__ == "__main__":
    locale.setlocale(locale.LC_NUMERIC, "de_DE")

    parser = argparse.ArgumentParser(
        description="Parse YNAB register and output to Ledger"
    )

    parser.add_argument(
        "-f", "--file", type=str, help="Filepath for register export file"
    )

    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        for row in reader:
            dt = datetime.strptime(row["Date"], "%d.%m.%Y")

            if parse_money(row['Outflow']) > 0:
                money = parse_money(row['Outflow'])
            else:
                money = parse_money(row['Inflow'])

            print_transaction(dt, row["Payee"], row['\ufeff"Account"'], row["Category"], money)
