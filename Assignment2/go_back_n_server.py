import threading
from server import Server
import socket
from convention import *
import time


class go_back_n_server(Server):
  
  def __init__(self, host_name, port, file_to_send, extra_delay_error_func, server_id,window_len=4):
    super().__init__(host_name, port, file_to_send, extra_delay_error_func, server_id)
    self.recv_set=set()
    self.window_len=4
    self.all_messages=[]
    self.time_sent_mappa={}
  
  def get_ack(self,client:socket.socket):
    #add serial numbers to the dict
    try:
      while True:
        full_ack=client.recv(MAX_LEN_MSG).decode(FORMAT_MSG)
        serial_no=int(full_ack.split()[-1])
        self.recv_set.add(serial_no)
        print(f"received ack for {serial_no}")
    except:
      print("connection stopped from client side")

  def send_window(self,client:socket.socket,index):
    print(f"sending window: {index} to {index+self.window_len}")
    for i in range(index,min(index+self.window_len,len(self.all_messages))):
      client.send(self.all_messages[i].encode(FORMAT_MSG))
      # print(f"len of msg is: {len(self.all_messages[i].encode(FORMAT_MSG))}")
      time_now=time.time()
      self.time_sent_mappa[i+1]=time_now
      sleep(1)

  
  def handle_client(self, client: socket.socket, addr):

    self.all_messages,total_serial=Server.encode(self.file_name)
    index=0
    self.all_messages=self.all_messages[:-1] # excluding the disconnect message

    
    #start receiver thread
    receiver_thread=threading.Thread(target=self.get_ack,args=[client])
    receiver_thread.start()

    while index!=len(self.all_messages)+self.window_len:
      prev_index=index-self.window_len
      serial_no_prev=prev_index+1

      while(serial_no_prev>=1 and serial_no_prev not in self.recv_set):
        #wait for the timeout amount to pass
        cur_time=time.time()
        # print(f"gonna check serial no: {serial_no_prev}")
        if cur_time-self.time_sent_mappa[serial_no_prev]<DEFAULT_TIMEOUT_MSG:
          sleep(1)
          continue
          
        self.send_window(client,prev_index)
        sleep(1) # give 1 second for buffering
  
      if(index<len(self.all_messages)):
        
        message_to_send=self.error_maker(self.all_messages[index])
        client.send(message_to_send.encode(FORMAT_MSG))
        # print(f"len of msg is: {len(self.all_messages[index].encode(FORMAT_MSG))}")
        
        self.time_sent_mappa[index+1]=time.time()
        sleep(1)
      index+=1

    try:
      while True:
        client.send(EXIT_MESSAGE.encode(FORMAT_MSG))
    except:
      print("connection closed from client side")

  def start_server(self):

    self.sock.listen()
    while True:
      try:
        client,addr=self.sock.accept()
      except socket.timeout as tt:
        continue
      temp_thread=threading.Thread(target=self.handle_client,args=[client,addr])
      temp_thread.start()
