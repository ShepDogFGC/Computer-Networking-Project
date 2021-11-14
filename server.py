import socket
import configparser
import requests
import json
import sys

# Read the server config file.
config = configparser.ConfigParser()
config.sections()
config.read('server.config')

# Set server params & start the server.
HOST = config['DEFAULT']['HOST']
PORT = int(config['DEFAULT']['PORT'])
print("ShepServer has started! Listening on port " + PORT.__str__())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    # Send a msg that the server has started.
    with conn:
        print('Successful Connection! Connected by ', addr)
        while True:
            # Collect data and translate it into something more usable.
            data = conn.recv(64000)
            print("Client Sent:", data.decode())
            client_msg = (data.decode()).lower()
            
            ### Command Handling
            
            # Kill the server & the client.
            if client_msg == 'exit':
                print('ShepServer Shutting Down...')
                break
            # Get Active Busses on a specified route.
            elif client_msg.__contains__('bus-routes'):
                routes = ['CLN', 'CLS', 'ER', 'MC', 'BV', 'NE']
                try:
                    route = client_msg.split()[1].upper()
                except:
                    msg = str("\nInvalid Argument: " + route + "\nAcceptable Arguments: CLN, CLS, ER, MC, BV, NE\n")
                    conn.sendall(msg.encode())
                if routes.__contains__(route.upper()):
                    resp = requests.get('https://content.osu.edu/v2/bus/routes/' + route + '/vehicles')
                    if(resp.status_code == 200):
                        bus_data = resp.json()['data']['vehicles']
                        #print(json.dumps(resp.json(), indent=4, sort_keys=True))
                        if bus_data != []:
                            for bus in bus_data:
                                msg = str("Bus Destination: " + bus_data['destination'] + "\nIs Bus Delayed: " + bus_data['delayed'] + "\nBus Speed: " + bus_data['speed'] + " MPH")
                                conn.sendall(msg.encode())
                        else:
                            msg = str("\nNo Active Busses!\n")
                            conn.sendall(msg.encode())
                else:
                    msg = str("\nInvalid Argument: " + route + "\nAcceptable Arguments: CLN, CLS, ER, MC, BV, NE\n")
                    conn.sendall(msg.encode())
            # Spit out garage availability info        
            elif client_msg == 'garage-info':
                resp = requests.get('https://content.osu.edu/v2/parking/garages/availability')
                if(resp.status_code == 200):
                    data = resp.json()['data']['garages']
                    print(len(data))
                    msg = ""
                    for garage in data:
                        msg += str("\nGarage Name: " + garage['name'] + "\nGarage Access Level: " + str(garage['currentAccess']) + "\nPercentage Full: " + str(garage['percentage']) + "\n")
                    conn.sendall(msg.encode())
            # A classes command
            
            # A dining hall command
            
            # After that its general cleanup/documentation/"good practice refactoring" and im done.