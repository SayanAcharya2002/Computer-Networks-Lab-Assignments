import socket,threading,random
from time import sleep


class Listener:
  def __init__(self,cl_ip,cl_port,se_ip,se_port):
    self.cl_ip=cl_ip
    self.cl_port=cl_port
    self.se_ip=se_ip
    self.se_port=se_port

    self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.sock.bind((cl_ip,cl_port))



  def start_listener(self):
    self.sock.connect((self.se_ip,self.se_port))
    index=0
    loop_index=0
    while True:
      data=self.sock.recv(4096)
      if data==('1'*16).encode('utf-8'):
        break
      rec_index,data=self.decode(data)
      if random.randint(0,1)==1:
        continue
      loop_index+=1
      # if loop_index%3==0:
      #   continue
      print(rec_index)
      if index==rec_index:
        print(f"received data: {data}")
        self.sock.send(f"ACK {index}".encode('utf-8'))
        index+=1

    print("closing client side")
    self.sock.close()


  def decode(self,data):
    data=str(data,encoding='utf-8')
    index=int(data[0:8],base=2)
    i=8
    actual_data=""
    while i<len(data):
      actual_data+=chr(int(data[i:i+8],base=2))
      i+=8
    return (index,actual_data)


client=Listener('127.0.0.1',9005,'127.0.0.1',8000)
client.start_listener()