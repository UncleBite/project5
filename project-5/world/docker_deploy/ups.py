from world_ups_proto import world_ups_pb2
from amazon_ups_proto import amazon_ups_pb2
from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32
import socket

world_fd = socket.socket()
# Define the port on which you want to connect
port = 12345
# connect to the server on local computer
world_fd.connect(('0.0.0.0', port))

amazon_fd = socket.socket()
amz_port = 65432
# connect to the server on local computer
#amazon_fd.connect(('0.0.0.0', amz_port))

def init_world():
    UConnect = world_ups_pb2.UConnect()
    UConnect.isAmazon = False;
    car1 = UConnect.trucks.add()
    car1.id = 5
    car1.x = 1
    car1.y =2
    send_to_world(UConnect)
    UConnected = world_ups_pb2.UConnected()
    UConnected=recv_from_world(UConnected)
    #print (UConnected)
    send_deliver_to_world(1,1,1)


def send_pickup_to_world(truckid,whid,seqnum):
    UCommands = world_ups_pb2.UCommands()
    pickup = UCommands.pickups.add()
    pickup.truckid = truckid
    pickup.whid = whid
    pickup.seqnum = seqnum
    UCommands.acks.append(1)
    send_to_world(UCommands)
    UResponses = world_ups_pb2.UResponses()
    recv_from_world(UResponses)
    print(UResponses)

def send_deliver_to_world(truckid,packages,seqnum):
    UCommands = world_ups_pb2.UCommands()
    deliveries = UCommands.deliveries.add()
    deliveries.truckid = truckid
    deliveries.seqnum = seqnum
    #deliveries.packages.append(packages)
    UCommands.acks.append(1)
    send_to_world(UCommands)
    UResponses = world_ups_pb2.UResponses()
    print(recv_from_world(UResponses))

def orderplaced_handle(orderplaced):
    UCommands = world_ups_pb2.UCommands()
    UResponses = world_ups_pb2.UResponses()
    pickup = UCommands.pickups.add()
    #pickup.truckid = truckid
    pickup.whid = orderplaced.whid
    #pickup.seqnum = seq
    message = UCommands.SerializeToString()
    #add mux
    while(1){
        send_to_world(message)
        recv_from_world(UResponses)
        if(UResponses.ack == seq)
            break
    }
    if(not UResponses.HasField('completions')):
        recv_from_world(UResponses)
    
    #unlock
    
    #add to database

def loadingfinished_handle()


def parse_Amazon(message):
    for orderplaced in message.aorderplaced:
        orderplaced_handle(orderplaced)
    for loadingfinished in message.aloaded:
        loadingfinished_handle(loadingfinished)

def parse():

    recv_from_world(UCommands)



def send_to_amazon(msg):
    print('msg you send is')
    print('-----')
    print(msg)
    print('-----')
    _EncodeVarint(amazon_fd.send, len(msg.SerializeToString()), None)
    amazon_fd.sendall(msg.SerializeToString())

def send_to_world(msg):
    print('msg you send is')
    print('-----')
    print(msg)
    print('-----')
    _EncodeVarint(world_fd.send, len(msg.SerializeToString()), None)
    world_fd.sendall(msg.SerializeToString())

def recv_from_world(Message):
    var_int_buff = []
    while True:
        buf = world_fd.recv(1)
        var_int_buff += buf
        print(buf)
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = world_fd.recv(msg_len)
    Message.ParseFromString(whole_message)
    return (Message)

def recv_from_amazon(Message):
    var_int_buff = []
    while True:
        buf = amazon_fd.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = amazon_fd.recv(msg_len)
    Message.ParseFromString(whole_message)
    return (Message)



def main():
    print("in main")
    init_world()

if __name__== "__main__":
  main()
