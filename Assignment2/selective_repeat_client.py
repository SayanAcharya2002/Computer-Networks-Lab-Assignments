import socket
import threading
from client import Listener
from convention import *

class selective_repeat_listener(Listener):
  def __init__(self, error_delay_func, client_id):
    super().__init__(error_delay_func, client_id)

  def start_listener(self,host_name,port):
    addr=(host_name,port)
    temp_thread=threading.Thread(target=self.establish_connection,args=[addr])
    temp_thread.start()

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
        send_msg="NAK -1"
        self.sock.send(send_msg.encode(FORMAT_MSG))

        continue
      
      message,serial_number=Listener.decode(msg)
      print(f"INCOMING MESSAGE FOR SERIAL:{serial_number} by {self.client_id}")
      print(f"{message}")

      send_msg=f"ACK {serial_number}"
      self.sock.send(send_msg.encode(FORMAT_MSG))
