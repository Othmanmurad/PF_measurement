from gpiozero import MCP3008
import time
from datetime import datetime
import math

class ZMPT101B:
    VREF = 3.3  # MCP3008 reference voltage
    SAMPLES = 100  # Number of samples to take for each measurement
    SAMPLE_INTERVAL = 0.001  # 1 ms between samples
    
    # Calibration factors
    CALIBRATION_FACTOR = 1.99  # Adjust this based on your previous calibration
    EXPECTED_MAINS_VOLTAGE = 120  # Expected RMS mains voltage

    def __init__(self, channel):
        self.adc = MCP3008(channel=channel)
        self.mains_calibration_factor = self.calculate_initial_calibration()

    def read_voltage(self):
        samples = [self.adc.value for _ in range(self.SAMPLES)]
        avg_raw = sum(samples) / self.SAMPLES
        sensor_voltage = (avg_raw * self.VREF) * self.CALIBRATION_FACTOR
        return sensor_voltage

    def calculate_initial_calibration(self):
        initial_sensor_voltage = self.read_voltage()
        initial_sensor_rms = initial_sensor_voltage / math.sqrt(2)
        return self.EXPECTED_MAINS_VOLTAGE / initial_sensor_rms

    def get_measurements(self):
        sensor_voltage = self.read_voltage()
        rms_sensor_voltage = sensor_voltage / math.sqrt(2)
        
        mains_rms_voltage = rms_sensor_voltage * self.mains_calibration_factor
        mains_peak_voltage = mains_rms_voltage * math.sqrt(2)
        
        return mains_peak_voltage, mains_rms_voltage

# Usage example
if __name__ == "__main__":
    sensor = ZMPT101B(channel=1)  # Using channel 1 of MCP3008
    print("Timestamp,Actual Voltage,RMS Voltage")
    print("Press Ctrl+C to stop the program")

    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Millisecond precision
            actual_voltage, rms_voltage = sensor.get_measurements()

            # Print to console in comma-separated format
            print(f"{timestamp},{actual_voltage:.2f},{rms_voltage:.2f}")

            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by user")
