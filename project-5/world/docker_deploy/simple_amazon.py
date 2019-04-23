from world_ups_proto import world_ups_pb2
from amazon_ups_proto import amazon_ups_pb2
from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32

import socket

HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

def recv_from_ups():
    var_int_buff = []
    while True:
        buf = conn.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = conn.recv(msg_len)
    print('len is =='+str(msg_len)+'   pos is=='+str( new_pos))
    UConnect = world_ups_pb2.UConnect()
    UConnect.ParseFromString(whole_message)
    print(UConnect)

ups_fd =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ups_fd.bind((HOST, PORT))
ups_fd.listen()
conn, addr = ups_fd.accept()
print('Connected by', addr)



def main():
    print("in main")
    recv_from_ups()

if __name__== "__main__":
  main()
