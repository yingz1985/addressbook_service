from socket import*
from hw1 import mappings
from _thread import *
from struct import *
import sys
import time

#validate args from terminal
if(len(sys.argv)==2):
    print("Usage: python3 server.py server_name server_port")
    sys.exit(1)
elif(len(sys.argv)==1):
    host = '127.0.0.1'
    serverPort = 1069
elif(len(sys.argv)==3):
    host = sys.argv[1]
    try:
        serverPort = int(sys.argv[2])
    except:
        print("invalid port")
        sys.exit(1)
else:
    print("Unnecessary arguments entered, exiting..")
    sys.exit(1)


#bind to local host and a port>1024
#estalish TCP connection
server_socket = socket(AF_INET,SOCK_STREAM)
server_socket.bind((host,serverPort))
#can listn to up to 20 clients at once, the 21th client gets rejected connection
server_socket.listen(20)


print("waiting for connection...")
#received first two bytes of the packet first
#determines how much we need to receive for the query string
#if format is off, return 0, do not continue to read from socket
#return value is length of query string
def pre(conn):
    length = b""
    while(len(length)!=2):
        #read at most two bytes with blocking recv call
        #stream-based TCP connection does not guarentee packet delivery
        #not all bytes arrive at the same time
        #make multiple calls to conn.recv if possible
        try:
            message = conn.recv(2)
        except Exception as e:
            return 0
        if not message:
            return 0
        length+=message

    leng = unpack("cB",length)
    #verify that it's a query packet
    if(leng[0].decode()!='Q'):
        return 0
    else:
        try:
            #parse string length, and return
            value = int(leng[1])

            return value
        except:

            return 0

#read n string bytes from socket
#return an empty string if connection drops
#validation is not necessary since we're just reading a string
def readn(conn,n):

    bytes_read = 0
    message = b""   #byte object
    while bytes_read < n:#read n bytes from stream

        try:
            m = conn.recv(1024)
        except Exception as e:
            return b""

        if(len(m)==0):  #connection terminated

            return b""
        else:
            bytes_read+=len(m)
            message += m
            if(len(message)>n): #actual length of string is not consistent
                return b""

    return message



def client_response(conn,addr):
    while True:
        time.sleep(0.5)

        n = pre(conn)
        #either format is invalid, such as header type not Q, or connection terminated
        if(n==0):
            break
        else:
            m = readn(conn,n)
            #invalid string read, or connection terminated
            if(m==b""):
                break

        print("query received for ", m.decode())

        reply = send_message(m.decode())
        conn.sendall(pack_message(reply))


    print("disconnecting client from ",str(addr[1]),"...")
    conn.close()


#goes to "database" and tries to get mapping of email to name
def send_message(email):
    return mappings.map(email)

#format response message
def pack_message(s):
    return pack("cB%ds" % (len(s),), str.encode('R'),len(s),str.encode(s))

while(True):
    conn,addr = server_socket.accept()
    #for every new client, start a new thread to execute commands
    #a single client could possibly have multiple queries
    print("connected at address",str(addr[0])," through port ",str(addr[1]))
    start_new_thread(client_response,(conn,addr))

