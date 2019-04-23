#!/usr/bin/env python3
import socket
import threading
import psycopg2
import time
import world_ups_pb2
import ups_amazon_pb2
from handle_message import recv_world_msg, recv_amazon_msg
from send_recv import send_to_world, recv_from_world, send_to_amazon
#from fill_message import fill_ups_connect, fill_ua_connect

# db_host = "vcm-3838.vm.duke.edu"
#db_host = "db"
db_host = "localhost"
# world_host = "vcm-3838.vm.duke.edu"
#world_host = "server"
#world_host ="vcm-8250.vm.duke.edu"
#world_host = "152.3.53.20"
world_host = "localhost"
amazon_host = "vcm-8230.vm.duke.edu"
# db_port = "6666"
db_port = "5432"
amz_conn_port = 55559
ups_world_conn_port = 12345


""" MAIN ENTRY """
""" connect to the database which is shared with web app """
def connect_db():
    while 1:
        try:
            db_conn = psycopg2.connect("dbname='postgres' user='postgres' password = 'passw0rd'"
                                       "host='" + db_host + "' port='" + db_port + "'")
            db_cur = db_conn.cursor()
            print("connected to the database!")
            break
        except psycopg2.OperationalError as error:
            print(error)
            continue
    return db_cur, db_conn
'''
db_cur.execute("""insert into package (worldid, name, status, product_name, description, count, location_x, location_y, packageid, truckid) values ('1', 'ncnc12345','D', 'food', 'no description', 5, '2', '4', 222, '1');""")
db_conn.commit()
db_cur.execute(""" select * from package;""")
row = db_cur.fetchone()
while row is not None:
    print(row)
    row = db_cur.fetchone()

print("data insert sucessfully!")
'''

# ----------------------------------------------------------------------------------
""" 1. establish connection with the world """
# ----------------------------------------------------------------------------------
# 1.1 establish a TCP connection to the "world"
def connect_world():
    world_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #while 1:
    try:
        world_fd.connect((world_host, ups_world_conn_port))
        #break
    except (ConnectionRefusedError, ConnectionResetError,
            ConnectionError, ConnectionAbortedError) as error:
        print(error)
        #continue
    print("!!!!!!")
    return world_fd


def init_world(world_fd, db_cur, db_conn):
    UConnect = world_ups_pb2.UConnect()
    UConnect.isAmazon = False
   # UConnect.worldid = 1
    for i in range(1,1):
        car1 = UConnect.trucks.add()
        car1.id = i
        car1.x = i
        car1.y = i
   
    send_to_world(UConnect, world_fd)
    UConnected = world_ups_pb2.UConnected()
    UConnected = recv_from_world(UConnected, world_fd)
    world_id = UConnected.worldid

    for i in range(1,30):
        db_cur.execute("insert into truck "
                       "(worldid, truckid, packageid, location_x,"
                       "location_y, status) values('" +
                        str(world_id) + "', '" +
                       str(i) + "', "+'0'+", '"+str(i)+"', '"+str(i)+ "', '" +
                       'I' + "')")
    print (UConnected)
    db_conn.commit()
    return world_id


# 1.2 check the database to see if there is any created world
# TODO: get created world's id from the data base, default 1000
#       database lookup here->
# TODO: for now, use a created world 1339 for debugging
#send message to world and create trucks and insert into table


# ----------------------------------------------------------------------------------
""" 2. establish connection with Amazon """
# ----------------------------------------------------------------------------------
def connect_amazon(world_id):
    amazon_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to the server on local computer
    while 1:
        try:
            #amazon_fd.connect(('10.0.0.243', 12345))
            #amazon_fd.connect((world_host, 5678))
            amazon_fd.connect((amazon_host, 55555))
            print("!!!!!")
            message = ups_amazon_pb2.AUConnect()
            message.worldid = world_id
            send_to_amazon(message, amazon_fd)
            break
        except (ConnectionRefusedError, ConnectionResetError,
                ConnectionError, ConnectionAbortedError) as error:
            #print(error)
            continue
    return amazon_fd
# ----------------------------------------------------------------------------------
""" 3. receive messages from Amazon and world, handle the messages """
# ----------------------------------------------------------------------------------
# create two threads to handle messages from amazon and world respectively
'''
thread1 = threading.Thread(target=recv_amazon_msg)
thread1.start()
thread2 = threading.Thread(target=recv_world_msg)
thread2.start()
'''
def main():
    print("Hello, World")
    db_cur, db_conn = connect_db()
    world_fd = connect_world()
    world_id =  init_world(world_fd, db_cur, db_conn)
    print("waiting for amazon setting up")
    time.sleep(6)
    amazon_fd = connect_amazon(world_id)
    thread1 = threading.Thread(target=recv_amazon_msg, args=(world_id, amazon_fd, world_fd))
    thread1.start()
    thread2 = threading.Thread(target=recv_world_msg, args=(world_id, amazon_fd, world_fd))
    thread2.start()

if __name__=="__main__":
    main()

