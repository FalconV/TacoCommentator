#  #!/usr/bin/python

from __future__ import print_function
from threading import Thread
from multiprocessing import Process
import socket
import sys
import Queue
import time
import serial
import RPi.GPIO as GPIO

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
        if quad_attached:
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
#                   print ('resending: ' + s)
                else:
                    pass
#                   print (received)
                #listen to the falcon while you wait
                received = ser.readline()
#               print (received)

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
    
    #grabbing the pi ip
    print ('grabbing ip')
    ipsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ipsock.connect(("google.com", 8080))
    time.sleep(5)
    loc_ip = ipsock.getsockname()[0]
    print (loc_ip)
    ipsock.close()
    print ('ip grabbed')
    
    ####socket setup####
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    #bind the socket to the port, MAKE SURE IP ADDRESS IS CORRECT EACH TIME $
    server_address = (loc_ip, 8889)
    print ('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    print (loc_ip)

    #listen for incoming connections
    sock.listen(1)
    
    #print ('this is thread3')
    #wait for connection
    #print ('waiting for a connection')
    GPIO.output(awaiting_connection_led, 1)
    connection, client_address = sock.accept()
    GPIO.output(awaiting_connection_led, 0)

    while True:
        while True:

            try:
                #print >>sys.stderr, 'connection from', client_address
                print ('waiting on data')
                #receive the data in small chuncks and send back to client
                while True:
                    data = connection.recv(24) #number is number of characters received
                    print (data)
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
                        break
                    else:
                        #print >>sys.stderr, 'no more data from', client_address
                        print ('no more data from', client_address)
                        break
                        
            finally:
                #clean up the connection
                print ('first packet sent')
                #connection.close()

if __name__ == '__main__':
    loc_ip = ""
    GPIO.setmode(GPIO.BCM)
    awaiting_connection_led = 4
    GPIO.setup(awaiting_connection_led, GPIO.OUT)
    quad_attached = 0

    if quad_attached:
        ser = serial.Serial('/dev/ttyUSB0', timeout=1, baudrate=115200)
    queue = Queue.Queue()
    process1 = Process(target=send, args=(queue,))
    #process2 = Process(target=get, args=(queue,))
    process3 = Process(target=sock, args=(queue,))
    #thread1 = Thread(target=send, args=(queue,))
    #thread2 = Thread(target=get, args=(queue,))
    #thread3 = Thread(target=sock, args=(queue,))

    print ('starting thread 1')
    process1.start()
    #thread1.start()
    #print ('starting thread 2')
    #process2.start()
    #thread2.start()
    print ('starting thread 3')
    process3.start()
    #thread3.start()
    print ('joining thread 1')
    process1.join()
    #thread1.join()
    #print ('joining thread 2')
    #process2.join()
    #thread2.join()
    print ('joining thread 3')
    process3.join()
    #thread3.join()
    print ('all done')
