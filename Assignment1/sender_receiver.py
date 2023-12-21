import ErrorDetection as ed
from random import sample

def encode_in_binary_string(s:str):
  ans=""
  for i in s:
    ans+=bin(ord(i))[2::].rjust(8,'0')
  return ans

def inject_errors(s:str,how_many:1):
  n=len(s)
  assert(n>=how_many)
  indices=sample(range(n),how_many)
  temp_list=[i for i in s]
  for i in indices:
    temp_list[i]=chr(49+(48-ord(s[i])))
  return ''.join(temp_list)

class Sender:
  def __init__(self,file_name,method,need_to_encode=False):
    self.file_name=file_name
    self.method=method
    self.need_to_encode=need_to_encode
  
  def make_data(self,output_file):
    listy=[]
    with open(self.file_name,'r') as f:
      for i in f.readlines():
        i=i.strip('\r\n').strip('\n')
        if self.need_to_encode:
          i=encode_in_binary_string(i)
        # print(i)
        output_data=self.method.create_redundant_frame(i)
        listy.append(output_data)
    with open(output_file,'w') as f:
      f.writelines(listy)

class Receiver:
  def __init__(self,method):
    self.method=method
  
  def validate_data(self,output_file):
    with open(output_file,'r') as f:
      for i in f.readlines():
        i=i.strip('\r\n').strip('\n')
        # print(i)
        valid=self.method.is_valid_frame(i)
        print(valid)

files=[
  "test_vert_red.txt",
  "test_long_red.txt",
  "test_check_sum.txt",
  "test_crc.txt",
]

methods=[
    ed.VertRedCheck(),
    ed.LongRedCheck(),
    ed.CheckSum(packet_len=4),
    ed.CyclicRedCheck(poly="11001"),
]

for i,j in zip(files,methods):
  send=Sender(file_name=i,method=j)
  send.make_data("output_"+i)

  rec=Receiver(method=j)
  rec.validate_data("output_"+i)

# send=Sender(file_name="test_encode_check_sum.txt",method=ed.CyclicRedCheck(poly="11001"),need_to_encode=True)
# send.make_data("output_encode_check_sum.txt")

# rec=Receiver(method=ed.CyclicRedCheck(poly="11001"))
# rec.validate_data("output_encode_check_sum.txt")
