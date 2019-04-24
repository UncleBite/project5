from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32
import world_ups_pb2
import ups_amazon_pb2
import protobuf_json
import json

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
    #print("sending ack to AMAZON")
    UCommu = ups_amazon_pb2.UCommunicate()
    UCommu.acks.append(ack)
    send_to_amazon(UCommu,amazon_fd)

def send_ack_to_world(ack, world_fd):
    #print("sending ack to WORLD")
    UCommands = world_ups_pb2.UCommands()
    UCommands.acks.append(ack)
    send_to_world(UCommands,world_fd)


def send_unack_msg_to_world():
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password = 'passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'")
    db_cur = db_conn.cursor()
    while True:
        """
        get all message that haven't receive ack
        """
        db_cur.execute("""select message from  world_ack""")
        """send them all again"""
        msgs_json = db_cur.fetchall()
        """define json format, restore it back to Message"""
        for msg_json in msgs_json:
            """restore it back to Message and send again"""
            msg = world_ups_pb2.UCommands()
            msg = json2pb(msg, msg_json, useFieldNumber=False)
            _EncodeVarint(worldfd.send, len(msg.SerializeToString()), None)
            worldfd.sendall(msg.SerializeToString())
        sleep(600)

def send_unack_msg_to_amazon():
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password = 'passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'")
    db_cur = db_conn.cursor()
    while True:
        """
        get all message that haven't receive ack
        """
        db_cur.execute("""select message from  amazon_ack""")
        """send them all again"""
        msgs_json = db_cur.fetchall()
        for msg_json in msgs_json:
            """restore it back to Message and send again"""
            msg = ups_amazon_pb2.UCommunicate()
            msg = json2pb(msg, msg_json, useFieldNumber=False)
            _EncodeVarint(amazon_fd.send, len(msg.SerializeToString()), None)
            amazon_fd.sendall(msg.SerializeToString())
        sleep(600)


def send_to_world(msg, worldfd):
    #print('msg you send to WORLD is:')
    print(msg)
    json_msg = pb2json(msg,)
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password = 'passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'")
    db_cur = db_conn.cursor()

    #if the message is not pure ack:
    if len(msg.pickups) or len(msg.deliveries) or len(msg.queries) != 0:
        """
        insert message into database
        """
        db_cur.execute("""INSERT INTO world_ack (seqnum,message) VALUES(%s,%s);""",(msg.acks,json_msg))
        db_conn.commit()
        _EncodeVarint(worldfd.send, len(msg.SerializeToString()), None)
        worldfd.sendall(msg.SerializeToString())
    else: #send pure ack
        _EncodeVarint(worldfd.send, len(msg.SerializeToString()), None)
        worldfd.sendall(msg.SerializeToString())

def send_to_amazon(msg, amazon_fd):
    #print('msg you send to AMAZON is')
    print(msg)
    json_msg = pb2json(msg,)
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password = 'passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'")
    db_cur = db_conn.cursor()
    if len(msg.uorderplaced) or len(msg.uarrived) or len(msg.udelivered) != 0:
        """
        insert message into database
        """
        db_cur.execute("""INSERT INTO amazon_ack (seqnum,message) VALUES(%s,%s);""",(msg.acks,json_msg))
        db_conn.commit()
        _EncodeVarint(worldfd.send, len(msg.SerializeToString()), None)
        worldfd.sendall(msg.SerializeToString())
    else:
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
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password = 'passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'")
    db_cur = db_conn.cursor()
    for ack in Message.acks:
        """
        delete all the mesage that has been marked as acked
        """
        db_cur.execute("""DELETE FROM world_ack WHERE seqnum = %s;""",(ack,))
    return (Message)

def recv_from_amazon(Message, amazon_fd):
    var_int_buff = []
    while True:
        try:
            buf = amazon_fd.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        except:
            continue
    whole_message = amazon_fd.recv(msg_len)
    Message.ParseFromString(whole_message)
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password = 'passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'")
    db_cur = db_conn.cursor()
    for ack in Message.acks:
        """
        delete all the mesage that has been marked as acked
        """
        db_cur.execute("""DELETE FROM amazon_ack WHERE seqnum = %s;""",(ack,))
    return (Message)
