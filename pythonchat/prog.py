import socket
import threading
import sys 

PORT=8080
ADDR=('192.168.0.102',PORT)#replace '192.168.0.102' with the IP of your machine
FORMAT='utf-8'
DISCONNECT='quit'
HEADER=1000
c = True

def sendmessage(conn):
    global name
    global c 
    while c:
        msg =input('')
        if msg == DISCONNECT:
            print('connection terminated')
            c = False
        msg = '@'+name+']           '+msg 
        msg =msg.encode(FORMAT)
        msglength =len(msg)
        sendlength =str(msglength).encode(FORMAT)
        sendlength += b''*(HEADER - len(sendlength))
        conn.send(sendlength)
        conn.send(msg)
    conn.close()

def receivemessage(conn, addr):   
    global c
    while c:
        msglength = conn.recv(HEADER).decode(FORMAT)
        
        if msglength:
            msglength = int(msglength)
            msg = conn.recv(msglength).decode(FORMAT)
            print(f'[{addr}{msg}')
            if msg == DISCONNECT:
                print('client terminated the connection')
                c= False
    conn.close()


def server():

    serversock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.bind(ADDR)
    print(f'Listening for a connection on PORT:{PORT}')
    serversock.listen(1)
    conn, addr=serversock.accept()
    print(f'Connected to [{addr}]')
    sendthread= threading.Thread(target=sendmessage, args=(conn,))
    sendthread.start()
    receivethread= threading.Thread(target=receivemessage, args=(conn, addr))
    receivethread.start()

   


def client():
    clientsock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerip=input('Enter the IP of the host you want to connect to')
    serveradd=(peerip, PORT)
    clientsock.connect(serveradd)
    print(f'Connected to [{peerip, PORT}]')
    sendthread= threading.Thread(target=sendmessage, args=(clientsock,))
    sendthread.start()
    receivethread= threading.Thread(target=receivemessage, args=(clientsock, serveradd))
    receivethread.start()


name=input('Please enter a name: ')

while True:
    choice=input('Type [listen] if you want to listen for connections or type [connect] if you want to establish connections:\n')
    if choice == 'listen':
        server()
        break
    elif choice == 'connect':
        client()
        break
    else:
        print('enter a valid option')



   


            
