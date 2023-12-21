from .Misc import InvalidBinaryString,LengthMismatchException,validate_binary_string

class VertRedCheck:

  def __str__(self):
    return "VertRedCheck"
  
  def validate_string(self,s):
    if(not validate_binary_string(s)):
      raise InvalidBinaryString()
  
  def get_redundancy(self,s:str)->str:
    val=0
    for i in s:
      if i=='1':
        val^=1
    return str(val)
  
  def create_redundant_frame(self,s:str)->str:
    self.validate_string(s)
    return s+self.get_redundancy(s)
  
  def is_valid_frame(self,s:str)->bool:
    try:
      self.validate_string(s)
    except:
      return False
    return self.get_redundancy(s)=='0'

if __name__=="__main__":
  # obj=VertRedCheck()
  # red=obj.create_redundant_frame("0110010")
  # print(red)
  # red=red[:-1]+chr(48+(49-ord(red[-1])))
  # print(obj.is_valid_frame(red))

  import sys
  file_name=sys.argv[1]
  with open(file_name,'r') as f:
    for i in f.readlines():
      i=i.strip('\r\n').strip('\n')
      obj=VertRedCheck()
      red=obj.get_redundancy(i)
      frame=obj.create_redundant_frame(i)
      print(f"input data: {i}")
      print(f"redundancy: {red}")
      print(f"output data: {frame}")
      print(f"is_valid: {obj.is_valid_frame(frame)}")