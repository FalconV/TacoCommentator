#  #!/usr/bin/python

from __future__ import print_function
from threading import Thread
import socket
import sys
import Queue
import time
import serial





ser = serial.Serial('/dev/ttyUSB0', timeout=1, baudrate=115200)

def send(q):
    s = "0,0,0,0*324*\n"
    while True:
        try:
            s = q.get(False)
            if s == "END":
                return
        except Queue.Empty:
                pass
        print ('sending' + s)
        #write to serial
        ser.write(s)
        received = ser.readline()
        print (received)
        while received != "OK\r\n":
            #if the falcon waited too long for you
            if received == "TIMEOUT\r\n" or received == "MISS\r\n":
                #repeat yourself
                ser.write(s)
                #print 'RTX'
#                print ('resending: ' + s)
            else:
                pass
#                print (received)
            #listen to the falcon while you wait
            received = ser.readline()
#            print (received)

        time.sleep(1)

def get(q):
    s = '0,0,0,0*324*\n'
    while True:
        #q.put(s)
        #s = raw_input()
        s = ""
        if s == "END\n":
            q.put("END\n")
            return
        #process string
        #expected format: roll,pitch,throttle,yaw
        checksum = 0
        for c in s:
            checksum += ord(c)
        s = s + '*' + "%d" % checksum + '*\n'
        # mod the checksum because fuck that shit
        checksum %=2000
        #q.put(s)

def sock(q):

    #bind the socket to the port, MAKE SURE IP ADDRESS IS CORRECT EACH TIME $
   # server_address = ('172.25.194.109', 8892)
  #  print >>sys.stderr, 'starting up on %s port %s' % server_address
 #   socket.bind(server_address)

    #listen for incoming connections
#    sock.listen(1)
    ####socket setup####
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #bind the socket to the port, MAKE SURE IP ADDRESS IS CORRECT EACH TIME $
    server_address = ('172.25.194.109', 8896)
    print ('starting up on %s port %s' % server_address)
    sock.bind(server_address)

    #listen for incoming connections
    sock.listen(1)
    
    print ('this is thread3')

    print ('waiting for a connection')
    connection, client_address = sock.accept()
    
    while True:
        #wait for connection
        #print ('waiting for a connection')
        #connection, client_address = sock.accept()

        try:
            #print >>sys.stderr, 'connection from', client_address

            #receive the data in small chuncks and send back to client
            while True:
                data = connection.recv(32) #number is number of characters received
                checksum = 0
                for c in data[2:]:
                    checksum += ord(c)
                s = data[2:] + '*' + "%d" % checksum + '*\n'
                print ('received "%s"' % s)
                q.put(s)
                if data:
                    #print >>sys.stderr, 'sending data back to the client'
                    print ('sending data back to the client')
                    connection.sendall(data)
                    continue
                else:
                    #print >>sys.stderr, 'no more data from', client_address
                    print ('no more data from', client_address)
                    break
                #if data == "1111\n":
                #    break
                #else:
                #    pass
                
        finally:
            #clean up the connection
            print ('finally')
            connection.close()
    
queue = Queue.Queue()
thread1 = Thread(target=send, args=(queue,))
thread2 = Thread(target=get, args=(queue,))
thread3 = Thread(target=sock, args=(queue,))

print ('starting thread 1')
thread1.start()
print ('starting thread 2')
thread2.start()
print ('starting thread 3')
thread3.start()
print ('joining thread 1')
thread1.join()
print ('joining thread 2')
thread2.join()
print ('joining thread 3')
thread3.join()
print ('all done')
