import socket
import sys

#create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#bind the socket to the port
server_address = ('172.25.194.109', 8895)
print ('starting up on %s port %s' % server_address)
sock.bind(server_address)

#listen for incoming connections
sock.listen(1)

while True:
	#wait for connection
	#print >>sys.stderr, 'waiting for a connection'
	print ('waiting for a connection')
	connection, client_address = sock.accept()

	try:
		#print >>sys.stderr, 'connection from', client_address
		print ('connection from', client_address)

		#receive the data in small chuncks and send back
		while True:
			data = connection.recv(32)
			#print >>sys.stderr, 'received "%s"' % data
			print ('received "%s"' % data)
			if data:
				#print >>sys.stderr, 'sending data back to the client'
#                                print ('sending data back to the client')
				connection.sendall(data)
			else:
				#print >>sys.stderr, 'no more data from', client_address
#                                print ('no more data from', client_address)
				break
			#if data == "1111\n":
			#	break
			#else:
			#	pass


	finally:
		#clean up the connection
		connection.close()
