# pi-particle-sensor
Sensor interface for real-time particulate monitoring using the SPS30 and Raspberry Pi, with CSV logging support

### Preparing the Pi
Type  `sudo raspi-config` into the terminal. Go to `Interface Options` and select `Serial port`. Say no to "Would you like a login shell to be accessible over serial?" and yes to "Would you like the serial port hardware enabled?". Then, reboot using 

```bash
sudo reboot
```

This alone didn't work for me, so after rebooting, you may need to add this line to the config: 

```bash
enable_uart=1
```

You can open the config using 

```bash 
sudo nano /boot/config.txt
```

You might need to reboot again after doing this? 

After rebooting and connecting the sensor, type 

```bash
ls -l /dev/serial*
```

into the terminal to find what serial port the sensor is connected to, and change the script to that port.

### Hardware connections:

| SPS30 Pin | Wire Color | Raspberry Pi GPIO | Pin Number | Function             |
|-----------|------------|-------------------|-------------|---------------------|
| 1 VCC     | Red        | 5V                | Pin 2 or 4  | Power               |
| 2 RX      | Grey       | GPIO14 (TXD)      | Pin 8       | UART TX (from Pi)   |
| 3 TX      | Green      | GPIO15 (RXD)      | Pin 10      | UART RX (to Pi)     |
| 4 SEL     | Yellow     | —                 | —           | Leave unconnected   |
| 5 GND     | Black      | GND               | Pin 6       | Ground              |

For more detailed connections, see the attached Fritzing schematic.


### Dependencies:
The dependencies can be found in the requirements.txt file. A user should be able to install them using:
```bash
cd sps30-pi
pip install -e .
```


### Running the code on startup
1) Move your script somewhere permanent

```bash
mkdir -p /home/pi/sps30
cp particles.py /home/pi/sps30/
```

2) Move the included service file (currently named $\texttt{sps30.service}$ to the $\texttt{systemd}$ directory (double-check the pi name and filepath)
   
```bash
sudo cp sps30.service /etc/systemd/system/
```

4) Enable and start from the service file:
```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable sps30.service
sudo systemctl start sps30.service
```
Now reboot the Pi.

You can check its status at any point using

```bash
sudo systemctl status sps30.service
```
