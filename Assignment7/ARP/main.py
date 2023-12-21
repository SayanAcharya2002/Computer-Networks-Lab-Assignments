from helper import Device
from typing import List
loop_back_addr="127.0.0.0"

all_devices:List[Device]=[]
all_clients=[]

with open('info.txt','r') as f:
  lines=[i.strip('\r\n').strip('\n') for i in f.readlines()]
  def get_input():
    index=0
    while index<len(lines):
      yield lines[index]
      index+=1
    return 
  iter_obj=get_input()
  n=int(next(iter_obj))
  for i in range(n):
    output=next(iter_obj).split()
    print(output)
    dev=Device((output[0],int(output[1])),((output[2],int(output[3]))),output[4],output[5])
    dev.start_device()
    all_devices.append(dev)
    if output[4]=='C':
      all_clients.append(dev)
  m=int(next(iter_obj))
  for i in range(m):
    a,b=next(iter_obj).split()
    a=int(a)
    b=int(b)
    all_devices[a-1].add_device(all_devices[b-1].server_addr)
    all_devices[b-1].add_device(all_devices[a-1].server_addr)

while True:
  inp=input() # device_index,ip_addr
  if inp.upper()=="EXIT":
    break
  inp=inp.split()
  all_devices[int(inp[0])-1].query_ip(inp[1])
