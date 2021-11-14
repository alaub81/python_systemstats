#!/usr/bin/python3
from gpiozero import CPUTemperature
import psutil
import datetime
import paho.mqtt.client as mqtt
import time, ssl, systemd.daemon

# set the variables
broker = "FQDN / IP ADDRESS"
port = 8883
mqttclientid = "clientid-systemstats-homie"
clientid = "clientid-systemstats"
clientname = "Clientname System Statistics"
nodes="systemstats"
username = "mosquitto"
password = "password"
insecure = True
qos = 1
retain_message = True
# Retry to connect to mqtt broker
mqttretry = 5
# how often should be a publish to MQTT (in Seconds)
publishtime = 30
# Show System Stat output
showinfo = False

# do the stuff
### Functions
def publish(topic, payload):
  client.publish("homie/" + clientid + "/" + topic,payload,qos,retain_message)

def on_connect(client, userdata, flags, rc):
  print("MQTT Connection established, Returned code=",rc)
  # homie client config
  publish("$state","init")
  publish("$homie","4.0")
  publish("$name",clientname)
  publish("$nodes",nodes)
  # homie node config
  publish(nodes + "/$name","System Statistics")
  publish(nodes + "/$properties","uptime,uptimemin,cputemp,cpuusage,load1,load5,load15,ramtotal,ramused,ramfree,rampercentused,disktotal,diskused,diskfree,diskpercentused")
  publish(nodes + "/uptime/$name","System Uptime")
  publish(nodes + "/uptime/$datatype","string")
  publish(nodes + "/uptimemin/$name","System Uptime in Minutes")
  publish(nodes + "/uptimemin/$unit","min")
  publish(nodes + "/uptimemin/$datatype","float")
  publish(nodes + "/cputemp/$name","CPU Temperature")
  publish(nodes + "/cputemp/$unit","°C")
  publish(nodes + "/cputemp/$datatype","float")
  publish(nodes + "/cpuusage/$name","CPU Usage")
  publish(nodes + "/cpuusage/$unit","%")
  publish(nodes + "/cpuusage/$datatype","float")
  publish(nodes + "/load1/$name","System Load 1")
  publish(nodes + "/load1/$datatype","float")
  publish(nodes + "/load5/$name","System Load 5")
  publish(nodes + "/load5/$datatype","float")
  publish(nodes + "/load15/$name","System Load 15")
  publish(nodes + "/load15/$datatype","float")
  publish(nodes + "/ramtotal/$name","Ram Total")
  publish(nodes + "/ramtotal/$unit","MiB")
  publish(nodes + "/ramtotal/$datatype","float")
  publish(nodes + "/ramused/$name","Ram Used")
  publish(nodes + "/ramused/$unit","MiB")
  publish(nodes + "/ramused/$datatype","float")
  publish(nodes + "/ramfree/$name","Ram Free")
  publish(nodes + "/ramfree/$unit","MiB")
  publish(nodes + "/ramfree/$datatype","float")
  publish(nodes + "/rampercentused/$name","Ram Usage")
  publish(nodes + "/rampercentused/$unit","%")
  publish(nodes + "/rampercentused/$datatype","float")
  publish(nodes + "/disktotal/$name","Disk Total")
  publish(nodes + "/disktotal/$unit","GiB")
  publish(nodes + "/disktotal/$datatype","float")
  publish(nodes + "/diskused/$name","Disk Used")
  publish(nodes + "/diskused/$unit","GiB")
  publish(nodes + "/diskused/$datatype","float")
  publish(nodes + "/diskfree/$name","Disk Free")
  publish(nodes + "/diskfree/$unit","GiB")
  publish(nodes + "/diskfree/$datatype","float")
  publish(nodes + "/diskpercentused/$name","Disk Usage")
  publish(nodes + "/diskpercentused/$unit","%")
  publish(nodes + "/diskpercentused/$datatype","float")
  # homie stae ready
  publish("$state","ready")

def on_disconnect(client, userdata, rc):
  print("MQTT Connection disconnected, Returned code=",rc)

