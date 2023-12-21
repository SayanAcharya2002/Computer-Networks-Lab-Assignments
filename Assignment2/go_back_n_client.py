from client import Listener
from convention import *
import threading,time

class go_back_n_listener(Listener):
  
  
  def start_listener(self,host_name,port):
    addr=(host_name,port)
    temp_thread=threading.Thread(target=self.establish_connection,args=[addr])
    temp_thread.start()

  def establish_connection(self,addr):
    self.sock.connect(addr)
    while True:
      msg=self.sock.recv(MAX_LEN_MSG).decode(FORMAT_MSG)
      msg=self.error_maker(msg)

      if msg==EXIT_MESSAGE:
        print("closing client node")
        self.sock.close()
        return
      if Listener.error_detect_parity(msg):
        print(f"Faulty Message Received by {self.client_id}!")
        continue
      
      message,serial_number=Listener.decode(msg)
      print(f"INCOMING MESSAGE FOR SERIAL:{serial_number} by {self.client_id}")
      print(f"{message}")

      send_msg=f"ACK {serial_number}"
      self.sock.send(send_msg.encode(FORMAT_MSG))