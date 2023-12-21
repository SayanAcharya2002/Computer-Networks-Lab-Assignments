import threading
import socket,random,time

from server import Server
from client import Listener

from go_back_n_server import go_back_n_server
from go_back_n_client import go_back_n_listener

from selective_repeat_server import selective_repeat_server
from selective_repeat_client import selective_repeat_listener

class Channel:
  def __init__(self,Server_type=Server,Client_type=Listener):
    self.Server_type=Server_type
    self.Client_type=Client_type
    self.HOST_IP=socket.getaddrinfo(socket.gethostname(),0)[1][-1][0]
    self.active_servers=[]
    self.active_listeners=[]

  @staticmethod
  def add_delay_error(s:str):
    time.sleep(random.randint(0,2))
    indices=random.sample(range(len(s)),random.randint(0,1))
    s_list=[i for i in s]
    for i in indices:
      s_list[i]=chr(1-ord(s_list[i])+2*ord('0')) #random bit flipping
    return ''.join(s_list)
  
  @staticmethod
  def null_delay_error(s:str):
    return s
  
  def add_server(self,ip:str,port:str,file_name:str,server_id,window:int=1):
    server=self.Server_type(ip,port,file_name,Channel.add_delay_error,server_id,window)
    self.active_servers.append(server)
    temp=threading.Thread(target=server.start_server,args=[])
    temp.start()

  def add_listener(self,ip:str,port:str,client_id):
    listener=self.Client_type(Channel.null_delay_error,client_id)#currently no error here
    self.active_listeners.append(listener)
    listener.start_listener(ip,port)


if __name__=="__main__":
  ip="127.0.0.1"
  port1=5003
  port2=5002


  """"
  Stop and wait
  """
  # channel=Channel()
  # channel.add_server(ip,port1,'file1.txt',1)
  # channel.add_listener(ip,port1,1)


  # channel.add_server(ip,port2,'file2.txt',2)
  # channel.add_listener(ip,port2,2)

  """"
  Go back N
  """


  # channel=Channel(Server_type=go_back_n_server,Client_type=go_back_n_listener)
  
  # channel.add_server(ip,port1,'file1.txt',1,2)
  # channel.add_listener(ip,port1,1)


  """"
  Selective Repeat
  """

  channel=Channel(Server_type=selective_repeat_server,Client_type=selective_repeat_listener)

  channel.add_server(ip,port1,'file1.txt',1,2)
  channel.add_listener(ip,port1,1)
