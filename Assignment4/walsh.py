from math import log2,ceil
import random

n=int(input("how many stations?"))
N=2**ceil(log2(n))

# need to create a walsh_table of N x N
walsh=[0]*N
for i in range(N):
  walsh[i]=[0]*N

def set_walsh(walsh,size):
  if(size==1):
    walsh[0][0]=1
    return
  half_size=size//2
  set_walsh(walsh,half_size)
  for i in range(half_size):
    for j in range(half_size,size):
      walsh[i][j]=walsh[i][j-half_size]
  
  for i in range(half_size,size):
    for j in range(half_size):
      walsh[i][j]=walsh[i-half_size][j]

  for i in range(half_size,size):
    for j in range(half_size,size):
      walsh[i][j]=-walsh[i-half_size][j-half_size]

set_walsh(walsh,N)

data_to_send=[0]*N
val=input("give data?(yes to input manually, otherwise random gen):")
if val.lower()=="yes":
  print("-1 for 0, 0 for silence, 1 for 1")
  for i in range(n):
    data_to_send[i]=int(input(f"for the {i}th station:"))
else:
  for i in range(n):
    data_to_send[i]=random.randint(-1,1)

encoded_data=[0]*N
for i in range(N):
  for j in range(N):
    encoded_data[j]+=data_to_send[i]*walsh[i][j]

data_unpacked=[0]*N
for i in range(N):#unpacking for the ith station
  tot=0
  for j in range(N):
    tot+=encoded_data[j]*walsh[i][j]
  tot//=N
  data_unpacked[i]=tot


print("data should be:")
print(*data_to_send)

print("data got:")
print(*data_unpacked)
ok=True

for i in range(N):
  if data_unpacked[i]!=data_to_send[i]:
    print(f"data garbled at {i}")
    ok=False
    break

if ok:
  print("data sent and received right")