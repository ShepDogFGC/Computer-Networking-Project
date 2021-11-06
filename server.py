import socket
import configparser

# Read the server config file.
config = configparser.ConfigParser()
config.sections()
config.read('server.config')

# Set server params.
HOST = config['DEFAULT']['HOST']
PORT = int(config['DEFAULT']['PORT'])

print("Server Started. Waiting on Client Connection...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Successful Connection! Connected by ', addr)
        while True:
            data = conn.recv(1024)
            print("Client Sent:", data.decode())
            if data == str.encode('Exit'):
                print('Shutting down server...')
                break
            print("Sending Resp to Client...")
            conn.sendall(data)