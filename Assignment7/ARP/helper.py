import socket,threading
MAX_DATA_SiZE=4096

print_lock=threading.Lock()

def _print(*args,**kwargs):
  print_lock.acquire()
  print(*args,**kwargs)
  print_lock.release()

class arp_entry:
  def __init__(self,mac_id,entry_type,max_time):
    self.mac_id=mac_id
    self.entry_type=entry_type
    self.max_time=max_time

class Device:
  def __init__(self,server_addr,reply_server_addr,mac_id,ip_addr=-1,):

    self.server_addr=server_addr #real ip addr/port
    self.reply_server_addr=reply_server_addr

    self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# udp socket
    self.sock.bind(self.server_addr)

    self.reply_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# udp socket
    self.reply_sock.bind(self.reply_server_addr)

    self.mac_id=mac_id
    self.ip_addr=ip_addr #pretend ip addr
    self.arp_table=dict()
    self.connec_devices=[]
    self.active_threads=[]
    
  def add_arp_entry(self,ip_addr,arp_entry_val):
    self.arp_table[ip_addr]=arp_entry_val

  def add_device(self,device_server_addr):
    self.connec_devices.append(device_server_addr)

  def start_device(self):
    t=threading.Thread(target=self.listen,args=[])
    self.active_threads.append(t)
    t.start()

  def listen(self):
    while True:#ip,reply_sock_ip,reply_sock_port
      data,parent_addr=self.sock.recvfrom(MAX_DATA_SiZE)
      data=str(data,encoding='utf-8').split(',')
      parent_reply_sock=(data[1],int(data[2]))
      
      
      #send data to all devices except the parent device
      for device in self.connec_devices:
        if device == parent_addr:
          continue
        self.sock.sendto(f"{data[0]},{self.reply_server_addr[0]},{self.reply_server_addr[1]}".encode('utf-8'),device)


      ans=None
      
      #get the output of the data sent. format: found,mac_id
      
      #leaf case

      if self.ip_addr==data[0]:
        ans=f"{self.mac_id}"
      else:
        #non leaf node case
        for i in range(len(self.connec_devices)-1):
          ret_data,addr=self.reply_sock.recvfrom(MAX_DATA_SiZE)
          string=str(ret_data,encoding='utf-8')
          split_string=string.split(',')
          if int(split_string[0])==1:
            ans=split_string[1]

      if ans:
        what_to_send=f"1,{ans}"
      else:
        what_to_send="0,Nothing"

      #send the ans back to parent
      self.sock.sendto(what_to_send.encode('utf-8'),parent_reply_sock)

  def query_ip(self,q_ip):
    
    if q_ip not in self.arp_table:
      
      for i in self.connec_devices:
        _print(f"trying device: {i}")
        self.sock.sendto(f"{q_ip},{self.reply_server_addr[0]},{self.reply_server_addr[1]}".encode('utf-8'),i)
        ans,addr=self.reply_sock.recvfrom(MAX_DATA_SiZE)
        ans=str(ans,encoding='utf-8').split(',')
        
        if int(ans[0])==1:
          self.arp_table[q_ip]=arp_entry(ans[1],'dynamic',-1)
          break
      if not ans or int(ans[0])==0:
        _print(f"not found any mac_id for ip:{q_ip}")
      else:
        _print(f"found. mac_id:ip found <-> {ans[1]},{q_ip}")
    else:
      _print(f"ip already in table. mac_id:ip found <-> {self.arp_table[q_ip].mac_id},{q_ip}")

