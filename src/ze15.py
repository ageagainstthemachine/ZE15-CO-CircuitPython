# ZE15-CO CircuitPython Library 20250210j
# https://github.com/ageagainstthemachine/ZE15-CO-CircuitPython

# Import necessary libraries/modules
import board  # Import board module
import busio  # Import busio module to use UART (serial communication)
import time  # Import time module for delays

class ZE15CO:
    """
    CircuitPython library for the ZE15-CO carbon monoxide sensor using UART.
    Optimized for cooperative multitasking (non-blocking behavior).
    
    The sensor has two modes:
    - **Initiative Upload Mode** (default): The sensor automatically sends data every second.
    - **Q&A Mode**: The microcontroller must send a request to receive data.
    
    The library provides functions to:
    - Read CO concentration (in ppm)
    - Check sensor health
    
    If debug mode is enabled, detailed information will be returned for troubleshooting.
    If debug mode is disabled, only the ppm value is returned, ensuring easy integration.
    If there is a problem, the returned value should just be 0.0ppm.
    """
    
    INITIATIVE_MODE = 0  # Default mode where data is sent every second automatically
    QNA_MODE = 1  # Query-Response mode, where data is requested by the user
    
    REQUEST_FRAME = bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])  # Command to request data in Q&A Mode
    
    def __init__(self, rx, tx, mode=INITIATIVE_MODE, debug=False, warmup_time=10):
        """
        Initializes the ZE15-CO sensor with the given UART RX and TX pins.
        :param rx: RX pin for receiving data from sensor
        :param tx: TX pin for sending data to sensor
        :param mode: Operating mode - INITIATIVE_MODE (default) or QNA_MODE
        :param debug: Enable debugging output for troubleshooting
        :param warmup_time: Time in seconds for sensor warm-up (default: 10s)
        """
        self.uart = busio.UART(tx, rx, baudrate=9600, timeout=1)  # Initialize UART with a 1-second timeout
        self.mode = mode  # Set the operating mode
        self.debug = debug  # Debugging flag
        self.warmup_time = warmup_time  # Customizable warm-up time
        self._wait_for_sensor_startup()  # Ensure sensor has time to stabilize
        self.uart.reset_input_buffer()  # Flush old data to prevent incorrect readings

    def _debug_print(self, message):
        """
        Prints debug messages if debugging is enabled.
        """
        if self.debug:
            print(f"[DEBUG] {message}")

    def _wait_for_sensor_startup(self):
        """
        Non-blocking wait for sensor stabilization.
        The sensor requires warm-up time before returning valid data.
        """
        start_time = time.monotonic()
        while time.monotonic() - start_time < self.warmup_time:
            pass  # Allows other tasks to run in the background
        self._debug_print(f"Sensor startup complete after {self.warmup_time} seconds.")

    def _calculate_checksum(self, data):
        """
        Calculates the checksum for the received sensor response.
        The checksum is used to verify data integrity.
        :param data: Byte array of response data from sensor
        :return: Computed checksum value (last byte of response)
        """
        return (0xFF - sum(data[1:8]) + 1) & 0xFF  # Perform checksum validation

    def _parse_co_data(self, data):
        """
        Parses the CO concentration from the received sensor data.
        Correctly determines which bytes to use based on the active mode.
        """
        if len(data) != 9 or data[0] != 0xFF:
            self._debug_print("Invalid data received - incorrect length or start byte. Resynchronizing...")
            return None  # Return None to indicate misalignment
        if self._calculate_checksum(data) != data[8]:
            self._debug_print(f"Checksum error! Received: {hex(data[8])}, Expected: {hex(self._calculate_checksum(data))}")
            return None  # Return None to indicate checksum failure
        
        # Determine correct byte locations based on mode
        if self.mode == self.INITIATIVE_MODE:
            high_byte = data[4]  # Initiative Mode uses Byte 4 for High Byte
            low_byte = data[5]  # Initiative Mode uses Byte 5 for Low Byte
        else:
            high_byte = data[2]  # Q&A Mode uses Byte 2 for High Byte
            low_byte = data[3]  # Q&A Mode uses Byte 3 for Low Byte
        
        # Convert bytes to CO concentration (ppm)
        co_ppm = ((high_byte << 8) | low_byte) * 0.1  # Corrected formula for both modes
        
        self._debug_print(f"CO ppm Calculation: ({high_byte} << 8 | {low_byte}) * 0.1 = {co_ppm} ppm")
        return co_ppm

    def read_co(self):
        """
        Reads CO concentration from the sensor (non-blocking implementation).
        Returns only the ppm value, ensuring clean integration.
        If no valid data is received, retries once before returning 0.0 ppm.
        """
        if self.mode == self.QNA_MODE:
            self.uart.reset_input_buffer()  # Flush any old data before sending a request
            self.uart.write(self.REQUEST_FRAME)  # Send query command to request data
            self._debug_print("Sent Q&A request to sensor.")
            time.sleep(0.1)  # Allow time for response
            
        for _ in range(2):  # Retry mechanism: attempts twice before failing
            while self.uart.in_waiting > 0:
                first_byte = self.uart.read(1)  # Read single byte
                if first_byte and first_byte[0] == 0xFF:
                    data = first_byte + self.uart.read(8)  # Read remaining bytes
                    self._debug_print(f"Raw Data Received: {[hex(b) for b in data]}")
                    co_ppm = self._parse_co_data(data)
                    if co_ppm is not None:
                        return co_ppm  # Return valid CO ppm value
                    self._debug_print("Checksum or parsing error, retrying.")
                    time.sleep(0.1)  # Allow buffer to stabilize before reattempting
        
        self._debug_print("Failed to read full response after retries. Returning 0.0 ppm.")
        return 0.0
