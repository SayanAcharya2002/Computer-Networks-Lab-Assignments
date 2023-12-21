from DHCP import Device

all_devices=[]
all_clients=[]
dhcp_server=None

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
    dev=Device(output[0],int(output[1]),is_dhcp=(output[-1]=='D'))
    dev.start_device()
    all_devices.append(dev)
    if output[-1]=='C':
      all_clients.append(dev)
  m=int(next(iter_obj))
  for i in range(m):
    a,b=next(iter_obj).split()
    a=int(a)
    b=int(b)
    all_devices[a-1].add_device(*all_devices[b-1].get_addr())
    all_devices[b-1].add_device(*all_devices[a-1].get_addr())

for i in range(n):
  print(all_devices[i].connected_devices)
  
while True:
  inp=input("give device index:") # device_index
  if inp.upper()=="EXIT":
    break
  all_devices[int(inp)-1].get_new_ip()
print("ending loop")