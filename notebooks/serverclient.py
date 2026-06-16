from socket import *

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

serverSocket.bind(('', serverPort))

print('The server is ready to receive')

while True:
    message, clientAddress = serverSocket.recvfrom(2048)

    modifiedMessage = message.decode().upper()

    serverSocket.sendto(modifiedMessage.encode(), clientAddress)