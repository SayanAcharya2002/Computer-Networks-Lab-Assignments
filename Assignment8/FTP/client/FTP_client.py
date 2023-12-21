import os,socket,threading,time

MAX_BUF_SIZE=4096

class ftp_client:
  def __init__(self,ip,port):
    self.ip=ip
    self.port=port
    self.control_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.data_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.control_sock.bind((ip,port))
    self.data_sock.bind((ip,port+1))

  def connect_with_server(self,server_ip,server_port):
    self.control_sock.connect((server_ip,server_port))
    self.data_sock.connect((server_ip,server_port+1))

  def make_file(self,file_name,_data):
    with open(file_name,'w') as f:
      _data=str(_data,encoding='utf-8')
      f.write(_data)

  def get_file(self,file_name):
    with open(file_name,'r') as f:
      lines=[i.strip('\r\n').strip('\n') for i in f.readlines()]
      return '\n'.join(lines).encode('utf-8')

  def command(self,command):
    command=command.split()
    if command[0]=='ls':
      self.control_sock.send(' '.join(command).encode('utf-8'))
      _data=self.data_sock.recv(MAX_BUF_SIZE)
      _data=str(_data,encoding='utf-8')
      print(_data)

    elif command[0]=='download':
      new_file_name=command[2]
      self.control_sock.send(' '.join(command[0:2:]).encode('utf-8'))
      _size=self.control_sock.recv(MAX_BUF_SIZE)
      _size=int(_size)
      _data=self.data_sock.recv(_size)
      self.make_file(new_file_name,_data)

    elif command[0]=='upload':
      _size=os.path.getsize(command[1])
      command.append(str(_size))
      self.control_sock.send(' '.join(command).encode('utf-8'))

      _data=self.get_file(command[1])
      self.data_sock.send(_data)

    elif command[0]=='exit':
      self.control_sock.send(' '.join(command).encode('utf-8'))
      time.sleep(0.5)
      self.control_sock.close()
      self.data_sock.close()
    else:
      print("wrong command given. no action taken")

if __name__=="__main__":
  client=ftp_client('127.0.0.2',8000)
  client.connect_with_server('127.0.0.1',8000)
  while True:
    inp=input()
    inp=inp.lower()
    client.command(inp)
    if inp=='exit':
      break

# download file_name
# upload file_name new_file_name
# ls directory(optional)
# exit