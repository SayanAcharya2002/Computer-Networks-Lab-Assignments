import socket
import threading
from convention import *

class Listener:
  def __init__(self,error_delay_func,client_id):
    self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.error_maker=error_delay_func
    self.client_id=client_id

  def start_listener(self,host_name,port):
    addr=(host_name,port)
    temp_thread=threading.Thread(target=self.establish_connection,args=[addr])
    temp_thread.start()
  
  @staticmethod
  def error_detect_parity(s:str)->bool:
    val=0
    for i in s:
      val^=(ord(i)-ord('0'))
    return val!=0

  @staticmethod
  def extract_message_part(s:str)->str:
    return s[16:-1]

  @staticmethod
  def decode(s:str)->str:
    serial_number=int(s[0:16],2)
    string=Listener.extract_message_part(s)

    # assert(len(string)%8==0)
    
    packs=len(string)//8
    message=""
    for i in range(packs):
      message+=chr(int(string[i*8:(i+1)*8],2))
    return (message,serial_number)

  def establish_connection(self,addr):
    self.sock.connect(addr)
    while True:
      msg=self.sock.recv(MAX_LEN_MSG).decode(FORMAT_MSG)
      msg=self.error_maker(msg)

      # print(f"msg len is: {len(msg)}")

      if msg==EXIT_MESSAGE:
        self.sock.close()
        return
      if Listener.error_detect_parity(msg):
        print(f"Faulty Message Received by {self.client_id}!")
        continue
      
      message,serial_number=Listener.decode(msg)
      print(f"INCOMING MESSAGE FOR SERIAL:{serial_number} by {self.client_id}")
      print(f"{message}")

      send_msg="ACK"
      self.sock.send(send_msg.encode(FORMAT_MSG))
      


if __name__=="__main__":
  listener=Listener(ZERO_ERROR_NO_DELAY_FUNC)
  # listener=Listener(SOME_ERROR_SOME_DELAY_FUNC)
  listener.start_listener('localhost',5000,)