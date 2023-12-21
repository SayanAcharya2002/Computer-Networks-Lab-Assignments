class LengthMismatchException(Exception):
  
  def __init__(self,msg="Length not multiple of 8"):
    super(Exception,self).__init__(msg)

class InvalidBinaryString(Exception):
  def __init__(self,msg="Invalid Binary String"):
    super(Exception,self).__init__(msg)

def validate_binary_string(s:str)->bool:
  for i in s:
    if i!='0' and i!='1':
      return False
  return True

