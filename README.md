# ZE15-CO CircuitPython Library

## Overview
This repository contains a CircuitPython library for interfacing with the ZE15-CO Carbon Monoxide Sensor by Winsen using a UART connection. The library is optimized for cooperative multitasking and provides support for both sensor modes: **Initiative Upload Mode** and **Q&A Mode**.

**Datasheet:** [ZE15-CO Official Datasheet](http://winsen-sensor.com/d/files/ZE15-CO.pdf)

---

## Features
- Supports both Initiative Upload Mode and Q&A Mode for sensor data retrieval.
- Checksum validation to ensure data integrity.
- Automatic resynchronization in case of misaligned packets.
- Non-blocking implementation to maintain system responsiveness.
- Debug mode for detailed troubleshooting output.

---

## Library Installation
To use this library, copy the `ze15.py` file to the `lib` directory of your CircuitPython board.

## Usage
### Importing the Library
```python
import board
import time
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

---

## License
This library is provided under the **GPL-3.0 License**. See [`LICENSE`](<LICENSE>) for details.

---

## Contributions
Contributions are welcome. Feel free to submit pull requests or report issues with the repository.
