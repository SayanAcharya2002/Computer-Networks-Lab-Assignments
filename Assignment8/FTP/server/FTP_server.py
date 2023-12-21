import socket,threading,os

MAX_BUF_SIZE=4096

class ftp_server:
  def __init__(self,ip,port):
    self.ip=ip
    self.control_port=port
    self.data_port=port+1

    self.control_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.data_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.control_sock.bind((ip,self.control_port))
    self.data_sock.bind((ip,self.data_port))
    
    self.control_sock.listen()
    self.data_sock.listen()

    self.threads=[]
    self.start_server()

  def start_server(self):
    t=threading.Thread(target=self.establish_connection,args=[],daemon=True)
    self.threads.append(t)
    t.start()

  def establish_connection(self):
    while True:
      control_client,control_addr=self.control_sock.accept()
      data_client,data_addr=self.data_sock.accept()

      t=threading.Thread(target=self.handle_connection,args=[control_client,control_addr,data_client,data_addr],daemon=True)
      self.threads.append(t)
      t.start()

  def get_file(self,file_name):
    with open(file_name,'r') as f:
      lines=[i.strip('\r\n').strip('\n') for i in f.readlines()]
      return '\n'.join(lines).encode('utf-8')
      
  def make_file(self,file_name,_data):
    with open(file_name,'w') as f:
      _data=str(_data,encoding='utf-8')
      f.write(_data)

  def handle_connection(self,control_client:socket.socket,control_addr,data_client:socket.socket,data_addr):
    #take commands from control and then act accordingly
    while True:
      command=control_client.recv(MAX_BUF_SIZE)
      command=str(command,encoding='utf-8')
      command=command.split()
      print(command)
      if command[0]=="ls":
        if len(command)==1:
          command.append('.')
        all_files=' '.join(os.listdir(command[1]))
        data_client.send(all_files.encode('utf-8'))

      elif command[0]=="download":
        file_name=command[1]
        if not os.path.exists(file_name):
          control_client.send("-1".encode('utf-8'))
        else:
          control_client.send(str(os.path.getsize(command[1])).encode('utf-8'))
          _data=self.get_file(file_name)
          data_client.send(_data)
      
      elif command[0]=="upload":
        file_name=command[1]
        _size=int(command[2])
        _data=data_client.recv(_size)
        print(_data)
        self.make_file(file_name,_data)

      elif command[0]=="exit":
        data_client.close()
        control_client.close()
        break


if __name__=="__main__":
  server=ftp_server('127.0.0.1',8000)
  server.establish_connection()