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
n = 0
while n < len(IPs):
    data, addr = sock.recvfrom(1024);
    if "READY" in data:
        print(data)
        if addr[1] not in Ports and addr[0] in IPs:
            ind = IPs.index(addr[0])
            Ports[ind] = addr[1]
            Files[ind] = open(str(addr[1]) + ".csv", 'w')
            n += 1
            print(n)

for t in zip(IPs, Ports):
    sock.sendto("START", (t[0], t[1]))

while True:
    data, addr = sock.recvfrom(1024);
    print(data)
    try:
        ind = IPs.index(addr[0])
    except ValueError:
        continue
    data = data.split(',')
    data[0] = str(int(data[0])*3.1415926/180)
    data[1] = str(int(data[1])*3.1415926/180)
    data[2] = str(int(data[2])*3.1415926/180)
    timelist = datetime.now().strftime("%H:%M:%S.%f").split(':')
    t = str(int(timelist[0])*3600 + int(timelist[1])*60 + float(timelist[2]))
    Files[ind].write(data + ',' + t + '\n')
    Files[ind].flush()
