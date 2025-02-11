# ZE15-CO Simple Initiative Upload Test Program 20250210b
# https://github.com/ageagainstthemachine/ZE15-CO-CircuitPython

# Import necessary libraries/modules
import board  # Import board module
import time  # Import time module for delays
from ze15 import ZE15CO  # Import the ZE15-CO sensor library

# ================= INITIATIVE MODE TEST ================= #
# This test program runs in Initiative Upload Mode, where the ZE15-CO sensor
# automatically sends data every second. The microcontroller only needs to read the data.

# Enable debugging - set to True for detailed debug output, False to disable
DEBUG_MODE = False

# Set custom warm-up time in seconds (default is 10s in the library)
WARMUP_TIME = 10

# Initialize the ZE15-CO sensor on UART pins GP0 (TX) and GP1 (RX)
# The mode is set to INITIATIVE_MODE, meaning the sensor continuously transmits data.
sensor = ZE15CO(rx=board.GP1, tx=board.GP0, mode=ZE15CO.INITIATIVE_MODE, debug=DEBUG_MODE, warmup_time=WARMUP_TIME)

def print_sensor_data():
    """
    Reads CO concentration, then prints the value.
    Since the sensor sends data automatically every second in Initiative Mode,
    this function simply reads and processes that data.
    """
    co_ppm = 0.0  # Default to 0.0 ppm if no valid data is received
    retry_count = 3  # Number of retries in case of transient read failures

    # Retry logic to ensure we receive valid data
    while retry_count > 0:
        co_ppm = sensor.read_co()  # Attempt to read CO concentration
        retry_count -= 1  # Decrement retry count if read fails
        if co_ppm > 0.0:  # If valid data is received, break the loop
            break
        time.sleep(0.5)  # Brief delay before retrying
    
    # Check if valid data was received or if an error occurred
    if co_ppm > 0.0:
        print(f"{co_ppm:.1f}")  # Print CO concentration value
    else:
        print("Error: Failed to read CO concentration")  # Indicate an issue

# Main loop: continuously read and display CO concentration
def main():
    while True:
        print_sensor_data()
        time.sleep(2)  # Wait 2 seconds before the next reading

# Run the main loop
if __name__ == "__main__":
    main()
