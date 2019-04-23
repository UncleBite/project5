from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32
import world_ups_pb2
import ups_amazon_pb2


world_ack_list = []
amazon_ack_list = []
seq = 0

def disconnect(world_fd):
    UCommands = ups_amazon_pb2.UCommands()
    UCommands.disconnect = True
    acks = UCommands.acks.add()
    acks.ack = get_seqnum()
    while True:
        send_to_world(UCommands,world_fd)
        if acks.ack in world_ack_list:
            break


def get_seqnum():
    global seq
    seq = seq+1
    return seq

def send_ack_to_amazon(ack, amazon_fd):
    print("sending ack to AMAZON")
    UCommu = ups_amazon_pb2.UCommunicate()
    UCommu.acks.append(ack)
    send_to_amazon(UCommu,amazon_fd)
    pass

def send_ack_to_world(ack, world_fd):
    print("sending ack to WORLD")
    UCommands = ups_amazon_pb2.UCommands()
    UCommands.acks.append(ack)
    send_to_world(UCommands,world_fd)
    pass

def send_to_world(msg, world_fd):
    print('msg you send to WORLD is:')
    print(msg)
    _EncodeVarint(world_fd.send, len(msg.SerializeToString()), None)
    world_fd.sendall(msg.SerializeToString())

def send_to_amazon(msg, amazon_fd):
    print('msg you send to AMAZON is')
    print(msg)
    _EncodeVarint(amazon_fd.send, len(msg.SerializeToString()), None)
    amazon_fd.sendall(msg.SerializeToString())

def recv_from_world(Message, world_fd):
    var_int_buff = []
    while True:
        try:
            buf = world_fd.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        except:
            continue
    whole_message = world_fd.recv(msg_len)
    Message.ParseFromString(whole_message)
    print("message received from WORLD is:")
    print(Message)
    return (Message)

def recv_from_amazon(Message, amazon_fd):
    var_int_buff = []
    while True:
        buf = amazon_fd.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = amazon_fd.recv(msg_len)
    Message.ParseFromString(whole_message)
    print("message received from AMAZON is:")
    print(Message)
    return (Message)
