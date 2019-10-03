#!/usr/bin/env python
# coding: utf-8

import argparse
import csv
import locale
from datetime import datetime


def print_transaction(date, payee, account, category, amount):
    print("{} {}".format(date.strftime("%Y/%m/%d"), payee))
    print("    {0}\t\t\t{1:.2f} EUR".format(category, amount))
    print("    {0}".format(account))
    print("")


def parse_money(money):
    return abs(locale.atof(money.replace(".", "").replace("€", "")))


if __name__ == "__main__":
    account_map = {
        "Sparkasse": "Closed:Assets:Sparkasse",
        "BAFöG": "Closed:Liabilities:BAFöG",
        "BAV": "Assets:Investments:Zurich Wayfair BAV",
        "GLS Giro": "Assets:GLS Giro",
        "Norisbank TG": "Closed:Assets:Norisbank TG",
        "Norisbank Giro": "Closed:Assets:Norisbank Giro",
        "GLS Depot": None,
        "comdirect Giro": "Assets:comdirect Giro",
        "Amazon VISA": "Closed:Liabilities:Amazon VISA",
        "comdirect TG": "Assets:comdirect Tagesgeld",
        "comdirect Verrechnung": "Assets:comdirect Verrechnung",
        "comdirect Depot": "Assets:Investments:comdirect Depot",
        "CosmosDirekt Basisrente": "Assets:Investments:cosmosdirect BR",
        "comdirect VISA": "Liabilities:comdirect Visa",
    }

    category_map = {
        "Everyday Expenses:Clothing",
        "Everyday Expenses:Clothes",
        "Taxes:Income Tax 2014",
        "Monthly Bills:Electricity",
        "Investment:Cosmos FondsBasisrente",
        "Taxes:Income Tax 2015",
        "Investment:Market",
        "Everyday Expenses:Cash",
        "Savings Goals:Saved Rent Liz",
        "Savings Goals:Emergency Fund",
        "Monthly Bills:iMac Credit",
        "Savings Goals:US Visa Fees",
        "Everyday Expenses:Groceries",
        "Everyday Expenses:Spending Money",
        "Savings Goals:Airbnb SFO",
        "Savings Goals:Vacation",
        "Everyday Expenses:Discretionary",
        "Monthly Bills:Business Expenses",
        "Everyday Expenses:Restaurants/Takeout",
        "Everyday Expenses:Public Transport",
        "Income:Available this month",
        "Savings Goals:MacBook",
        "Savings Goals:30. Geburtstag",
        "Taxes:Income Tax 2016",
        "Income:Available next month",
        "Yearly Bills:Boris Deposit",
        "Savings Goals:Northeast Trip 2018",
        "Yearly Bills:Insurance",
        "Monthly Bills:Housekeeping",
        "Taxes:Income Tax 2013",
        "Savings Goals:Big Purchase/Gift Fund",
        "Monthly Bills:Cable/Subscriptions",
        "Savings Goals:Berlin Vaca",
        "Savings Goals:NYC X-Mas",
        "Monthly Bills:Health Insurance",
        "Savings Goals:Pay back BAFöG",
        "Everyday Expenses:Mandatory",
        "Taxes:VAT",
        "Monthly Bills:Phone/Mobile/Internet",
        "Savings Goals:NYC",
        "Monthly Bills:Rent",
        "Pre-YNAB Debt:Amazon VISA",
        "Everyday Expenses:Transportation",
    }

    locale.setlocale(locale.LC_NUMERIC, "de_DE")

    parser = argparse.ArgumentParser(
        description="Parse YNAB register and output to Ledger"
    )

    parser.add_argument(
        "-f", "--file", type=str, help="Filepath for register export file"
    )

    accounts = set()
    categories = set()

    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        for row in reader:
            dt = datetime.strptime(row["Date"], "%d.%m.%Y")

            if parse_money(row["Outflow"]) > 0:
                money = parse_money(row["Outflow"])
            else:
                money = parse_money(row["Inflow"])

            # print_transaction(dt, row["Payee"], row['\ufeff"Account"'], row["Category"], money)

            accounts.add(row['\ufeff"Account"'])
            categories.add(row["Category"])

    print(categories)
