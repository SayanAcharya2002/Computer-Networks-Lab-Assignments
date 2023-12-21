from time import sleep
from random import randint,sample

MAX_LEN_MSG=1024
FORMAT_MSG='utf-8'
DEFAULT_TIMEOUT_MSG=4
MAX_CHARS_TO_SEND=25
MAX_LEN_CONTENT=8*MAX_CHARS_TO_SEND #keep as a multiple of 8 for better demo purposes
EXIT_MESSAGE="0"*16+"0"*100+"0"
ZERO_ERROR_NO_DELAY_FUNC=lambda x:x

def SOME_ERROR_SOME_DELAY_FUNC(s:str):
  sleep(2)
  indices=sample(range(len(s)),randint(0,1))
  s_list=[i for i in s]
  for i in indices:
    s_list[i]=chr(1-ord(s_list[i])+2*ord('0')) #random bit flipping
  return ''.join(s_list)