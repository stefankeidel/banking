#!/usr/bin/env python
# coding: utf-8

import argparse
import csv
import locale
from datetime import datetime
#import pudb; pu.db


class SkipTransactionException(Exception):
    pass


def print_transaction(date, payee, account, category, amount):
    print("{} {}".format(date.strftime("%Y/%m/%d"), payee))
    print("    {0:<50}{1:.2f} EUR".format(category, amount))
    print("    {0}".format(account))
    print("")


def parse_money(money):
    return abs(locale.atof(money.replace(".", "").replace("€", "")))


def translate_stuff(payee, account, category, money):
    account_map = {
        "Sparkasse": "Closed:Assets:Sparkasse",
        "BAFöG": "Closed:Liabilities:BAFöG",
        "BAV": "Assets:Investments:Zurich Wayfair BAV",
        "GLS Giro": "Assets:GLS Giro",
        "Norisbank TG": "Closed:Assets:Norisbank TG",
        "Norisbank Giro": "Closed:Assets:Norisbank Giro",
        "GLS Depot": 'Assets:REPLACEME',
        "comdirect Giro": "Assets:comdirect Giro",
        "Amazon VISA": "Closed:Liabilities:Amazon VISA",
        "comdirect TG": "Assets:comdirect Tagesgeld",
        "comdirect Verrechnung": "Assets:comdirect Verrechnung",
        "comdirect Depot": "Assets:Investments:comdirect Depot",
        "CosmosDirekt Basisrente": "Assets:Investments:cosmosdirect BR",
        "comdirect VISA": "Liabilities:comdirect Visa",
    }

    category_map = {
        "Everyday Expenses:Clothing": "Expenses:Discretionary",
        "Everyday Expenses:Clothes": "Expenses:Discretionary",
        "Taxes:Income Tax 2014": "Expenses:Taxes",
        "Monthly Bills:Electricity": "Expenses:Utilities",
        "Investment:Cosmos FondsBasisrente": "Expenses:Investments",
        "Taxes:Income Tax 2015": "Expenses:Taxes",
        "Investment:Market": "Expenses:Investments",
        "Everyday Expenses:Cash": "Expenses:Cash",
        "Savings Goals:Saved Rent Liz": "Income:Rent",
        "Savings Goals:Emergency Fund": "Misc:Emergency Fund",
        "Monthly Bills:iMac Credit": "Expenses:Discretionary",
        "Savings Goals:US Visa Fees": "Expenses:US Visa",
        "Everyday Expenses:Groceries": "Expenses:Mandatory",
        "Everyday Expenses:Spending Money": "Expenses:Discretionary",
        "Savings Goals:Airbnb SFO": "Expenses:Travel",
        "Savings Goals:Vacation": "Expenses:Travel",
        "Everyday Expenses:Discretionary": "Expenses:Discretionary",
        "Monthly Bills:Business Expenses": "Expenses:Business",
        "Everyday Expenses:Restaurants/Takeout": "Expenses:Discretionary",
        "Everyday Expenses:Public Transport": "Expenses:Transportation",
        "Income:Available this month": "Income:Generic",
        "Savings Goals:MacBook": "Expenses:Misc",
        "Savings Goals:30. Geburtstag": "Expenses:Misc",
        "Taxes:Income Tax 2016": "Expenses:Taxes",
        "Income:Available next month": "Income:Generic",
        "Yearly Bills:Boris Deposit": "Expenses:Misc",
        "Savings Goals:Northeast Trip 2018": "Expenses:Travel",
        "Yearly Bills:Insurance": "Expenses:Insurance",
        "Monthly Bills:Housekeeping": "Expenses:Discretionary",
        "Taxes:Income Tax 2013": "Expenses:Taxes",
        "Savings Goals:Big Purchase/Gift Fund": "Expenses:Misc",
        "Monthly Bills:Cable/Subscriptions": "Expenses:Subscriptions",
        "Savings Goals:Berlin Vaca": "Expenses:Travel",
        "Savings Goals:NYC X-Mas": "Expenses:Travel",
        "Monthly Bills:Health Insurance": "Expenses:Insurance",
        "Savings Goals:Pay back BAFöG": "Expenses:Debt",
        "Everyday Expenses:Mandatory": "Expenses:Mandatory",
        "Taxes:VAT": "Expenses:Taxes",
        "Monthly Bills:Phone/Mobile/Internet": "Expenses:Utilities",
        "Savings Goals:NYC": "Expenses:Travel",
        "Monthly Bills:Rent": "Expenses:Rent",
        "Pre-YNAB Debt:Amazon VISA": "Expenses:Misc",
        "Everyday Expenses:Transportation": "Expenses:Transportation",
    }

    # Transfers are direct interactions between accounts
    if payee.startswith('Transfer :'):
        # this is to make sure we only import one side of the transfer
        # as in the original exports we have two transactions for the same
        if money < 0:
            raise SkipTransactionException()

        source_acct = payee.split(':')[-1].strip()
        category = account_map[source_acct]
    elif payee == 'Starting Balance':
        category = 'Equity:Opening Balances'
    elif payee == 'Reconciliation Balance Adjustment':
        category = 'Income:Capital Gains'
    elif category == '':
        category = 'Misc:Misc'
    else:
        category = category_map[category]

    return payee, account_map[account], category


if __name__ == "__main__":

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
                # this is a bit counterintuitive but it has to do
                # with the order we print the transaction in :shrug:
                money = -1 * parse_money(row["Inflow"])

            try:
                payee, account, category = translate_stuff(
                    row["Payee"], row['\ufeff"Account"'], row["Category"], money
                )
            except SkipTransactionException:
                continue

            print_transaction(dt, payee, account, category, money)

            accounts.add(row['\ufeff"Account"'])
            categories.add(row["Category"])
