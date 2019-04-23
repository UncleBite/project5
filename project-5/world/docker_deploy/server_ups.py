from UPS_WORLD_PROTOCOL import world_ups_pb2
from UPS_AMAZON_PROTOCOL import ups_amazon_pb2
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

def send_to_world(msg):
    print('msg you send is')
    print('-----')
    print(msg)
    print('-----')
    _EncodeVarint(world_fd.send, len(msg.SerializeToString()), None)
    world_fd.sendall(msg.SerializeToString())

def send_to_amazon(msg):
    print('msg you send is')
    print('-----')
    print(msg)
    print('-----')
    _EncodeVarint(amazon_fd.send, len(msg.SerializeToString()), None)
    amazon_fd.sendall(msg.SerializeToString())

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

def completions_handler(completions):
    UCommun_ArrivedAtWarehouse = ups_amazon_pb2.UCommunicate()
    UCommun_PackageDelivered = ups_amazon_pb2.UCommunicate()
    for completion in completions:
        if(completion.status == "ArrivedAtWarehouse"):
            arrived = UCommun_ArrivedAtWarehouse.uarrived.add()
            #arrived.trucknum = truck_id
            #arrived.seqnum = seq
        if(completion.status == "PackageDelivered"):
            delived = UCommun_PackageDelivered.udelivered.add()
            #delived.packageid = packageid
            #delived.seqnum = seq

    if(UCommun_ArrivedAtWarehouse.HasField('uarrived')):
        while(1){
            send_to_amazon(UCommun_ArrivedAtWarehouse)
            #stop for a while
            #find ack in ack_list
            #if ack found, break
        }

        if(UCommun_PackageDelivered.HasField('udelivered')):
        while(1){
            send_to_amazon(UCommun_PackageDelivered)
            #stop for a while
            #find ack in ack_list
            #if ack found, break
        }

def orderplaced_handler(orderplaced_handle_list):
    UCommands = world_ups_pb2.UCommands()
    for orderplaced in orderplaced_handle_list:
        pickup = UCommands.pickups.add()
        #pickup.truckid = truckid
        pickup.whid = orderplaced.whid
        #pickup.seqnum = seq
    while(1){
        send_to_world(UCommands)
        #stop for a while
        #find ack in ack_list
        #if ack found, break
    }
    #message send successfully, main thread wait for UResponses
def loadingfinished_handler(loadingfinished_handle_list):
    UCommands = world_ups_pb2.UCommands()
    for loadingfinished in loadingfinished_handle_list:
        go_deliver = UCommands.deliveries.add()
        #go_deliver.truckid = truckid
        #go_deliver.seqnum = seq
        




def ups_world_receiver():
    UResponses = world_ups_pb2.UResponses()
    completions  = []
    delivered = []
    truckstatus = []
    err = []
    while(1){
        recv_from_world(UResponses)
        if(UResponses.HasField('completions')):
            for complete in UResponses.completions:
                completions.append(complete)
            completions_handler(completions)
            completions.clear()
        if(UResponses.HasField('delivered')):
            for deliver in UResponses.delivered:
                delivered.append(deliver)
            delivered_handler(delivered)
            delivered.clear()
        if(UResponses.HasField('finished')):
            
        if(UResponses.HasField('acks')):
            #add ack to list
        if(UResponses.HasField('truckstatus')):

        if(UResponses.HasField('error')):

    }

def amazon_ups_receiver():
    ACommun = ups_amazon_pb2.ACommunicate()
    orderplaced_handle_list = []
    loadingfinished_handle_list = []
    while(1){
        if(ACommun.HasField('aorderplaced')):
            #assign thread for orderplaced_handler
            for orderplaced in ACommun.aorderplaced:
                orderplaced_handle_list.append(orderplaced)
            orderplaced_handler(orderplaced_handle_list)
            orderplaced_handle_list.clear()
            #send ack 
        if(ACommun.HasField('aloaded')):
            for loadingfinished in ACommun.aloaded:
                loadingfinished_handle_list.append(loadingfinished)
            loadingfinished_handler(loadingfinished_handle_list)
            loadingfinished_handle_list.clear()
            #send ack
        if(ACommun.HasField('acks')):
            #add ack to list
    }