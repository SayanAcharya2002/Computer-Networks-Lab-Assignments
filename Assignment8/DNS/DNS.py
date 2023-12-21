import socket,threading,json,time

MAX_BUF_SIZE=4096

print_lock=threading.Lock()

def _print(*args,**kwargs):
  print_lock.acquire()
  print(args,kwargs)
  print_lock.release()

def get_new_ip():
  index=1
  while True:
    yield f"127.0.0.{index}"
    index+=1

get_new_ip=iter(get_new_ip()).__next__

class dns_packet:
  def __init__(self,ip,port,pid,data):
    self.ip=ip
    self.port=port
    self.pid=pid
    self.data=data
  
  def encode(self,format='utf-8'):
    return f"{self.ip} {self.port} {self.pid} {self.data}".encode(format)

  @classmethod
  def decode(cls,string,format='utf-8'):
    listy=str(string,encoding=format).split()

    return dns_packet(listy[0],int(listy[1]),int(listy[2]),' '.join(listy[3::]))


class Server:
  def __init__(self,ip,port,parent_server,is_root_server=False):
    self.ip=ip
    self.port=port
    self.parent_server=parent_server
    
    # _print(ip)
    self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    self.sock.bind((ip,port))

    self.is_root_server=is_root_server
    self.child_server=dict()

    self.domain_map=dict()

    self.threads=[]

    self.start_server()

  def get_addr(self):
    return (self.ip,self.port)

  def start_server(self):
    t=threading.Thread(target=self.listen,args=[],daemon=True)
    self.threads.append(t)
    t.start()

  # def add_device(self,addr):
  #   self.conneceted_devices.append(addr)

  def listen(self):
    while True:
      packet,addr=self.sock.recvfrom(MAX_BUF_SIZE)
      packet=dns_packet.decode(packet)
      t=threading.Thread(target=self.handle_packet,args=[packet,addr],daemon=True)
      self.threads.append(t)
      t.start()
  
  def peel_one_domain(self,string:str):#peeled part,rest
    listy=string.split('.')
    return listy[-1],'.'.join(listy[0:-1:]),len(listy)
  
  def remove_www(self,string:str):
    listy=string.split('.')
    index=0
    if listy[0]=="www":
      index+=1
    return '.'.join(listy[index::])

  def handle_packet(self,packet:dns_packet,prev_addr):
    data=packet.data.split()
    _print(self.ip,self.port,data)
    if data[0]=="query":
      if self.is_root_server:
        data[1]=self.remove_www(data[1])

      cur_dom,rest_dom,rest_len=self.peel_one_domain(data[1])
      if rest_len==1:#search ended
        ip='?'
        if cur_dom in self.domain_map:
          ip=self.domain_map[cur_dom]
        _print(packet.ip,packet.port,ip)
        self.send_packet(dns_packet(packet.ip,packet.port,packet.pid,f"reply {ip}"),(packet.ip,packet.port))
      else:
        if cur_dom not in self.child_server:
          self.send_packet(dns_packet(packet.ip,packet.port,packet.pid,f"reply ?"),(packet.ip,packet.port))
        else:
          self.send_packet(dns_packet(packet.ip,packet.port,packet.pid,f"query {rest_dom}"),self.child_server[cur_dom].get_addr())

    elif data[0]=="reply":
      if self.parent_server:
        self.send_packet(packet,self.parent_server)
      else:
        # _print(packet.ip,packet.port)
        self.send_packet(packet,(packet.ip,packet.port))

    elif data[0]=="new":
      if self.is_root_server:
        data[1]=self.remove_www(data[1])

      cur_dom,rest_dom,rest_len=self.peel_one_domain(data[1])
      if rest_len==1:#search ended
        self.domain_map[cur_dom]=data[2]
        _print(f"domain added-> {rest_dom} {data[2]}")
      else:
        if cur_dom not in self.child_server:
          self.child_server[cur_dom]=Server(get_new_ip(),8000,self.get_addr())
          
        self.send_packet(dns_packet(packet.ip,packet.port,packet.pid,f"new {rest_dom} {data[2]}"),self.child_server[cur_dom].get_addr())
      


  def send_packet(self,packet:dns_packet,addr):
    self.sock.sendto(packet.encode(),addr)


class DNS:
  def __init__(self,ip_root,port_root):
    self.ip_root=ip_root
    self.port_root=port_root
    self.root_server=Server(ip_root,port_root,None,True)

  # def add_new_domain(self,dom_name,ip):
  #   self.root_server.send_packet(dns_packet('0',0,0,f"new {dom_name} {ip}"),(self.))

  # def query_domain(self,dom_name,query_machine_addr,pid):
  #   self.root_server.send_packet(dns_packet(*query_machine_addr,pid,f"query {dom_name}"))

class Client:
  def __init__(self,ip,port,dns_server:DNS):
    self.ip=ip
    self.port=port
    self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    self.sock.bind((ip,port))
    self.dns_server=dns_server
    self.pid=0

    self.pid_table=dict()
    self.threads=[]

    self.start_client()

  def start_client(self):
    t=threading.Thread(target=self.listen,args=[],daemon=True)
    self.threads.append(t)
    t.start()

  def listen(self):
    while True:
      packet,addr=self.sock.recvfrom(MAX_BUF_SIZE)
      packet=dns_packet.decode(packet)

      data=packet.data.split()

      if data[0]=="reply":
        if data[1]=='?':
          _print(f"no domain found for {self.pid_table[packet.pid]}")
        else:
          _print(f"domain found for {self.pid_table[packet.pid]} as {data[1]}")

  def query(self,dom_name):
    self.pid_table[self.pid]=dom_name
    self.send_packet(dns_packet(self.ip,self.port,self.pid,f"query {dom_name}"),self.dns_server.root_server.get_addr())
    self.pid+=1
  
  def add_new_domain(self,dom_name,ip):
    self.send_packet(dns_packet(self.ip,self.port,self.pid,f"new {dom_name} {ip}"),self.dns_server.root_server.get_addr())

  def send_packet(self,packet,addr):
    self.sock.sendto(packet.encode(),addr)


if __name__=="__main__":
  dns=DNS(get_new_ip(),8000)
  client=Client('127.0.1.0',8000,dns)
  mappa=json.load(open('dom.json'))
  for i,j in mappa.items():
    client.add_new_domain(i,j)
    time.sleep(0.5)
  
  while True:
    inp=input()
    if inp.upper()=="EXIT":
      break
    client.query(inp)

  # mappa=dict()
  # while True:
  #   inp=input()
  #   if inp.upper()=="EXIT":
  #     break
    
  #   inp=inp.split()
  #   mappa[inp[0]]=inp[1]
  # json.dump(mappa,open('dom.json','w'))
  
