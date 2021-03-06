import socket
import subprocess
import threading
from datetime import datetime
'''
UDP_IP = "192.168.4.3"
UDP_PORT = 8080
MESSAGE = "Hello, World"

sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2.bind(("192.168.4.4", 8080))
'''
IPs = []
files = []
pipe = subprocess.Popen("arp -a|grep ESP", shell=True, stdout=subprocess.PIPE)
text = pipe.stdout.read().decode("utf-8")


class Receiver(threading.Thread):
    def run(self, UDP_IP, UDP_PORT, f):
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((UDP_IP, UDP_PORT))
            data, addr = sock.recvfrom(1024)
            f.write(data)
    

lines = text.split('\n') ;
for line in lines:
    if len(line) > 0:
        l = line.split(' ')
        #name = l[0].decode("unicode-escape")
        ip = l[1].encode('ascii', 'ignore')[1:-1]
        if True:
            IPs.append(ip)

Files = [None for i in range(0, len(IPs))]
Ports = [None for i in range(0, len(IPs))]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("192.168.4.1", 8080))
print(IPs)

channels = []
while n < len(IPs):
    data, addr = sock.recvfrom(1024);
    if addr[0] in IPs:
        channel = data.split(',')[1]
        if channel not in channels:
            ind = IPs.index(addr[0])
            Files[ind] = open(channel + ".csv", 'w')
            #subprocess.Popen("mkfifo pipe" + channel, shell=True)
            #Files[ind] = open("pipe" + channel, 'w')
            

print(len(channels))
while True:
    data, addr = sock.recvfrom(1024);
    print(data)
    try:
        channel = data.split(',')[1]
    except ValueError:
        continue
    #data = data.split(',')
    #data[0] = str(int(data[0])*3.1415926/180)
    timelist = datetime.now().strftime("%H:%M:%S.%f").split(':')
    t = str(int(timelist[0])*3600 + int(timelist[1])*60 + float(timelist[2]))
    Files[ind].write(data + ',' + t + '\n')
    Files[ind].flush()
