#  #!/usr/bin/python

from __future__ import print_function
from multiprocessing import Process, Queue
import socket
import select
import sys
import datetime
import time
import serial
import RPi.GPIO as GPIO
import smtplib
import os

def send(q):
    s = "0,0,0,0*324*\n"
    q.put(s)
    while True:
        if not q.empty():
            try:
                s = q.get(False)
                if s == "END":
                    return
            except q.empty():
                pass
            #print ('sending ' + s)
            if quad_attached:
                #write to serial
                ser.write(s)
                received = ser.readline()
                #print (received)
                while received != "OK\r\n":
                    #if the falcon waited too long for you
                    if received == "TIMEOUT\r\n" or received == "MISS\r\n":
                        #repeat yourself
                        ser.write(s)
                        #print 'RTX'
#                       print ('resending: ' + s)
                    else:
                        pass
#                       print (received)
                    #listen to the falcon while you wait
                    received = ser.readline()
#                   print (received)

def sock(q):

    pack_count = 0
    rest_count = 0
    
    #grabbing the pi ip and setting up email port
    ipsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ipsock.connect(("gmail.com", 8080))
    except IOError:
        print('no internet detected')
        GPIO.Output(nowifi_led, 1)
    time.sleep(5)
    loc_ip = ipsock.getsockname()[0]

    #set up the piviewer html code
    #edit the file with the new local_ip
    f = open('/var/www/html/piviewer/index.template.html', 'r') 
    f2 = open('/var/www/html/piviewer/index.html.tmp', 'w') 
    htmlBeginning = f.read(2474) 
    htmlEnding = f.read() 
    f2.write(htmlBeginning) 
    f2.write(loc_ip) 
    f2.write(htmlEnding) 
    f2.close() 
    f.close() 
    f3 = open('/var/www/html/piviewer/index.html', 'w') 
    f4 = open('/var/www/html/piviewer/index.html.tmp', 'r') 
    htmlEntire = f4.read()
    f3.write(htmlEntire)
    f3.close()
    f4.close()
    os.remove('/var/www/html/piviewer/index.html.tmp')
        
    ####socket setup####
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#    sock.setblocking(0)
    sock.settimeout(10)
    close_flag = 0
    #bind the socket to the port, get ip and port from email
    port = 8888
    while port:
        try:
            server_address = (loc_ip, port)
            sock.bind(server_address)
        except IOError:
            port += 1
        else:
            eport = port
            port = 0
    print ('starting up on %s port %s' % server_address)

    #email ip and port
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("falconv.uh@gmail.com",'falconners')
    emsg = loc_ip + ' ' + str(eport)
    server.sendmail('ip_update@gmail.com','falconv.uh@gmail.com',emsg)
    server.quit()
    ipsock.close()

    #listen for incoming connections
    sock.listen(1)
    #wait for connection
    GPIO.output(awaiting_connection_led, 1)
    connection, client_address = sock.accept()
    GPIO.output(awaiting_connection_led, 0)
    close_flag = 0
    
    input = [sock, sys.stdin, connection]

    while True:
	print ('while True')
	if close_flag == 1:
	    pass
            pack_count = 0
            connection.close()
            GPIO.output(awaiting_connection_led, 1)
	    print ('before accepting connection')
	    connection, client_address = sock.accept()
	    print ('after accepting connection')
            GPIO.output(awaiting_connection_led, 0)
	    close_flag = 0
        try:
            #receive the data in small chuncks and put on queue
            while True:
		print ('second while True')
		r, w, e = select.select(input, [], [], 1.0)
		for s in r:
		    if s == sock: #handle getting new socket connections
			print ('new connection found')
			newClient, newAddress = sock.accept()
			input.append(newClient) #add new connection to list of selections
#		    elif s == sys.stdin and sys.stdin.read == 's': #handle keyboard inputs
#			for i in range(100):
#			    print ('keyboard input')
#			pass #we can figure out what we want to do later
		    else: #handle all other sockets
                        data = connection.recv(24)
		        print (data)
    		        for d in data[2:len(data)]:
    		            if d == '=':
			        dataToSend = '';
		            elif d == '\n':
                                if len(dataToSend) != 19:
                                    dataToSend = '1500,1500,1250,1500'
                                    close_flag = 1
			        break
		            else:
			        dataToSend += d;
                        #print ('data received')
                        if not data:
                            print ('data is empty')
                            close_flag = 1
                            dataToSend = '1500,1500,1250,1500'
                            break
                        if dataToSend[0:4] == 'close':
                            print ('closing conection')
                            close_flag = 1
                            break
                        #this security measure to be replicated and replaced on android app
                        if dataToSend[10:13] == '1250':
                            rest_count += 1
                            if rest_count > 100:
                                close_flag = 1
                                rest_count = 0
                                break
                        else:
                            rest_count = 0
                        #print (data)
                        checksum = 0
                        for c in dataToSend:
		            checksum += ord(c)
                        s = dataToSend + '*' + '%d' % checksum + '*\n'
		        print (datetime.datetime.now().strftime("%H:%M:%S.%f") + ' received %s' % s)
                        q.put(s)
                        break
                      
        finally:
            pack_count +=  1
            
    print ('connection closed')

if __name__ == '__main__':
    loc_ip = ""
    
    #status leds setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    program_running_led = 24
    nousb_led = 18
    awaiting_connection_led = 4
    nowifi_led = 25
    GPIO.setup(awaiting_connection_led, GPIO.OUT)
    GPIO.setup(nousb_led, GPIO.OUT)
    GPIO.setup(program_running_led, GPIO.OUT)
    GPIO.setup(nowifi_led, GPIO.OUT)
    GPIO.output(program_running_led, 1)
    GPIO.output(awaiting_connection_led, 0)
    GPIO.output(nousb_led, 0)
    GPIO.output(nowifi_led, 0)

    #set up serial over USB
    quad_attached = 1
    try:
        ser = serial.Serial('/dev/ttyUSB0', timeout=1, baudrate=115200)
    except serial.SerialException:
        try:
            ser = serial.Serial('/dev/ttyUSB1', timeout=1, baudrate=115200)
        except serial.SerialException:
            try:
                ser = serial.Serial('/dev/ttyUSB2', timeout=1, baudrate=115200)
            except serial.SerialException:
                #no usb is detected
                GPIO.output(nousb_led, 1)
                quad_attached = 0


    queue = Queue()
    process1 = Process(target=send, args=(queue,))
    process3 = Process(target=sock, args=(queue,))
    print ('starting thread 1')
    process1.start()
    print ('starting thread 3')
    process3.start()
    print ('joining thread 1')
    process1.join()
    print ('joining thread 3')
    process3.join()
    print ('all done')
