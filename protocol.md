# Brivis Protocol

## Messge Structure 
Each message transmission is made up of a length byte, source address, destination address, operation code, n bytes of data and a CRC 16 checksum.

| **Byte** |   01   | 02  |  03  |   04   |   ..   | *last* 
|----------|:------:|:---:|:----:|:------:|:------:|:------:
|          | Length | Src | Dest | OpCode | (data) | CRC16

>For example the message `082131070A05068AC5` is broken down
> 
>| Length | Src | Dest | OpCode |  (data)  | CRC16
>|:------:|:---:|:----:|:------:|:--------:|:-----:
>|  `08`  |`21` | `31` |  `07`  |`0A 05 06`|`8A C5`

### Length

Length is the total number of bytes **not** including the length byte the are to follow. Consider this byte as a header to the rest of the message ans is a fixed length of 1.

### Src / Dest Address

The source address is an 8 bit value that represents the originator of the message. Where as the destination address is the intended recipient of the message.

### OpCode and Data

The operation code is an 8 bit value that by preceed up to *n* data bytes where *n* is the length of the message subtract the src, dest and CRC16 bytes.

### CRC 16

The cyclic redundency check (crc) is a 16 bit value to check the integrity of the message.
The CRC 16 used a predefined set of parameters named `CRC-16/BUYPASS`. 

|        Parameter | Value    |
|-----------------:|----------|
|            Width | `16`     |
|       Polynomial | `0x8005` |
|          Initial | `0x0000` |
|  Input Reflected | `False`  |
| Output Reflected | `False`  |
|       XOr Output | `0x0000` |

## Known OpCodes

### `01` - Ping?
 
*No message body*

### `FF` - Ack?

*No message body*

### `FB` - Status Response

4 byte message body *(unknown)*

### `06` - Request Status

*No message body*

### `07` - Day & Time

3 byte message body

1. Hour of day(e.g. `0x16` == `22:xx`)
2. Minute of hour(e.g. `0x24` == `xx:36`)
3. Day of week(Monday == `0x00`, Sunday == `0x06`).

### `09` - Unknown 

*No message body*

### `0b` - Set Temperature

3 byte message body

1. State of something? (remains `0x00` for most of the day. `0xff` has been seen).
2. Target temperature(e.g. `0x11` == `17 deg C`). `0x00` is "off".
3. Current temperature times 2(e.g. `0x25` == `18.5 deg C`).

### `29` - Unknown

1 byte message body

1. `00` - ?