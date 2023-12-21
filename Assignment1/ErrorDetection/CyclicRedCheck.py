from .Misc import LengthMismatchException,InvalidBinaryString,validate_binary_string
from collections import deque

class CyclicRedCheck:

  def __str__(self):
    return f"CyclicRedCheck with poly {self.poly}"

  def __init__(self,poly:str):
    validate_binary_string(poly)
    self.poly=poly
  
  def validate_string(self,s:str)->bool:
    if(not validate_binary_string(s)):
      raise InvalidBinaryString()
  
  def get_redundancy(self,s:str)->str:
    if len(s)<len(self.poly):
      raise LengthMismatchException("Length of data smaller than length of encoder")
    s+='0'*(len(self.poly)-1)
    val=int(self.poly,base=2)
    big=0
    for i in range(len(s)):
      big=(big<<1)+(ord(s[i])-ord('0'))
      if(big==0):
        continue
      size_big=len(bin(big)[2::])
      if(size_big==len(self.poly)):
        big^=val

    return bin(big)[2::].rjust(len(self.poly)-1,'0')

  def create_redundant_frame(self,s:str)->str:
    self.validate_string(s)
    return s+self.get_redundancy(s)

  def is_valid_frame(self,s:str)->bool:
    try:
      self.validate_string(s)
    except:
      return False
    return self.get_redundancy(s)=='0'*(len(self.poly)-1)

  




if __name__=="__main__":
  # obj=CyclicRedCheck("11001")
  # frame=obj.create_redundant_frame("110011")
  # print(frame)
  # print(obj.is_valid_frame(frame))

  import sys
  file_name=sys.argv[1]
  with open(file_name,'r') as f:
    for i in f.readlines():
      i=i.strip('\r\n').strip('\n')
      obj=CyclicRedCheck(poly="11001")
      red=obj.get_redundancy(i)
      frame=obj.create_redundant_frame(i)
      print(f"input data: {i}")
      print(f"redundancy: {red}")
      print(f"output data: {frame}")