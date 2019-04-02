from socket import *
import sys
from struct import *

#encode query message into bytes
def pack_message(s):
    return pack("cB%ds" % (len(s),), str.encode('Q'),len(s),str.encode(s))

#a valid email address should only have one '@' character
#it can contain other special characters and doesn't necessarily end with '.com' or '.edu'
#for example user@[local_ip_address] is a valid email
#for simplicity I will only verify if there's only one and only @ character
def validateEmailAddr(email):
    if(email.find('@')==email.rfind('@') and email.find('@')!=-1 and email.strip().find(" ")==-1):
        return True
    else:
        return False

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
        message = conn.recv(2)
        if not message:
            return 0
        length+=message

    leng = unpack("cB",length)
    #verify that it's a response packet
    if(leng[0].decode()!='R'):
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
        m = conn.recv(1024)
        if(len(m)==0):  #connection terminated

            return b""
        else:
            bytes_read+=len(m)
            message += m
            if(len(message)>n): #actual length of string is not consistent
                return ""

    return message


#run in terminal with multiple clients
#by default client connects to the localhost server
#user may also choose to connect to a different server
if(len(sys.argv)==2):
    print("Usage: python client.py server_name server_port")
    sys.exit(1)
elif(len(sys.argv)==1):
    serverName = '127.0.0.1'
    serverPort = 1069
elif(len(sys.argv)==3):
    serverName = sys.argv[1]
    try:
        serverPort = int(sys.argv[2])
    except:
        print("invalid port")
        sys.exit(1)
else:
    print("Unnecessary arguments entered, exiting..")
    sys.exit(1)


client = socket(AF_INET,SOCK_STREAM)
try:
    client.connect((serverName,serverPort))
except Exception as e:
    print("Connection failed")


while(True):
    email = input("Enter an email: ")
    email = email.strip()
    #user did not enter anything and exit
    if(len(email)==0):
        break
    #quick check if the email address is invalid, refer to the method for details
    elif(validateEmailAddr(email)==False):
        print("Invalid email address entered")
        continue
    #if length of string is >255, too long to be encoded, we will reject it
    elif (len(email) > 255):
        print("\n~~~~~Operation not supported~~~~~\ncurrent database does not support email_addresses with more than 255 characters\n")
        continue
    client.sendall(pack_message(email))    #send correct format of query asking for email -> name


    n = pre(client)
    if (n == 0):
        break
    else:
        name = readn(client,n)
        if (name == b""):
            break

    #If not mapped in the database, disconnect session
    if(name.decode()=="Null"):
        print("email is currently not logged in our database")
        break
    print("From Server: "+ email+" belongs to ",name.decode())

client.close()
print("client session ending...")




