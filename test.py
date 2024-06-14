import sys
import time,os

str = "time java -jar "+"code/"+sys.argv[1]+" < input.txt > mutual.txt"
#print(str)
real_start = time.time()
os.system(str)
os.system("python3 checker.py")
real_end = time.time()
print(f'总体时间: {real_end - real_start}')
