from server import Server
from client import Listener
import threading,time,socket
from convention import *

from collections import deque

class selective_repeat_server(Server):
  def __init__(self, host_name, port, file_to_send, extra_delay_error_func, server_id, window: int = 1):
    super().__init__(host_name, port, file_to_send, extra_delay_error_func, server_id, window)
    self.all_messages=[]
    self.recv_dict=dict()
    self.time_sent_mappa=dict()
    self.queue=deque()


  def get_ack(self,client:socket.socket):
    #add serial numbers to the dict
    try:
      while True:
        full_ack=client.recv(MAX_LEN_MSG).decode(FORMAT_MSG)
        ack_type,serial_no=full_ack.split()
        serial_no=int(serial_no)
        
        if(ack_type=='NAK'):
          self.recv_dict[serial_no]=-1
        else:
          self.recv_dict[serial_no]=1
        
        print(f"received {ack_type} for {serial_no}")
    except:
      print("connection stopped from client side\n")
  
  def send_one_frame(self,serial_no,frame_content:str,client:socket.socket):
    try:
      client.send(frame_content.encode(FORMAT_MSG))
      timing=time.time()
      self.time_sent_mappa[serial_no]=timing
      self.queue.append((serial_no,timing))
      sleep(1)

    except Exception as e:
      print("Connection to server closed.\n")
      print(f"{e}")

  def handle_client(self, client: socket.socket, addr):
    self.all_messages,total_serial=self.encode(self.file_name)
    self.all_messages=self.all_messages[:-1:1]
    index=0

    #start receiver thread
    receiver_thread=threading.Thread(target=self.get_ack,args=[client])
    receiver_thread.start()

    while index!=len(self.all_messages)+self.window_len:
      prev_index=index-self.window_len
      serial_no_prev=prev_index+1

      if(serial_no_prev>=1 and (serial_no_prev not in self.recv_dict or self.recv_dict[serial_no_prev]==-1)):
        #wait for the timeout amount to pass
        cur_time=time.time()
        # print(f"gonna check serial no: {serial_no_prev}")
        if cur_time-self.time_sent_mappa[serial_no_prev]<DEFAULT_TIMEOUT_MSG:
          sleep(1)
          continue
          
        self.send_one_frame(serial_no_prev,self.all_messages[serial_no_prev-1],client)

        sleep(1) # give 1 second for buffering
  
      while(len(self.queue)>0 and self.queue[0][1]<time.time()):
        serial_no_now=self.queue[0][0]
        self.queue.popleft()
        if serial_no_now in self.recv_dict and self.recv_dict[serial_no_now]==1:
          continue
        # print("printing from here")
        self.send_one_frame(serial_no_now,self.all_messages[serial_no_now-1],client)
        

      if(index<len(self.all_messages)):
        
        message_to_send=self.error_maker(self.all_messages[index])
        self.send_one_frame(index+1,message_to_send,client)
        

        # client.send(message_to_send.encode(FORMAT_MSG))
        # print(f"len of msg is: {len(self.all_messages[index].encode(FORMAT_MSG))}")
        # sleep(1)
        
      index+=1

    try:
      while True:
        client.send(EXIT_MESSAGE.encode(FORMAT_MSG))
    except:
      print("connection closed from client side at end_msg\n")