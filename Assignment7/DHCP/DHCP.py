import socket,threading,time

MAX_PACKET_SIZE=4096
print_lock=threading.Lock()

def _print(*args,**kwargs):
  print_lock.acquire()
  print(*args,**kwargs)
  print_lock.release()


class Packet:
  keys=[
    'src_ip',
    'src_port',
    'dest_ip',
    'dest_port',
    'pid',
    'data',
  ]
  def __init__(self,
              src_ip,src_port,
              dest_ip,dest_port,
              pid,data):
    self.src_ip=src_ip
    self.src_port=src_port
    self.dest_ip=dest_ip
    self.dest_port=dest_port
    self.pid=pid
    self.data=data

    self.mappa=dict(zip(Packet.keys,[
      src_ip,src_port,
      dest_ip,dest_port,
      pid,data,
    ]))
  
  def __getitem__(self,key_val):
    return self.mappa[key_val]

  def encode(self,format='utf-8'):
    string=f"{self.src_ip} {self.src_port} {self.dest_ip} {self.dest_port} {self.pid} {self.data}"

    return string.encode(format)

  @classmethod
  def decode(cls,string:str,format='utf-8'):
    parts=str(string,encoding=format).split()
    return Packet(parts[0],int(parts[1]),parts[2],int(parts[3]),parts[4],' '.join(parts[5::]))


class Device:
  def __init__(self,ip,port,is_dhcp=False):
    self.ip=ip
    self.port=port
    self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    self.sock.bind((ip,port))
    self.is_dhcp=is_dhcp
    if self.is_dhcp:
      self.dhcp_mutex=threading.Lock()
      self.dhcp_table=dict()

    self.dhcp_ip='?'
    self.dhcp_port=0
    self.active_dhcp_request=False

    self.routing_table=dict()
    self.connected_devices=[]
    self.ip_count=0
    self.pid=0
    self.pid_table=dict()
    self.assigned_ip='?'

    self.threads=[]
  
  def get_addr(self):
    return (self.ip,self.port)

  def add_device(self,ip,port):
    self.connected_devices.append((ip,port))

  def start_device(self):
    t=threading.Thread(target=self.listen,args=[])
    t.setDaemon(True)
    t.start()
    self.threads.append(t)

  def listen(self):
    while True:
      packet,addr=self.sock.recvfrom(MAX_PACKET_SIZE)
      packet=Packet.decode(packet) 
      t=threading.Thread(target=self.handle_packet,args=[packet,addr])
      t.setDaemon(True)
      t.start()
      self.threads.append(t)

  def add_to_routing_table(self,packet,addr):#(ip)->(ip,port)
    tup=(packet['src_ip'])
    if tup not in self.routing_table:
      self.routing_table[tup]=addr

  def give_new_ip(self):
    assert(self.is_dhcp)

    self.dhcp_mutex.acquire()
    
    assigned_ip=self.ip_count
    self.ip_count+=1
    ip= f"193.0.0.{assigned_ip}"
    
    self.dhcp_mutex.release()

    return ip

  def get_new_ip(self):
    t_start=time.time()
    while time.time()-t_start<=10:
      if self.assigned_ip=='?' and not self.active_dhcp_request:
        self.active_dhcp_request=True
        self.send_packet(Packet(self.ip,self.port,'?',0,0,f"query_dhcp_server"),('?',0))
        
    if self.assigned_ip=='?':
      _print("dhcp server finding or ip allocation failed!")
    else:
      _print(f"assigned ip is {self.assigned_ip}")


  def handle_packet(self,packet:Packet,addr):#this addr is previous socket
    self.add_to_routing_table(packet,addr)
    data=packet['data']
    if self.is_dhcp:
      if packet.dest_ip=='?':
        if data=="query_dhcp_server":
          _print(f"query_dhcp reached from {packet['src_ip']}")
          self.send_packet(Packet(self.ip,self.port,packet['src_ip'],packet['src_port'],packet['pid'],f"reply_dhcp_server {self.ip} {self.port}"),(packet['src_ip'],packet['src_port']))
        
    data=data.split()
    
    if packet.dest_ip==self.ip or packet.dest_ip=='?': #reached destination
      _print(data)
      if data[0]=="reply_dhcp_server":
        self.dhcp_ip=packet['src_ip']
        self.dhcp_port=packet['src_port']

        self.send_packet(Packet(self.ip,self.port,self.dhcp_ip,self.dhcp_port,0,f"query_new_ip"),(self.dhcp_ip,self.dhcp_port))

      elif data[0]=="query_new_ip":
        self.send_packet(Packet(self.ip,self.port,packet['src_ip'],packet['src_port'],packet['pid'],f"reply_new_ip {self.give_new_ip()}"),(packet['src_ip'],packet['src_port']))

      elif data[0]=="reply_new_ip":
        task_pid=self.pid
        self.pid+=1
        self.assigned_ip=data[1]

        #send an arp to see if exists
        self.send_packet(Packet(self.ip,self.port,'?',8000,task_pid,f"query_existing_ip {data[1]}"),('?',8000))
        self.pid_table[task_pid]='?'
        
        t_start=time.time()
        is_failed=False
        while time.time()-t_start<=5:
          if self.pid_table[task_pid]!='?' and self.pid_table[task_pid]=='1':
            #got the ans_to_query as invalid_ip
            self.assigned_ip='?'#the assigned ip
            is_failed=True
            break
          time.sleep(0.5)

        if not is_failed:
          _print(f"ip_allocation successful for {data[1]}.")
          self.send_packet(Packet(self.ip,self.port,self.dhcp_ip,self.dhcp_port,0,f"acquired_new_ip {self.assigned_ip}"),(self.dhcp_ip,self.dhcp_port))
        else:
          _print(f"ip_allocation failed for {data[1]}.")
          self.active_dhcp_request=False

      elif data[0]=="query_existing_ip":
        if data[1]==self.assigned_ip:
          self.send_packet(Packet(self.ip,self.port,packet['src_ip'],packet['src_port'],packet['pid'],"reply_existing_ip 1"))

      elif data[0]=="reply_existing_ip":
        self.pid_table[packet['pid']]=data[1]

      elif data[0]=='acquired_new_ip':
        self.dhcp_table[data[1]]=-1 # time limit
        self.active_dhcp_request=False
  
      elif packet.dest_ip!=self.ip:#on route
        self.send_packet(packet,(packet['dest_ip'],packet['dest_port']),set([addr]))
    
    elif packet.dest_ip!=self.ip:#on route
      self.send_packet(packet,(packet['dest_ip'],packet['dest_port']),set([addr]))

  def send_packet(self,packet,addr,exclude_list=set()):
    if addr in self.routing_table:
      self.sock.sendto(packet.encode(),self.routing_table[addr[0]])
    else:
      for dev in self.connected_devices:
        if dev not in exclude_list:
          self.sock.sendto(packet.encode(),dev)