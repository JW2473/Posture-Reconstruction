import matplotlib.pyplot as plt
import numpy as np

def millis(time):
    timelist = time.split(':')
    t = int(timelist[0])*3600000+int(timelist[1])*60000+float(timelist[2])*1000
    if int(timelist[0]) < 5:
        t += 24*3600000
    return t
interval = 10000
'''
with open('9008.csv') as f:
    l = f.readline();
    strlist = l.split(',')
    tw0 = int(strlist[-2])
    tpi0 = millis(strlist[-1])
    tw = int(strlist[-2]) + interval
    tpi = millis(strlist[-1]) + interval
    count1 = 0;
    count2 = 0;
    result1 = [];
    result2 = [];
    result3 = [];
    while l:
        strlist = l.split(',')
        if int(strlist[-2]) < tw:
            count1 += 1
        else:
            #print(count1)
            result1.append(count1)
            count1 = 0
            tw += interval
        if millis(strlist[-1]) < tpi:
            count2 += 1
        else:
            result2.append(count2)
            result3.append(millis(strlist[-1]) - tpi0 - int(strlist[-2]) + tw0)
            count2 = 0
            tpi += interval
        l = f.readline()
'''
n = 0
with open('9009.csv') as f:
    with open('9008.csv') as g:
        l1 = f.readline()
        l2 = g.readline()
        result = []
        while l1:
            n = n + 1
            if n%10 == 0:
                strlist1 = l1.split(',')
                strlist2 = l2.split(',')
                result.append(millis(strlist1[-1]) - millis(strlist2[-1]) - int(strlist1[-2]) + int(strlist2[-2]))
            l1 = f.readline()
            l2 = g.readline()
result = np.asarray(result)
#result1 = np.asarray(result1)
#result2 = np.asarray(result2)
#result3 = np.asarray(result3)
t = np.arange(0.0, len(result), 1)
plt.plot(t, result)
plt.show()

        


        
