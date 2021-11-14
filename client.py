import socket
import configparser
import sys

# Read the server config file.
config = configparser.ConfigParser()
config.sections()
config.read('server.config')

# Set server params.
HOST = config['DEFAULT']['HOST']
PORT = int(config['DEFAULT']['PORT'])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        sendStr = input("Send something to the server: ")
        msg = sendStr.encode()
        s.sendall(msg)
        data = s.recv(64000).decode()
        if sendStr == "exit":
            print('Shutting Down Client...')
            break
        else:
            print(data)
