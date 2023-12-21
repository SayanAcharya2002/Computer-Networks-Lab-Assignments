import ErrorDetection as ed
from random import sample

def inject_errors(s:str,how_many:1):
  n=len(s)
  assert(n>=how_many)
  indices=sample(range(n),how_many)
  temp_list=[i for i in s]
  for i in indices:
    temp_list[i]=chr(49+(48-ord(s[i])))
  return ''.join(temp_list)

def func1(input_data=None):
  methods=[
    ed.LongRedCheck(),
    ed.VertRedCheck(),
    ed.CheckSum(packet_len=4),
    ed.CyclicRedCheck(poly="11001"),
  ]
  if not input_data:
    input_data="110101010"
  error_data=inject_errors(input_data,1)
  print(f"input_data: {input_data}")
  print(f"error_data: {error_data}")
  for obj in methods:
    sig=obj.get_redundancy(input_data)
    error_frame=error_data+sig
    print(f"Error detected by {obj.__str__()}: {not obj.is_valid_frame(error_frame)}")

def func2():
  new_methods=[
    ed.CheckSum(packet_len=4),
    ed.CyclicRedCheck(poly="1101"),
  ]
  input_data="10000001"
  error_data="00000000"
  print(f"input_data: {input_data}")
  print(f"error_data: {error_data}")
  for obj in new_methods:
    sig=obj.get_redundancy(input_data)
    error_frame=error_data+sig
    print(f"Error detected by {obj.__str__()}: {not obj.is_valid_frame(error_frame)}")

def func3():
  new_methods=[
    ed.VertRedCheck(),
    ed.CyclicRedCheck(poly="11001"),
  ]
  input_data="10101101011110001110101111000101101011000110001"
  error_data="10101101011010001010101101000101101011000110001"
  print(f"input_data: {input_data}")
  print(f"error_data: {error_data}")
  for obj in new_methods:
    sig=obj.get_redundancy(input_data)
    error_frame=error_data+sig
    print(f"Error detected by {obj.__str__()}: {not obj.is_valid_frame(error_frame)}")

func3()