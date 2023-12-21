import socket
import threading
from time import sleep

print_mutex=threading.Lock()
def _print(*args,**kwargs):
  print_mutex.acquire()
  print(args,kwargs)
  print_mutex.release()

class Sender:
  def __init__(self,ip,port,file_name):
    self.ip=ip
    self.port=port
    self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.sock.bind((ip,port))
    self.threads=[]
    self.file_name=file_name
    self.received=[]

  def start_server(self):
    self.sock.listen()
    try:
      while True:
        client,addr=self.sock.accept()
        t=threading.Thread(target=self.sender,args=[client,addr])
        t.start()
        self.threads.append(t)
    except:
      _print("closing server side")
  def sender(self,client,addr):
    self.data_list=self.encode_data()
    n=len(self.data_list)
    self.received=[False]*n
    t=threading.Thread(target=self.get_ack,args=[client])
    t.start()
    self.threads.append(t)

    for i in range(n+3):
      prev_index=i-3
      while prev_index>=0 and self.received[prev_index]==False:
        _print(f"timeout for {prev_index}")
        _print(f"sending window: {prev_index}-{prev_index+2}")
        self.resend_window(prev_index,client)
      _print(f"sending frame: {i}")
      if i<n:
        self.send_one_frame(self.data_list[i],client)
    
    self.send_one_frame("1"*16,client)
    _print("closing server side.")
    self.sock.close()

  def resend_window(self,index,client):
    for i in range(index,index+3):
      if i<len(self.data_list):
        self.send_one_frame(self.data_list[i],client)
      
  def send_one_frame(self,string:str,client:socket.socket):
    client.send(string.encode('utf-8'))
    sleep(1)
  
  def get_ack(self,client):
    try:
      while True:
        data=client.recv(4096)
        data=str(data,encoding="utf-8")
        data=data.split()
        _print("ack_data",data)
        _print(f"received ack: {data[1]}")
        self.received[int(data[1])]=True
    except:
      _print("closing server side")

  def encode_data(self):
    string=""
    with open(self.file_name,'r') as f:
      for i in f.readlines():
        i=i.strip('\r\n').strip('\n')
        string+=''.join([str(bin(ord(j)))[2::].rjust(8,'0') for j in i])
    
    data_list=[]
    if len(string)%16!=0:
      string+="0"*8
    index=0
    for i in range(len(string)//16):
      data_list.append(str(bin(index)[2::].rjust(8,'0'))+string[i*16:i*16+16])
      index+=1
    
    return data_list


sender=Sender('127.0.0.1',8000,'file1.txt')
sender.start_server()