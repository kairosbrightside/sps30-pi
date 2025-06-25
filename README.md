# pi-particle-sensor
Sensor interface for real-time particulate monitoring using the SPS30 and Raspberry Pi, with CSV logging support

### Preparing the Pi
Type $\texttt{sudo raspi-config}$ into the terminal. Go to $\texttt{Interface Option}$ and enable UART. Then, reboot using $\texttt{sudo reboot}$. 

This alone didn't work for me, so after rebooting, you may need to add this line to the config: $\texttt{enable_uart=1}$. You can open the config using $\texttt{sudo nano /boot/config.txt}$. You might need to reboot again after doing this? 

After rebooting and connecting the sensor, type $\texttt{ls -l /dev/serial*}$ into the terminal to find what serial port the sensor is connected to, and change the script to that port.

### Hardware connections:

| SPS30 Pin | Wire Color | Raspberry Pi GPIO | Pin Number | Function            |
|-----------|------------|-------------------|-------------|---------------------|
| 1 VCC     | Red        | 5V                | Pin 2 or 4  | Power               |
| 2 RX      | Grey       | GPIO14 (TXD)      | Pin 8       | UART TX (from Pi)   |
| 3 TX      | Green      | GPIO15 (RXD)      | Pin 10      | UART RX (to Pi)     |
| 4 SEL     | Yellow     | —                 | —           | Leave unconnected   |
| 5 GND     | Black      | GND               | Pin 6       | Ground              |
For more detailed connections, see the attached Fritzing schematic.


### Dependencies:
the dependencies can be found in the requirements.txt file

### Running the code on startup
1) Move your script somewhere permanent
Example directory: $\texttt{/home/pi/sps30/particles.py}$

2) Make it executable
$\texttt{chmod +x /home/pi/sps30/particles,py}$

3) make a systemd service file
$\texttt{sudo nano /etc/systemd/system/sps30.service}$

4) Paste the following text into that file:
[Unit]
Description=SPS30 Air Sensor Logger
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/sps30/particles.py <---- CHANGE TO YOUR FILEPATH	
WorkingDirectory=/home/pi/sps30 <--- may need to change
StandardOutput=journal
StandardError=journal
Restart=on-failure
User=pi <---- may need to change

[Install]
WantedBy=multi-user.target


5) Enable and start the service:
$\texttt{sudo systemctl daemon-reexec}$
$\texttt{sudo systemctl daemon-reload}$
$\texttt{sudo systemctl enable sps30.service}$
$\texttt{sudo systemctl start sps30.service}$

Now reboot the Pi.

You can check its status at any point using
$\texttt{sudo systemctl status sps30.service}$
