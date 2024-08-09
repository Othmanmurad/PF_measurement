import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np
from gpiozero import MCP3008
from datetime import datetime
import math

# Set up MCP3008 for voltage sensor
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)

# Set up the voltage channel
voltage_channel = AnalogIn(mcp, MCP.P1)

# Constants
SAMPLES = 1000
SAMPLE_RATE = 100000  # Hz
VCC = 3.3
ADC_MAX = 65535
VOLTAGE_CALIBRATION_FACTOR = 71.7  # Adjusted based on actual measurements

# MagneLab CT Class
class MagneLabCT:
    VREF = 3.3  # MCP3008 reference voltage
    CT_MAX_VOLTAGE = 0.333  # CT output voltage at rated current
    SAMPLES = 1000  # Number of samples for averaging and RMS calculation
    SAMPLE_INTERVAL = 0.001  # 1 ms between samples

    # Calibration factors
    VOLTAGE_CALIBRATION = 24.5  # Actual value/ value printed through the code
    CURRENT_CALIBRATION = 1.85  # Actual value/ value printed through the code

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

# Set up the new current transformer
current_transformer = MagneLabCT(channel=0, max_current=30)

def read_voltage_samples():
    voltage_samples = []
    start_time = time.monotonic()
    for _ in range(SAMPLES):
        voltage_samples.append(voltage_channel.value)
        while time.monotonic() - start_time < 1/SAMPLE_RATE:
            pass
        start_time += 1/SAMPLE_RATE
    
    voltages = np.array(voltage_samples) / ADC_MAX * VCC * VOLTAGE_CALIBRATION_FACTOR
    voltages = voltages * 2
    return voltages

def calculate_power_parameters(voltages, current):
    v_rms = np.sqrt(np.mean(voltages**2))
    
     # Set current to 0 if it's less than 0.4
    if current < 0.4:
        current = 0.0
    
    i_rms = current
    
    # Set i_rms to 0 if it's less than 0.4
    if i_rms < 0.4:
        i_rms = 0.0
        
    i_rms = current
    apparent_power = v_rms * i_rms
    active_power = np.mean(voltages * current)  # Modified calculation for active power
    power_factor = active_power / apparent_power if apparent_power != 0 else 0
    phase_angle = np.arccos(power_factor)
    #reactive_power = apparent_power * np.sin(phase_angle)
    reactive_power = math.sqrt(max(apparent_power**2 - active_power**2, 0))  # Use max to avoid negative values due to floating-point errors

    return v_rms, i_rms, apparent_power, active_power, reactive_power, power_factor, phase_angle

print("Timestamp, V_RMS, I_RMS, Apparent Power, Active Power, Reactive Power, Power Factor, Phase Angle")

while True:
    # Read voltage samples from the sensor
    voltages = read_voltage_samples()

    # Get calibrated voltage and current from the current transformer
    calibrated_voltage, calibrated_current = current_transformer.get_measurements()

    # Calculate power parameters
    v_rms, i_rms, apparent_power, active_power, reactive_power, power_factor, phase_angle = calculate_power_parameters(voltages, calibrated_current)

    # Get current timestamp
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Print the values
    print(f"{timestamp}, {v_rms:.8f}, {i_rms:.8f}, {apparent_power:.8f}, {active_power:.8f}, {reactive_power:.8f}, {power_factor:.8f}, {np.degrees(phase_angle):.8f}")

    time.sleep(1)
