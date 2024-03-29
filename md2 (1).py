from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusException
import threading
import time
import paho.mqtt.client as mqtt
import json
# Define the Modbus settings
client = ModbusClient(method='rtu', port='/dev/ttyUSB0',  parity='N', baudrate=9600, bytesize=8, stopbits=1, timeout=2, strict=False)
client.connect()
# Slave IDs to read data from
slave_ids = [1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,127]
# Lock for synchronization between threads
lock = threading.Lock()

mqtt_topics = ["transmonk/mechmark/site1/command", "transmonk/mechmark/site1/reconfigure"]
# Define callback functions for MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the desired topics when connected
    for topic in mqtt_topics:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    try:
        # Decode JSON data from the message payload
        data = json.loads(msg.payload.decode("utf-8"))
        # Extract values from JSON data
        print(data)
        if msg.topic == "transmonk/mechmark/site1/command":
            if data.get("masterid") == "2":
            # Handle messages for topic1
            # Example: Do something with data from topic1
                register_address = 5
                values = data.get("workingvoltage")
                slave_addr = data.get("to")
                write_to_registers(register_address, int(values), int(slave_addr))
                pass
        elif msg.topic == "transmonk/mechmark/site1/reconfigure":
            if data.get("masterid") == "2":
            # Handle messages for topic2
            # Example: Do something with data from topic2
                register_address = 0
                values = data.get("newid")
                slave_addr = 127
                write_to_registers(register_address, int(values), int(slave_addr))
                pass
        else:
            # Handle other topics if needed
            print(f"invalid topic: {msg.topic}")
            pass

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

# Create a client instance for MQTT
client_mqtt = mqtt.Client()
client_mqtt.on_connect = on_connect
client_mqtt.on_message = on_message
# Connect to the MQTT broker
client_mqtt.connect("transmonkmqtt.coppercloud.in", 1883, 60)  # Replace with your MQTT broker information
# Start the MQTT loop in a separate thread
mqtt_thread = threading.Thread(target=client_mqtt.loop_start, daemon=True)
mqtt_thread.start()
def read_registers():
    while True:
        for slave_id in slave_ids:
            client_mqtt.publish("transmonk/data", slave_id) 

            try:
                # Specify the slave address and the range of registers to read
                response = client.read_holding_registers(address=0, count=22, slave=slave_id)
                # Process the data if the response is valid
                if response.isError():
                    # Handle Modbus exceptions
                    exception_code = response.get_exception_code()
                    print(f"Modbus Exception from Slave {slave_id}: {exception_code}")
                    time.sleep(3)
                else:
                    # Process the data as needed
                    values = response.registers
                    print(f"Slave {slave_id} Values: {values}")
                    # Publish values to MQTT
                    client_mqtt.publish("transmonk/mechmark/site1/data", json.dumps({"masterid":1, "deviceid": slave_id, "values": values}))  # Replace with your MQTT topic
                    time.sleep(3)
            except ModbusException as e:
                # Handle Modbus exceptions
                print(f"Modbus Exception from Slave {slave_id}: {e}")
                time.sleep(3)
            except Exception as e:
                # Handle other exceptions
                print(f"Error from Slave {slave_id}: {e}")
                time.sleep(3)
# Function to write to Modbus registers

def write_to_registers(register_address , values, unit):

    with lock:

        try:
            # Specify the slave address, register address, and values to write
            client.write_registers(register_address, values, slave=unit)
            print(f"Write successful to Slave {unit}, Address {register_address}, Values {values}")
            time.sleep(3)
        except ModbusException as e:
            # Handle Modbus exceptions
            print(f"Modbus Exception during write operation: {e}")
            time.sleep(3)
        except Exception as e:
            # Handle other exceptions
            print(f"Error during write operation: {e}")
            time.sleep(3)
# Start a thread for reading registers
read_thread = threading.Thread(target=read_registers, daemon=True)
read_thread.start()

# Wait for the threads to finish (you may remove this if your program has other work to do)
read_thread.join()
mqtt_thread.join()
# Close the Modbus connection
client.close()



