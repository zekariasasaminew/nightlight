import time
from seeed_dht import DHT
import paho.mqtt.client as mqtt
import json
from os import path
import csv
from datetime import datetime

id = 'c2b67ec5-3744-4559-b8b2-309dab7bd0f1'
client_name = id + 'temperature_sensor_client'
client_telemetry_topic = id + '/telemetry'
temperature_file_name = 'temperature.csv'
fieldnames = ['date', 'temperature']

if not path.exists(temperature_file_name):
    with open(temperature_file_name, mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

sensor = DHT("11", 5)

def handle_telemetry(client, userdata, message):
    payload = json.loads(message.payload.decode())
    with open(temperature_file_name, mode='a') as temperature_file:
        temperature_writer = csv.DictWriter(temperature_file, fieldnames=fieldnames)
        temperature_writer.writerow({
            'date': datetime.now().astimezone().replace(microsecond=0).isoformat(),
            'temperature': payload['temperature']
        })

mqtt_client.on_message = handle_telemetry
mqtt_client.subscribe(client_telemetry_topic)

while True:
    _, temp = sensor.read()
    telemetry = json.dumps({'temperature': temp})
    mqtt_client.publish(client_telemetry_topic, telemetry)
    time.sleep(10 * 60)
