# Reverse Engineering the Brivis 1-Wire Protocol 

## Motive

Wanting to automate existing systems in my house and we havea Brivis Central heating unit. Although it has a timer, it's not very practical when everyone in the house doen't live with a fixed schedule and the weather changes. 

Ideally, we can interact with the control panel to turn on and off using a system such as If This Then That to automate multiple home appliaces together.

## Preliminary

The control panel accepts two wires, that immediately pass through a full bridge rectifier. This appears to make installation easier as the signal is 15V DC so to allow reverse polarity. 
![IMG_20161004_145240.jpg](images/IMG_20161004_145240.jpg?raw=true)

Measuring the signal with a scope, the voltage drops down to 13.6V when the panel is connected, and to a further 8V during data transmission. Typical current draw when data is transmitted is 20mA (`8V / 20mA = 400Ω`)
Manually testing a 220Ω resistor pulls the voltage back down to 8V, shows tha the system as a 180Ω effective series resistance. 

![IMG_20161004_144120.jpg](images/IMG_20161004_144120.jpg?raw=true)

![IMG_20161004_144424.jpg](images/IMG_20161004_144424.jpg?raw=true)

When the panel is plugged in and powered on, it draws power for about 20ms (charing up it's own capacitor). Then settles to about 4mA.

![IMG_20161004_144933.jpg](images/IMG_20161004_144933.jpg?raw=true)

Using a circuit that holds a reference voltage of the system at rest and operates an output signal as the input voltage drops below a threshold, a logic analyser can be used to collect data for long periods of time. For example, using a fx2la based logic analyser such as Saleae Logic, we can capture data for long periods of time.

![IMG_20180410_050047.jpg](images/IMG_20180410_050047.jpg?raw=true)

After capturing the raw signals, a UART protocol decoder is used configured with a 9600 baudrate and inverted signal gives us clean hex data that we can work with. 

![Logic_2018-04-11_01-44-54.png](images/Logic_2018-04-11_01-44-54.png?raw=true)

## Analysis

Each byte in a payload is transmitted at 10ms intervals, with about 50ms in between payloads. 

![Logic_2018-04-11_01-47-18.png](images/Logic_2018-04-11_01-47-18.png?raw=true) ![Logic_2018-04-11_01-48-46.png](images/Logic_2018-04-11_01-48-46.png?raw=true)

Here is a dump of the payloads with their respective timestamp during a single session.

```
 6.99  | 05 21 31 09 60 A1             // Turning the knob to increment the set temperature
 7.10  | 05 31 21 FF 03 D5
 7.18  | 05 21 31 09 60 A1
 7.31  | 05 31 21 FF 03 D5
 7.39  | 05 21 31 09 60 A1
 7.52  | 05 31 21 FF 03 D5
 7.60  | 05 21 31 09 60 A1
 7.72  | 05 31 21 FF 03 D5
 7.80  | 05 21 31 09 60 A1
 7.92  | 05 31 21 FF 03 D5
 8.01  | 05 21 31 09 60 A1
 8.13  | 05 31 21 FF 03 D5
 8.22  | 08 21 31 0B 00 0E 23 40 93    // The set temperature is now greater than the current temperature of the panel
 8.37  | 05 31 21 FF 03 D5
 8.46  | 05 21 31 09 60 A1
 8.58  | 05 31 21 FF 03 D5
 8.67  | 05 21 31 09 60 A1
 8.78  | 05 31 21 FF 03 D5
 8.87  | 05 21 31 09 60 A1
 8.98  | 05 31 21 FF 03 D5
 9.07  | 05 21 31 09 60 A1
 9.19  | 05 31 21 FF 03 D5
 9.27  | 08 21 31 0B FF 14 23 90 9C    // The heating system shows the fan is active and the gas heating element is on.
 9.43  | 05 31 21 FF 03 D5
 9.51  | 06 21 31 29 00 E0 CB
 9.62  | 09
 9.66  | 05 31 21 FF 03 D5
 9.74  | 05 21 31 09 60 A1
 9.84  | 09
 9.88  | 05 31 21 FF 03 D5
 9.97  | 05 21 31 09 60 A1
10.07  | 09
10.11  | 05 31 21 FF 03 D5
10.20  | 08 21 31 0B FF 16 23 1C 9F
10.32  | 09
10.36  | 05 31 21 FF 03 D5
10.45  | 06 21 31 29 00 E0 CB
10.57  | 05 31 21 FF 03 D5
10.66  | 05 21 31 06 60 83
10.75  | 09 31
10.80  | 09 31 21 FB 00 22 00 00 F1 64
10.97  | 09 31 21 05 00 22 00 00 59 37
11.10  | 05 21 31 FF 62 95
13.20  | 05 21 31 09 60 A1             // Turning the knob to decrement the set temperature
13.31  | 05 31 21 FF 03 D5
13.39  | 05 21 31 09 60 A1
13.52  | 05 31 21 FF 03 D5
13.61  | 05 21 31 09 60 A1
13.73  | 05 31 21 FF 03 D5
13.82  | 05 21 31 09 60 A1
13.94  | 05 31 21 FF 03 D5
14.03  | 08 21 31 0B 00 0D 23 4A 93
14.18  | 05 31 21 FF 03 D5
14.27  | 05 21 31 09 60 A1
14.38  | 05 31 21 FF 03 D5
14.47  | 05 21 31 09 60 A1
14.56  | 09 31
14.61  | 05 31 21 FF 03 D5
14.70  | 08 21 31 0B 00 00 23 E4 90
14.82  | 09 31
14.87  | 05 31 21 FF 03 D5
14.96  | 06 21 31 29 00 E0 CB
15.07  | 09
15.11  | 05 31 21 FF 03 D5
15.20  | 05 21 31 06 60 83
15.31  | 09
15.34  | 09 31 21 FB 00 00 00 00 F3 CC
15.52  | 09 31 21 05 00 00 00 00 5B 9F
15.65  | 05 21 31 FF 62 95
```

The messages appear to start with a length byte as the following number of bytes match. Based on randomness (or high entropy) the last two bytes could be CRC 16.

[Reveng](http://reveng.sourceforge.net/readme.htm) is a neat utility to try and guess your CRC parameters. Using a random message captured from the log. We get
```bash
$ reveng -w 16 -s 082131070a05068ac5
width=16  poly=0x8005  init=0x0000  refin=false  refout=false  xorout=0x0000  check=0xfee8  residue=0x0000  name="CRC-16/BUYPASS"
```
Which proves the last two bytes are CRC16 using `CRC-16/BUYPASS`

Extracting the message by (removing the first byte(the length) and the last 2 bytes(the CRC) yields a message where bytes:

1. The source device's address
2. The destination device's address
3. An opcode?(message in this context means the remaining bytes)
    - Heater
        - `01` -- Appears to be a ping. Sent to increasing addresses after removing the controller. No message body.
        - `FF` -- Appears to be heater "ack". No message body
        - `FB` -- Appears to be status reporting. Message is 4 bytes.
    - Controller
        - `06` -- Appears to be status request. (Heater responds `FB`). No message body.
        - `07` -- Time/Day of Week. (1ce/min). (Aked by heater with `FF`). 3 byte message body:
            1. Hour of day(e.g. `0x16` == `22:xx`)
            2. Minute of hour(e.g. `0x24` == `xx:36`)
            3. Day of week(Monday == `0x00`, Sunday == `0x06`).
        - `09` -- ???. (1ce/min). (Aked by heater with `FF`). No message body.
        - `0b` -- Temperature control (1ce/min). (Aked by heater with `FF`). 3 byte message body:
            1. State of something? (remains `0x00` for most of the day. `0xff` has been seen).
            2. Target temperature(e.g. `0x11` == `17 deg C`). `0x00` is "off".
            3. Current temperature times 2(e.g. `0x25` == `18.5 deg C`).
        - `29` -- ???. (1ce/min). (Aked by heater with `FF`). 1 byte message body:
            - `00` -- ?

