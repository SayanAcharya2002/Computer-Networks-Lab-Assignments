from math import ceil
from .Misc import LengthMismatchException,InvalidBinaryString,validate_binary_string

class CheckSum:

  def __str__(self):
    return f"CheckSum with packet_len={self.packet_len}"

  def __init__(self,packet_len=4):
    self.packet_len=4

  def validate_string(self,s:str)->bool:
    if(not validate_binary_string(s)):
      raise InvalidBinaryString()
    if len(s)%self.packet_len!=0:
      raise LengthMismatchException(f"Length not multiple of {self.packet_len}")
  
  def get_redundancy(self,s:str)->str:
    n=len(s)
    val=0
    for i in range(n//self.packet_len):
      val+=int(s[i*self.packet_len:(i+1)*self.packet_len],base=2)
    bin_val=bin(val)[2::]
    if len(bin_val)%self.packet_len!=0:
      bin_val=bin_val.rjust(ceil(len(bin_val)/self.packet_len)*self.packet_len,'0')
    new_n=len(bin_val)
    sum=0
    for i in range(new_n//self.packet_len):
      sum+=int(bin_val[i*self.packet_len:(i+1)*self.packet_len],base=2)
    sum=bin(sum)[2::]
    sum=sum.rjust(self.packet_len,'0')
    # print(['1' if i=='0' else '1' for i in sum])
    return ''.join('1' if i=='0' else '0' for i in sum)

  def create_redundant_frame(self,s:str)->str:
    self.validate_string(s)
    return s+self.get_redundancy(s)

  def is_valid_frame(self,s:str)->bool:
    try:
      self.validate_string(s)
    except:
      return False
    return self.get_redundancy(s)=='0'*self.packet_len

if __name__=="__main__":
  # list_of_nums=[
  #   7,
  #   11,
  #   12,
  #   0,
  #   6,
  # ]
  # input_data=''.join(bin(i)[2::].rjust(4,'0') for i in list_of_nums)
  # print(input_data)
  # obj=CheckSum(packet_len=4)
  # red=obj.get_redundancy(input_data)
  # frame=obj.create_redundant_frame(input_data)
  # print(red)
  # print(obj.is_valid_frame(frame))

  import sys
  file_name=sys.argv[1]
  with open(file_name,'r') as f:
    for i in f.readlines():
      i=i.strip('\r\n').strip('\n')
      obj=CheckSum(packet_len=4)
      red=obj.get_redundancy(i)
      frame=obj.create_redundant_frame(i)
      print(f"input data: {i}")
      print(f"redundancy: {red}")
      print(f"output data: {frame}")
