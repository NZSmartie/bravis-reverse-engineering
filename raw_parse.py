#!/usr/bin/env python3

import collections
import csv
from decimal import Decimal
import itertools
import string
import sys

SHOWABLE_CHARACTERS = set(
    ' ' + string.ascii_letters + string.digits + string.punctuation)


class Row(collections.namedtuple('Row', ('ts', 'value'))):

    pass


def rows_to_messages(rows):
    msg = [rows[0]]
    msgs = []
    for row in rows[1:]:
        if (row.ts - msg[-1].ts) > 0.015:
            msgs.append(msg)
            msg = [row]
        else:
            msg.append(row)
    msgs.append(msg)
    msg_strs = []
    for msg in msgs:
        msg_str = []
        for item in msg:
            msg_str.append('%02X' % item.value)
        msg_str = ' '.join(msg_str)
        msg_strs.append(msg_str)
        print('{: >5.2f}  | {}'.format(msg[0].ts, msg_str))
    for item in sorted(set(msg_strs), key=lambda item: msg_strs.count(item)):
        print('{: <30}'.format(item), '#' * msg_strs.count(item))


def diff_graph(rows):
    last_row = rows[0]
    values = []
    for row in rows[1:]:
        values.append(round(row.ts - last_row.ts, 2))
        last_row = row
    sorted_data = list((val, values.count(val)) for val in sorted(set(values)))
    for val, count in sorted_data:
        print(' {: >5.3f} -> {}'.format(val, '#' * count))


def main():
    rows = []
    with open(sys.argv[1]) as f:
        reader = iter(csv.reader(f))
        next(reader)  # skip header
        for row in reader:
            ts = Decimal(row[0])
            value = int(row[2], base=16)
            rows.append(Row(ts, value))
    # diff_graph(rows)
    rows_to_messages(rows)


if __name__ == '__main__':
    main()
