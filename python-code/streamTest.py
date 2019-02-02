import time
f1 = open('pipe1', 'w')
f2 = open('pipe2', 'w')
f3 = open('pipe3', 'w')
f4 = open('pipe4', 'w')
for i in range(0, 15):
    try:
        f1.write('0, 0, 0, 0, 0, 0, 0, 0, 0, ' + str(i) + '\n')
        f1.flush()
        f2.write('0, 0, 0, 0, 0, 0, 0, 0, 0, ' + str(i) + '\n')
        f2.flush()
        f3.write('0, 0, 0, 0, 0, 0, 0, 0, 0, ' + str(i) + '\n')
        f3.flush()
        f4.write('0, 0, '+ str(-3*i*3.1416/180) +', 0, 0, 0, 0, 0, 0, ' + str(i) + '\n')
        f4.flush()
    except BrokenPipeError:
        time.sleep(0.2)
        continue
    time.sleep(0.1)
