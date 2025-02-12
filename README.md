# ZE15-CO CircuitPython Library

## Overview
This repository contains a CircuitPython library for interfacing with the ZE15-CO Carbon Monoxide Sensor by Winsen using a UART connection. The library is optimized for cooperative multitasking and provides support for both sensor modes: **Initiative Upload Mode** and **Q&A Mode**.

**Datasheet:** [ZE15-CO Official Datasheet](http://winsen-sensor.com/d/files/ZE15-CO.pdf)

## Features
- Supports both Initiative Upload Mode and Q&A Mode for sensor data retrieval.
- Checksum validation to ensure data integrity.
- Automatic resynchronization in case of misaligned packets.
- Non-blocking implementation to maintain system responsiveness.
- Debug mode for detailed troubleshooting output.

## Library Installation
To use this library, copy the `ze15.py` file to the `lib` directory of your CircuitPython board.

## Usage
### Importing the Library
```python
from ze15 import ZE15CO
```

### Initializing the Sensor
```python
sensor = ZE15CO(rx=board.GP1, tx=board.GP0, mode=ZE15CO.INITIATIVE_MODE, debug=False, warmup_time=10)
```
**Parameters:**
- `rx`: UART RX pin.
- `tx`: UART TX pin.
- `mode`: Operation mode (`ZE15CO.INITIATIVE_MODE` or `ZE15CO.QNA_MODE`).
- `debug`: Enable or disable debug messages (default: `False`).
- `warmup_time`: Warm-up time in seconds before sensor begins reading (default: `10s`).

## Operating Modes
### Initiative Upload Mode
In this mode, the ZE15-CO sensor automatically transmits data every second.

#### Example Usage
```python
while True:
    co_ppm = sensor.read_co()
    print(f"CO Concentration: {co_ppm:.1f} ppm")
    time.sleep(1)
```

### Q&A Mode
In this mode, the microcontroller must send a request to the sensor and then wait for a response.

#### Example Usage
```python
while True:
    co_ppm = sensor.read_co()
    print(f"CO Concentration: {co_ppm:.1f} ppm")
    time.sleep(2)
```

## Data Format and Protocol
The ZE15-CO sensor communicates using a 9-byte UART packet format. The format differs slightly between modes.

### Q&A Mode Request Format
```
| Byte|0   |1   |2   |3   |4   |5   |6   |7   |8   |
|--------------------------------------------------|
| Data|0xFF|0x01|0x86|0x00|0x00|0x00|0x00|0x00|CHK |
```
#### Byte Description:
- **Byte 0 (0xFF):** Start byte.
- **Byte 1 (0x01):** Command identifier (read gas concentration).
- **Byte 2 (0x86):** Data type (CO gas request command).
- **Bytes 3-7 (0x00):** Reserved, always zero.
- **Byte 8 (CHK):** Checksum for validation.

### Q&A Mode Response Format
```
| Byte|0   |1   |2   |3   |4   |5   |6   |7   |8   |
|--------------------------------------------------|
| Data|0xFF|0x86|HB  |LB  |0x00|0x00|0x00|0x00|CHK |
```
#### Byte Description:
- **Byte 0 (0xFF):** Start byte.
- **Byte 1 (0x86):** Command echo (confirming CO gas response).
- **Bytes 2-3 (HB, LB):** High and low bytes of CO concentration.
- **Bytes 4-7 (0x00):** Reserved, always zero.
- **Byte 8 (CHK):** Checksum for validation.

### Initiative Upload Mode Format
```
| Byte|0   |1   |2   |3   |4   |5   |6   |7   |8   |
|--------------------------------------------------|
| Data|0xFF|0x04|0x03|0x01|HB  |LB  |0x13|0x88|CHK |
```
#### Byte Description:
- **Byte 0 (0xFF):** Start byte.
- **Byte 1 (0x04):** Gas type identifier (CO gas).
- **Byte 2 (0x03):** Measurement unit (ppm).
- **Byte 3 (0x01):** Decimal places (0.1 ppm resolution).
- **Bytes 4-5 (HB, LB):** High and low bytes of CO concentration.
- **Bytes 6-7 (0x13, 0x88):** Full range (5000 ppm fixed value).
- **Byte 8 (CHK):** Checksum for validation.

### CO Concentration Calculation
```
CO ppm = ((High Byte << 8) | Low Byte) * 0.1
```
#### Calculation Steps:
1. The high byte (`HB`) is shifted left by 8 bits to represent the most significant part of the value.
2. The low byte (`LB`) is added to this shifted value, forming a 16-bit integer.
3. This integer value is then multiplied by 0.1 to apply the sensor's scaling factor.

### Checksum Calculation
```
CHK = (0xFF - (Sum of bytes 1 through 7) + 1) & 0xFF
```
#### Calculation Steps:
1. Sum **bytes 1 through 7** of the response.
2. Subtract this sum from **0xFF**.
3. Add **1** to the result.
4. Mask to **8 bits** using `& 0xFF` to ensure overflow does not affect the result.

## Test Programs
### Initiative Upload Mode Test
This example ([`code.py`](<examples/Initiative-Upload-Mode/code.py>)) program continuously reads the CO concentration from the sensor.

### Q&A Mode Test
This example ([`code.py`](<examples/QA-Mode/code.py>)) program requests and retrieves CO concentration data when needed.

## Debug Mode
For troubleshooting, enable debug mode when initializing the sensor:
```python
sensor = ZE15CO(rx=board.GP1, tx=board.GP0, mode=ZE15CO.QNA_MODE, debug=True)
```
This will print additional information such as raw data received, checksum validation, and misalignment handling.

## License
This library is provided under the **GPL-3.0 License**. See [`LICENSE`](<LICENSE>) for details.

## Contributions
Contributions are welcome. Feel free to submit pull requests or report issues with the repository.
