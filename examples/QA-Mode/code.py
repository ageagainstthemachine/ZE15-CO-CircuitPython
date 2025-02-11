# ZE15-CO Simple Q&A Mode Test Program 20250210b
# https://github.com/ageagainstthemachine/ZE15-CO-CircuitPython

# Import necessary libraries/modules
import board  # Import board module
import time  # Import time module for delays
from ze15 import ZE15CO  # Import the ZE15-CO sensor library

# ================= QUESTION & ANSWER MODE TEST ================= #
# This test program runs in Q&A Mode, where the ZE15-CO sensor does NOT automatically send data.
# The microcontroller must send a request, and then the sensor responds with CO concentration data.

# Enable debugging - set to True for detailed debug output, False to disable
DEBUG_MODE = False

# Set custom warm-up time in seconds (default is 10s in the library)
WARMUP_TIME = 10

# Initialize the ZE15-CO sensor on UART pins GP0 (TX) and GP1 (RX)
# The mode is set to QNA_MODE, meaning we must request data manually.
sensor = ZE15CO(rx=board.GP1, tx=board.GP0, mode=ZE15CO.QNA_MODE, debug=DEBUG_MODE, warmup_time=WARMUP_TIME)

def request_and_print_sensor_data():
    """
    Sends a request to the sensor and reads CO concentration.
    This function is necessary in Q&A Mode because the sensor does not transmit automatically.
    """
    co_ppm = 0.0  # Default to 0.0 ppm if no valid data is received
    retry_count = 3  # Number of retries in case of transient read failures

    # Retry logic to ensure we receive valid data
    while retry_count > 0:
        co_ppm = sensor.read_co()  # Send request and read CO concentration
        retry_count -= 1  # Decrement retry count if read fails
        if co_ppm > 0.0:  # If valid data is received, break the loop
            break
        time.sleep(0.5)  # Brief delay before retrying
    
    # Check if valid data was received or if an error occurred
    if co_ppm > 0.0:
        print(f"{co_ppm:.1f}")  # Print CO concentration value
    else:
        print("Error: Failed to read CO concentration")  # Indicate an issue

# Main loop: continuously request and display CO concentration
def main():
    while True:
        request_and_print_sensor_data()
        time.sleep(2)  # Wait 2 seconds before sending the next request

# Run the main loop
if __name__ == "__main__":
    main()
