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
                    #print(len(data))
                    msg = ""
                    for garage in data:
                        msg += str("\nGarage Name: " + garage['name'] + "\nGarage Access Level: " + str(garage['currentAccess']) + "\nPercentage Full: " + str(garage['percentage']) + "\n")
                    conn.sendall(msg.encode())
            # Misc CSE Class Info
            elif client_msg.__contains__('cse-class-info'):
                resp = requests.get('https://content.osu.edu/v2/classes/search?q=CSE')
                min_num = 0
                max_num = 9999
                try:
                    min_num = client_msg.split()[1]
                    max_num = client_msg.split()[2]
                except:
                    msg = str("\nAn Error Occured Parsing Arguments.\nUsage: cse-class-info <min-course-num> <max-course-num>")
                courses = resp.json()['data']['courses']
                msg = ""
                #print(json.dumps(courses, indent=4, sort_keys=True))
                for course in courses:
                    print(json.dumps(course, indent=4, sort_keys=True))
                    class_code = int(course['course']['catalogNumber'].replace("H",""))
                    if class_code >= int(min_num) and class_code <= int(max_num):
                        msg += str("\nCourse: CSE " + str(class_code) + "\nCourse Title: " + course['sections'][0]['courseTitle'] + "\nCourse Desc: " + course['course']['description'] + "\nCredit Hrs: " + str(course['course']['maxUnits']) + "\n")
                conn.sendall(msg.encode())
            # Misc Dining Hall Info
            elif client_msg == 'dining-info':
                resp = requests.get('https://content.osu.edu/v2/api/v1/dining/locations')
                if(resp.status_code == 200):
                    data = resp.json()['data']['locationsWithGeoCode']
                    msg = ""
                    for dining_hall in data:
                        food_list = ""
                        for food in dining_hall['cuisines']:
                            food_list = "".join(food['cuisineType'])
                        msg += str("\nDining Hall: " + dining_hall['locationName'] + "\nAddress: " + dining_hall['address1'] + "\nDining Style: " + dining_hall['diningStyle'] + "\nFood Types: " + food_list + "\n")
                    conn.sendall(msg.encode())
            # After that its general cleanup/documentation/"good practice refactoring" and im done.
            else:
                msg = "Invalid Command: " + client_msg + "\nList of Commands: \n\nbus-routes <route>\ncse-class-info <min-course-num> <max-course-num>\ngarage-info\ndining-info\nexit\n"
                conn.sendall(msg.encode())
                