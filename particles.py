import time
import struct
import csv
import logging
from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection, ShdlcDeviceBase
from sensirion_shdlc_driver.command import ShdlcCommand

#using the logging library for logging
# we initially just wanted a console output but you could reconfigure it if you prefer something else
# we do have a csv that it logs to though
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("sps30_debug.log"),
        logging.StreamHandler()
    ]
)

# --- Custom SHDLC Commands ---
class StartMeasurementCommand(ShdlcCommand):
    def __init__(self):
        # 0x00 = StartMeasurement, payload = [0x01, 0x03] for mass concentration mode
        super().__init__(id=0x00, data=bytes([0x01, 0x03]), max_response_time=0.1)

class StopMeasurementCommand(ShdlcCommand):
    def __init__(self):
        # Must pass an empty payload as data
        super().__init__(id=0x01, data=b"", max_response_time=0.1)

class ReadMeasurementCommand(ShdlcCommand):
    def __init__(self):
        super().__init__(id=0x03, data=b"", max_response_time=0.1)

    def interpret_response(self, data):
        if len(data) != 40:
            raise ValueError(f"Unexpected data length: {len(data)} bytes")
        return struct.unpack(">10f", data)

# device class
class SPS30ManualDevice(ShdlcDeviceBase):
    def start_measurement(self):
        logging.debug("Sending StartMeasurement command...")
        self.execute(StartMeasurementCommand())

    def stop_measurement(self):
        logging.debug("Sending StopMeasurement command...")
        self.execute(StopMeasurementCommand())

    def read_measured_values(self):
        return self.execute(ReadMeasurementCommand())


# --- Main Execution ---
try:
    # change to your serial port
    # if it's connected to a pi 5, it will most likely be this port
    # but you can double-check if needed using the minicom tool
    # i think the serial ports on the pi 5 are weird so if you're using a different model you might get an error
    # typing the command " ls -l /dev/serial* " into your terminal should also return the correct port
    port = ShdlcSerialPort('/dev/ttyAMA0', baudrate=115200)  
    connection = ShdlcConnection(port)
    device = SPS30ManualDevice(connection, slave_address=0x00)
    logging.info("Connected to SPS30 device.")

    try:
        device.start_measurement()
        logging.info("Started measurement.")
    except Exception as e:
        logging.error(f"Start measurement failed: {e}")
        raise SystemExit("Could not start measurement. Check your port and connections?")

    time.sleep(2)  # Sensor warm-up time

    # logs to csv
    with open("sps30_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            'Timestamp', 'PM1.0', 'PM2.5', 'PM4.0', 'PM10',
            'NC0.5', 'NC1.0', 'NC2.5', 'NC4.0', 'NC10', 'Typical Particle Size'
        ])

        logging.info("Logging now! (press cntrl + C to stop)")

        while True:
            try:
                values = device.read_measured_values()
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                # reformat to reflect your preferred output 
                logging.info(f"PM2.5: {values[1]:.2f} µg/m³ | PM10: {values[3]:.2f} µg/m³")
                writer.writerow([timestamp] + list(values))
            except Exception as e:
                logging.warning(f"Measurement read failed: {e}")
            time.sleep(60) # sampling time; this is probably a little excessive so you can change it

except KeyboardInterrupt:
    logging.info("Measurement stopped by user.")

except Exception as e:
    logging.critical(f"Fatal error: {e}")

finally:
    try:
        device.stop_measurement()
        logging.info("Stopped measurement.")
    except Exception as e:
        logging.warning(f"Could not stop measurement: {e}")
    try:
        port.close()
        logging.info("Closed serial port.")
    except Exception:
        pass
