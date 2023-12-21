import socket
import threading
from convention import *

# socket.setdefaulttimeout(DEFAULT_TIMEOUT_MSG)


class Server:
  
  def __init__(self,host_name,port,file_to_send,extra_delay_error_func,server_id,window:int=1):
    self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.sock.bind((host_name,port))
    self.file_name=file_to_send
    self.error_maker=extra_delay_error_func
    self.server_id=server_id
    self.window_len=window

    self.sock.settimeout(DEFAULT_TIMEOUT_MSG)

  def start_server(self):
    self.sock.listen()
    while True:
      try:
        client,addr=self.sock.accept()
      except socket.timeout as tt:
        continue
      temp_thread=threading.Thread(target=self.handle_client,args=[client,addr])
      temp_thread.start()


  @staticmethod
  def make_16_bit_number(n):
    return bin(n)[2::].rjust(16,'0')

  @staticmethod
  def calculate_parity(s):
    val=0
    for i in s:
      val^=(ord(i)-ord('0'))
    return str(val)

  @staticmethod
  def encode(file_name):
    with open(file_name,"r") as f:
      message=''.join(f.readlines())
    encoded_message=""
    for i in message:
      encoded_message+=bin(ord(i))[2::].rjust(8,'0')
    listy=[]
    index=0
    serial_number=1
    while index<len(encoded_message):
      upto=index+MAX_LEN_CONTENT
      if upto>len(encoded_message):
        upto=len(encoded_message)

      main_message=Server.make_16_bit_number(serial_number)+encoded_message[index:upto]
      
      listy.append(main_message+Server.calculate_parity(main_message))
      index=upto
      serial_number+=1
    listy.append(EXIT_MESSAGE)
    return (listy,serial_number-1)

  def handle_client(self,client:socket.socket,addr):
    client.settimeout(DEFAULT_TIMEOUT_MSG)
    all_messages,total_serial=Server.encode(self.file_name)
    print([len(i) for i in all_messages])
    index=0
    while index!=len(all_messages):
      message_to_send=self.error_maker(all_messages[index])
      ret=client.send(message_to_send.encode(FORMAT_MSG))
      
      # print(f"msg sent: {message_to_send}, sender side return code: {ret}")
      
      try:
        msg=client.recv(MAX_LEN_MSG).decode(FORMAT_MSG)
      except socket.timeout as tt:
        print(f"timeout before receving ack from client by {self.server_id}")
        continue
      except ConnectionAbortedError as cae:
        print(f"connection to client closed by {self.server_id}.")
        break
      index+=1
    print(f"message sending done by {self.server_id}.")
    client.close()

if __name__=="__main__":
  # sender=Server("localhost",5000,'file1.txt',ZERO_ERROR_NO_DELAY_FUNC)
  sender=Server("localhost",5000,'file1.txt',SOME_ERROR_SOME_DELAY_FUNC)  
  sender.start_server()