def sensorpublish():
  publish(nodes + "/uptime","{}".format(uptime))
  publish(nodes + "/uptimemin","{:.0f}".format(uptime_min))
  publish(nodes + "/cputemp","{:.2f}".format(cpu_temp.temperature))
  publish(nodes + "/cpuusage","{:.1f}".format(cpu_usage))
  publish(nodes + "/load1","{:.2f}".format(load_1))
  publish(nodes + "/load5","{:.2f}".format(load_5))
  publish(nodes + "/load15","{:.2f}".format(load_15))
  publish(nodes + "/ramtotal","{:.0f}".format(ram_total))
  publish(nodes + "/ramused","{:.0f}".format(ram_used))
  publish(nodes + "/ramfree","{:.0f}".format(ram_free))
  publish(nodes + "/rampercentused","{:.0f}".format(ram_percent_used))
  publish(nodes + "/disktotal","{:.3f}".format(disk_total))
  publish(nodes + "/diskused","{:.3f}".format(disk_used))
  publish(nodes + "/diskfree","{:.3f}".format(disk_free))
  publish(nodes + "/diskpercentused","{:.0f}".format(disk_percent_used))

# running the Script
#MQTT Connection
mqttattempts = 0
while mqttattempts < mqttretry:
  try:
    client=mqtt.Client(mqttclientid)
    client.username_pw_set(username, password)
    client.tls_set(cert_reqs=ssl.CERT_NONE) #no client certificate needed
    client.tls_insecure_set(insecure)
    client.will_set("homie/" + clientid + "/$state","lost",qos,retain_message)
    client.connect(broker, port)
    client.loop_start()
    mqttattempts = mqttretry
  except :
    print("Could not establish MQTT Connection! Try again " + str(mqttretry - mqttattempts) + "x times")
    mqttattempts += 1
    if mqttattempts == mqttretry:
      print("Could not connect to MQTT Broker! exit...")
      exit (0)
    time.sleep(5)

# Tell systemd that our service is ready
systemd.daemon.notify('READY=1')

client.on_connect = on_connect
client.on_disconnect = on_disconnect

# finaly the loop
while True:
  try:
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime_min = (uptime.seconds+uptime.days*24*3600)/60
    cpu_temp = CPUTemperature()
    cpu_usage = psutil.cpu_percent(interval=1, percpu=False)
    load_1, load_5, load_15 = psutil.getloadavg()
    ram = psutil.virtual_memory()
    ram_total = ram.total / 2**20       # MiB.
    ram_used = ram.used / 2**20
    ram_free = ram.free / 2**20
    ram_percent_used = ram.percent
    disk = psutil.disk_usage('/')
    disk_total = disk.total / 2**30     # GiB.
    disk_used = disk.used / 2**30
    disk_free = disk.free / 2**30
    disk_percent_used = disk.percent
    sensorpublish()
    if showinfo == True:
      print("---System Informations---")
      print("System Uptime: %s - %.0f min" % (uptime, uptime_min))
      print("CPU Temperatur: {:.1f}".format(cpu_temp.temperature) + " °C")
      print("CPU Usage: {:.0f} %".format(cpu_usage))
      print("Load average: %.2f %.2f %.2f" % (load_1, load_5, load_15))
      print("Ram Total: %.1f MiB\nRam Used: %.1f MiB\nRam Free: %.1f MiB\nRam Usage: %.1f %%" % (ram_total, ram_used, ram_free, ram_percent_used))
      print("Disk Total: %.1f GiB\nDisk Used: %.1f GiB\nDisk Free: %.1f GiB\nDisk Usage: %.1f %%" % (disk_total, disk_used, disk_free, disk_percent_used))
    time.sleep(publishtime)

  except KeyboardInterrupt:
    print("Goodbye!")
    # At least close MQTT Connection
    publish("$state","disconnected")
    time.sleep(1)
    client.disconnect()
    client.loop_stop()
    exit (0)

# At least close MQTT Connection
print("Script stopped")
publish("$state","disconnected")
time.sleep(1)
client.disconnect()
client.loop_stop()
