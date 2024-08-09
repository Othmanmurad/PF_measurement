from gpiozero import MCP3008
import time
from datetime import datetime
import math

class MagneLabCT:
    VREF = 3.3  # MCP3008 reference voltage
    CT_MAX_VOLTAGE = 0.333  # CT output voltage at rated current
    SAMPLES = 1000  # Number of samples for averaging and RMS calculation
    SAMPLE_INTERVAL = 0.001  # 1 ms between samples
    
    # Calibration factors
    VOLTAGE_CALIBRATION = 21.5  # Actual value/ value printed through the code
    CURRENT_CALIBRATION = 1.45  # Actual value/ value printed through the code

    def __init__(self, channel, max_current):
        self.adc = MCP3008(channel=channel)
        self.max_current = max_current

    def get_measurements(self):
        samples = [self.adc.value for _ in range(self.SAMPLES)]

        # Calculate average voltage
        avg_voltage = sum(samples) / self.SAMPLES * self.VREF
        
        # Calculate RMS voltage
        rms_voltage = math.sqrt(sum(v**2 for v in samples) / self.SAMPLES) * self.VREF
        
        # Calculate RMS current
        rms_current = (rms_voltage / self.CT_MAX_VOLTAGE) * self.max_current
        
        # Apply calibration
        calibrated_voltage = avg_voltage * self.VOLTAGE_CALIBRATION
        calibrated_current = rms_current * self.CURRENT_CALIBRATION

        return calibrated_voltage, calibrated_current

# Usage example
if __name__ == "__main__":
    # Change max_current based on your CT model (5, 20, 30, 50, 100, 200, or 600)
    sensor = MagneLabCT(channel=0, max_current=30)

    print("Timestamp,Calibrated Voltage,Calibrated RMS Current")
    print("Press Ctrl+C to stop the program")

    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Millisecond precision
            calibrated_voltage, calibrated_current = sensor.get_measurements()

            # Print to console in comma-separated format
            print(f"{timestamp},{calibrated_voltage:.3f},{calibrated_current:.3f}")

            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by user")




