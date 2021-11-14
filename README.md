# python_systemstats
Reads Linux System statistics, like System Load, CPU/Ram Usage and Disk utilization with a python script. Also you can publish the data to a MQTT Broker. So it is possible to use the data somewhere else, for example in your smarthome enviroment. For that usage, there is a homie convention based script, which you can run as systemd service.

# Requirements
you need to install the following requirements for python3
```bash
apt update && apt install python3 python3-pip python3-paho-mqtt python3-gpiozero python3-psutil python3-systemd

# or via pip3
pip3 install paho-mqtt
pip3 install psutil
pip3 install gpiozero
pip3 install systemd
```
Also you should have a [MQTT Broker](https://www.laub-home.de/wiki/Eclipse_Mosquitto_Secure_MQTT_Broker_Docker_Installation)

Thats enough for a short test:
```bash
cd /usr/local/sbin
wget https://github.com/alaub81/python_systemstats/raw/main/systemstats.py
chmod +x systemstats.py 
systemstats.py

```
Now you should see the following output:
```txt
---System Informations---
System Uptime: 19:40:41.538989 - 1181 min
CPU Temperatur: 37.4 °C
CPU Usage: 1 %
Load average: 0.23 0.25 0.16
Ram Total: 368.4 MiB
Ram Used: 35.7 MiB
Ram Free: 137.0 MiB
Ram Usage: 28.3 %
Disk Total: 29.0 GiB
Disk Used: 2.1 GiB
Disk Free: 25.7 GiB
Disk Usage: 7.4 %
```

# Installing the systemstats-homie.py Script as systemd service
Installation is easy, just download the `systemstats-homie.py` and `systemstats-homie.service`, configure them und ready it is.

```bash
cd /usr/local/sbin
wget https://github.com/alaub81/python_systemstats/raw/main/systemstats-homie.py
chmod +x systemstats-homie.py 
nano systemstats-homie.py
```
Now configure the part on top of the script with your data.
After that, just install the systemd service and start it:
```bash
cd /etc/systemd/system
wget https://github.com/alaub81/python_systemstats/raw/main/systemstats-homie.service
systemctl daemon-reload
systemctl enable systemstats-homie.service
systemctl start systemstats-homie.service
```
Now check if everything is running
```bash
systemctl status systemstats-homie.service
```
and also check the data is published to the mqtt broker.

# More Informations
you can find more informations about the scripts [here](https://www.laub-home.de/wiki/Python_System_Status_Script). Sorry its written in german.
