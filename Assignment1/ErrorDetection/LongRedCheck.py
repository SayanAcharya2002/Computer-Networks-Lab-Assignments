from .Misc import LengthMismatchException,InvalidBinaryString,validate_binary_string

class LongRedCheck:

  def __str__(self):
    return "LongRedCheck"
  
  def validate_string(self,s:str)->bool:
    if(not validate_binary_string(s)):
      raise InvalidBinaryString()
    if len(s)%8!=0:
      raise LengthMismatchException()

  def create_redundant_frame(self,s:str)->str:
    self.validate_string(s)
    return s+self.get_redundancy(s)

  def get_redundancy(self,s:str)->str:
    n=len(s)
    val=0
    for i in range(n//8):
      val^=int(s[i*8:i*8+8],base=2)
    return bin(val)[2::].rjust(8,'0')

  def is_valid_frame(self,s:str)->bool:
    try:
      self.validate_string(s)
    except:
      return False
    return int(self.get_redundancy(s),base=2)==0

if __name__=="__main__":
  # obj=LongRedCheck()
  # frame=obj.create_redundant_frame("11100111110111010011100110101001")
  # frame=chr(48+(49-ord(frame[0])))+frame[1::]
  # print(frame)
  # print(obj.is_valid_frame(frame))

  import sys
  file_name=sys.argv[1]
  with open(file_name,'r') as f:
    for i in f.readlines():
      i=i.strip('\r\n').strip('\n')
      obj=LongRedCheck()
      red=obj.get_redundancy(i)
      frame=obj.create_redundant_frame(i)
      print(f"input data: {i}")
      print(f"redundancy: {red}")
      print(f"output data: {frame}")