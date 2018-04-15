#!/usr/bin/env python3

import collections
import csv
from decimal import Decimal
import itertools
import string
import sys

from crcmod.predefined import PredefinedCrc

SHOWABLE_CHARACTERS = set(
    ' ' + string.ascii_letters + string.digits + string.punctuation)


class Row(collections.namedtuple('Row', ('ts', 'value'))):

    pass

class BrivisMessage(collections.namedtuple('Row', ('ts', 'value'))):

    @property
    def crc(self):
        crc = PredefinedCrc('crc-16-buypass')
        crc.update(self.value[:-2])
        return crc.crcValue
    
    @property
    def crc_valid(self):
        if len(self.value) <= 2:
            return False
        return self.crc == int.from_bytes(self.value[-2:], byteorder='big')


def rows_to_messages(rows):
    discarded = 0
    total = 0
    msgs = []
    last_row = None
    msg_bytes = []
    for row in rows:
        msg_bytes += [(v, row.ts) for v in row.value]
        total += len(row.value)

    while len(msg_bytes) > 0:
        if len(msg_bytes) < (msg_bytes[0][0] + 1):
            discarded += 1
            msg_bytes[:1] = []
        message = [v[0] for v in msg_bytes[0:(msg_bytes[0][0] + 1)]]
        brivis_message = BrivisMessage(msg_bytes[0][1], bytes(message))
        if brivis_message.crc_valid:
            msgs.append(brivis_message)
            msg_bytes[0:(msg_bytes[0][0] + 1)] = []
            last_row = row
        else:
            discarded += 1
            msg_bytes[:1] = []
        # continue
        # if len(msg_bytes) == 0:
        #     msg_bytes.append(row.value[0])
        
        # if (len(msg_bytes) - 1) < msg_bytes[0]:
        #     msg_bytes += row.value[:msg_bytes[0] - len(msg_bytes) - 1]
        

        # if (len(msg_bytes) - 1) >= msg_bytes[0]:
        #     msgs.append(BrivisMessage(last_row.ts, bytes(msg_bytes[:msg_bytes[0]+1])))
        #     last_row = None
    discarded += len(msg_bytes)
    print('lost {}'.format(discarded/total * 100))
    return msgs


def diff_graph(rows):
    last_row = rows[0]
    values = []
    for row in rows[1:]:
        values.append(round(row.ts - last_row.ts, 2))
        last_row = row
    sorted_data = list((val, values.count(val)) for val in sorted(set(values)))
    for val, count in sorted_data:
        print(' {: >5.3f} -> {}'.format(val, '#' * count))


def print_counts(prefix, arr):
    msg_occurrences = collections.Counter(arr)
    for msg, count in reversed(msg_occurrences.most_common()):
        print('{} {:>5} | {}'.format(prefix, count, msg))



def main():
    rows = []
    with open(sys.argv[1]) as f:
        for line in f:
            _, _, data = line.strip().partition(' |')
            if not data:
                continue
            ts, _, val_hex = data.partition(', ')
            if not val_hex:
                continue
            ts = Decimal(ts) / 1000
            value = bytes.fromhex(val_hex)
            rows.append(Row(ts, value))
    # diff_graph(rows)
    msgs = rows_to_messages(rows)
    
    filter_messages = True
    if filter_messages:
        filtered = []
        for m in msgs:
            mhex = m.value[1:-2].hex()
            if mhex[:6] in ['312101', '3121ff']:
                continue
            elif mhex[:6] in ['213106', '213107', '213109']:
                continue
            elif mhex == '3121fb00000000':
                continue
            elif mhex[:8] in ['21310b00', '21312900']:
                continue
            elif mhex[:2] == '31' and mhex[4:6] == '01':
                continue
            else:
                filtered.append(m)
        msgs = filtered
            
            



    with open('filtered.csv', 'w') as f:
        f.write('Timestamp, Origin, Destination, OpCode, Message\n')
        for m in msgs:
            mhex = m.value[1:-2].hex()
            f.write('{:.2f}, {}, {}, {}, {}\n'.format(m.ts, mhex[:2], mhex[2:4], mhex[4:6], mhex[6:]))
            # if mhex[4:6] == '0b':
            #     f.write(
            #         '{:.2f}, {}, {}, {}, {:d}, {:d}, {:d}\n'
            #         .format(
            #             m.ts,
            #             mhex[:2],
            #             mhex[2:4],
            #             mhex[4:6],
            #             m.value[4],
            #             m.value[5],
            #             m.value[6]))
    

    message_bytes = [msg.value[1:-2].hex() for msg in msgs]
    outbound = [msg[4:] for msg in message_bytes if msg[:4] == '2131']
    inbound = [msg[4:] for msg in message_bytes if msg[:4] == '3121']
    other = [msg[4:] for msg in message_bytes if msg[:4] not in ('3121', '2131')]

    print_counts('OB_msg', (msg[:2] for msg in outbound))
    print()
    print_counts('IB_msg', (msg[:2] for msg in inbound))
    print()
    print_counts('Other ', (msg[:2] for msg in other))



    # msg_occurrences = collections.Counter(msg.value[1:-2] for msg in msgs)
    # for msg, count in reversed(msg_occurrences.most_common()):
    #     if msg[:2].hex() == '2131':
    #         print('{:>5} | -> {}'.format(count, msg.hex()))
    #     elif msg[:2].hex() == '3121':
    #         print('{:>5} | <- {}'.format(count, msg.hex()))
    #     else:
    #         print('{:>5} | ?? {}'.format(count, msg.hex()))

    # for msg in msgs:
    #     print('{: >5.2f} | {} (crc: {})'.format(msg.ts, msg.value.hex(), msg.crc_valid))
    # for item in sorted(set(msg_strs), key=lambda item: msg_strs.count(item)):
    #     print('{: <30}'.format(item), '#' * msg_strs.count(item))


if __name__ == '__main__':
    main()
