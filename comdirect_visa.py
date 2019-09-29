#!/Users/stefan/anaconda3/bin/python
from datetime import datetime
import sys
import csv
import codecs
import locale
import re


def print_transaction(record):
    print("{} {}".format(
        record['date'].strftime("%Y/%m/%d"),
        record['payee']
    ))
    print("    {0}{1:38.2f} EUR".format("<category>", record['money']))
    print("    {0}".format("Liabilities:comdirect Visa"))
    print("")


def main():
    locale.setlocale(locale.LC_ALL, "de_DE")
    print("Date,Payee,Category,Memo,Outflow,Inflow")

    with codecs.open(sys.argv[1], "r", "iso-8859-1") as f:
        r = csv.reader(f, delimiter=';', quotechar='"')
        foreign = False
        foreignadd = 0
        for row in r:
            try:
                # Date
                # get the date, and if the first thing is not a date, skip row
                dt = datetime.strptime(row[0], '%d.%m.%Y')

                # Payee
                payee = row[4].strip()

                # Money, as in inflow or outflow
                money = locale.atof(re.sub(r'\.', '', row[5]))

                if foreign:
                    money += foreignadd
                    foreign = False

                if 'PROZ.AUSLANDSENTGELT' in payee:
                    foreign = True
                    foreignadd = money
                else:
                    print_transaction({
                        'date': dt,
                        'payee': payee,
                        'money': -1 * money
                    })
            except ValueError:
                continue
            except IndexError:
                continue


if __name__ == "__main__":
    main()
