import psycopg2
import threading
from concurrent.futures import ThreadPoolExecutor
import random
import world_ups_pb2
import ups_amazon_pb2
from send_recv import disconnect, get_seqnum, send_ack_to_amazon, send_ack_to_world, send_to_world, send_to_amazon, recv_from_world, recv_from_amazon, world_ack_list, amazon_ack_list

mutex = threading.Lock()
db_host = "localhost"
#db_port = "6666"
db_port = "5432"

def truckid_selector():
    #mutex.acquire()
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    db_cur.execute("SELECT * from truck WHERE status = 'I'")
    row = db_cur.fetchone()
    if row is not None:
        db_cur.execute("UPDATE truck SET status ='E' WHERE truckid = '{}';".format(str(row[2])))
        db_conn.commit()
        #mutex.release()
        return row[2]
    '''
    db_cur.execute("SELECT * from truck WHERE status = {}").format("O")
    row = db_cur.fetchone()
    if row is not None:
        db_cur.execute("UPDATE truck SET status = E WHERE truckid = {};").format(row["truckid"])
        db_conn.commit()
        return row["truckid"]
    '''
    '''
    db_cur.execute("SELECT * from truck WHERE status = {}").format("W")
    row = db_cur.fetchone()
    if row is not None:
        return row["truckid"]'''
    '''
    db_cur.execute("SELECT * from truck WHERE status = {}").format("E")
    row = db_cur.fetchone()
    if row is not None:
        db_cur.execute("UPDATE truck SET status = E WHERE truckid = {};").format(row["truckid"])
        db_conn.commit()
        return row["truckid"]
    '''
    '''
    db_cur.execute("SELECT * from truck WHERE status = {}").format("L")
    row = db_cur.fetchone()
    if row is not None:
        db_cur.execute("UPDATE truck SET status = E WHERE truckid = {};").format(row["truckid"])
        db_conn.commit()
        return row["truckid"]
    '''
    #mutex.release()
    print("no truck avaliable!")
    return -1


def update_truck_completion(location_x, location_y, truckid, world_id):
    try:
        db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                                  "host='" + db_host + "' port='" + db_port + "'") 
        db_cur = db_conn.cursor()
    except psycopg2.OperationalError as error:
            print(error)
    try:
        db_cur.execute("update truck set status = 'W', "
                       "location_x ='"+str(location_x)+"',"+"location_y = '"+str(location_y)
                       +"'where truckid = '" + str(truckid) +
                       "' and worldid = '" + str(world_id) + "'")
        db_conn.commit()
    except psycopg2.OperationalError as error:
            print(error)


def completions_handler(completions, world_id, amazon_fd, world_fd):
    try:
        db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                                   "host='" + db_host + "' port='" + db_port + "'") 
        db_cur = db_conn.cursor()
    except psycopg2.OperationalError as error:
        print(error)
    UCommu = ups_amazon_pb2.UCommunicate()
    #mutex.acquire()
    for completion in completions:
        if completion.status == "ARRIVE WAREHOUSE":
            UArrivedAtWarehouse = UCommu.uarrived.add()
            UArrivedAtWarehouse.truckid = completion.truckid
            UArrivedAtWarehouse.seqnum = get_seqnum()
            location_x = completion.x
            location_y = completion.y
            truckid = completion.truckid
            update_truck_completion(location_x, location_y, truckid, world_id)
            try:
                db_cur.execute("select packageid from package where "
                               "worldid = '" + str(world_id) + "' and truckid = '" +
                               str(truckid) + "' and status = 'E'")
                rows = db_cur.fetchall()
            except psycopg2.OperationalError as error:
                print(error)
            for row in rows:
                db_cur.execute("update package set status = 'W' where "
                               "packageid = '" + str(row[0]) +
                               "' and worldid = '" + str(world_id) + "'")
                db_conn.commit()
        if completion.status == "IDLE":
            location_x = completion.x
            location_y = completion.y
            truckid = completion.truckid
            db_cur.execute("update truck set status = 'I', "
                           "location_x = '"+str(location_x)+"',"+"location_y = '"+str(location_y)
                           +"'where truckid = '" + str(truckid) +
                           "' and worldid = '" + str(world_id) + "'")
            db_conn.commit()
    send_to_amazon(UCommu, amazon_fd)
   #     if UPackageDelivered.seqnum in amazon_ack_list:
   #         break
    db_conn.commit()
    #mutex.release()
    return

def truck_update_deliver(truckid, world_id, packageid):
    try:
        db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                                 "host='" + db_host + "' port='" + db_port + "'") 
        db_cur = db_conn.cursor()
    except psycopg2.OperationalError as error:
            print(error)
    try:
        db_cur.execute("update package set status = 'D' "
                       "where truckid = '" + str(truckid) +
                       "' and worldid = '" + str(world_id) + "' and packageid = '" + str(packageid)+ "'")
        db_conn.commit()
    except psycopg2.OperationalError as error:
            print(error)


def delivered_handler(deliveries, world_id, amazon_fd, world_fd):
    UCommu = ups_amazon_pb2.UCommunicate()
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    #mutex.acquire()
    for deliver in deliveries:
        UPackageDelivered = UCommu.udelivered.add()
        UPackageDelivered.packageid = deliver.packageid
        UPackageDelivered.seqnum = get_seqnum()
        #TODO: add lock
        db_cur.execute("select location_x, location_y from package"
                       " where worldid = '"+str(world_id)+"' and packageid = '"+str(deliver.packageid)+"' and status = 'O'")
        row = db_cur.fetchone()
        package_x = int(row[0])
        package_y = int(row[1])
        truck_update_deliver(deliver.truckid ,world_id, UPackageDelivered.packageid)
        db_cur.execute("update truck set location_x = '"+ str(package_x)+ "', location_y = ' "
                        + str(package_y) + "'where truckid = '" + str(deliver.truckid) +
                        "' and worldid = '" + str(world_id) + "'")
        db_conn.commit()
        #while True:
    send_to_amazon(UCommu, amazon_fd)
    #    if UPackageDelivered.seqnum in amazon_ack_list:
    #        break
    db_conn.commit()
    #mutex.release()
    return


def error_handler(errors):
    for error in errors:
        print("ERROR-----")
        print(error.err,str(error.originseqnum),str(error.seqnum))
    return

def update_truck(packageid, world_id, amazon_fd, world_fd,truck_id):
    try:
        db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
        #db_conn.set_isolation_level(3)
        db_cur = db_conn.cursor()
    except psycopg2.OperationalError as error:
            print(error)
    tmp1= """update truck set packageid = %s where worldid= %s and truckid= %s"""
    try:
            db_cur.execute(tmp1,(str(packageid),str(world_id),str(truck_id)))
            db_conn.commit()
    except psycopg2.OperationalError as error:
        print(error)

def package_db_handle(orderplaced_handle_list, world_id, amazon_fd, world_fd,truck_list):
    try:
        db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
        db_conn.set_isolation_level(3)
        db_cur = db_conn.cursor()
    except psycopg2.OperationalError as error:
            print(error)
    for i in  range (0, len(orderplaced_handle_list)):
        userid = 'unknown'
        if orderplaced_handle_list[i].HasField("UPSuserid"):
            userid = orderplaced_handle_list[i].UPSuserid
            # product = order.things.name
        # description = order.things.description
        # count = order.things.count
        location_x = orderplaced_handle_list[i].x
        location_y = orderplaced_handle_list[i].y
        packageid = orderplaced_handle_list[i].packageid
        tmp1= """update truck set packageid = %s where worldid= %s and truckid= %s"""
        update_truck(packageid, world_id, amazon_fd, world_fd,truck_list[i])
        for product in orderplaced_handle_list[i].things:
            tmp = """insert into package (worldid, name, status, product_name, description, count, location_x,location_y, packageid, truckid) values(%s,%s, 'C', %s ,%s ,%s,%s,%s ,%s ,%s) """
            db_cur.execute(tmp,(str(world_id),str(userid), str(product.name),str(product.description),int(product.count),str(location_x),str(location_y),str(packageid),str(truck_list[i])))
            db_conn.commit()
    db_conn.commit()
    return

def update_truck_orderplaced(packageid, world_id, amazon_fd, world_fd,truckid):
    try:
        db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
        #db_conn.set_isolation_level(3)
        db_cur = db_conn.cursor()
    except psycopg2.OperationalError as error:
            print(error)
    tmp1= """update package set status = 'E' where truckid = %s and worldid =%s and packageid = %s"""
    try:
            print(tmp1 % (str(truckid),str(world_id),str(packageid)))
            db_cur.execute(tmp1,(str(truckid),str(world_id),str(packageid)))
            db_conn.commit()
    except psycopg2.OperationalError as error:
        print(error)


def orderplaced_handler(orderplaced_handle_list, world_id, amazon_fd, world_fd, truck_list):
    UCommands = world_ups_pb2.UCommands()
    UCommu = ups_amazon_pb2.UCommunicate()
    #mutex.acquire()
    package_db_handle(orderplaced_handle_list,world_id, amazon_fd,world_fd,truck_list)
    for i in  range (0, len(orderplaced_handle_list)):
        UGoPickup = UCommands.pickups.add()
        UGoPickup.truckid = int(truck_list[i])
        UGoPickup.whid = orderplaced_handle_list[i].whid
        UGoPickup.seqnum = get_seqnum()
        #edited
        UOrderPlaced = UCommu.uorderplaced.add()
        UOrderPlaced.packageid = orderplaced_handle_list[i].packageid
        UOrderPlaced.truckid = int(truck_list[i])
        UOrderPlaced.seqnum = get_seqnum()
        update_truck_orderplaced(UOrderPlaced.packageid, world_id, amazon_fd, world_fd,UOrderPlaced.truckid)
        tmp2 = """update truck set status = 'E' where truckid =  %s and worldid =%s"""
        db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                                "host='" + db_host + "' port='" + db_port + "'") 
        db_cur = db_conn.cursor()
        db_cur.execute(tmp2,(str(UGoPickup.truckid), str(world_id)))
        db_conn.commit()
        db_conn.close()
    send_to_amazon(UCommu, amazon_fd)
    #    if UOrderPlaced.seqnum in amazon_ack_list:
    #        break
    #while True:
    send_to_world(UCommands, world_fd)
    #    if  UGoPickup.seqnum in world_ack_list:
    #        break
    #mutex.release()
    return

def loading_status_update(loadingfinished_handle_list, world_id, amazon_fd, world_fd):
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'")
    db_cur = db_conn.cursor()
    #mutex.acquire()
    for loadingfinished in loadingfinished_handle_list:
        db_cur.execute("update package set status = 'L' "
                             "where truckid = '" + str(loadingfinished.truckid) +
                             "' and worldid = '" + str(world_id) + "' and packageid = '"
                             + str(loadingfinished.packageid) + "'")
        db_conn.commit()
    for loadingfinished in loadingfinished_handle_list:
        db_cur.execute("update truck set status = 'L' "
                             "where truckid = '" + str(loadingfinished.truckid) +
                             "' and worldid = '" + str(world_id) +"' and packageid =  '"
                             + str(loadingfinished.packageid) + "'")
        db_conn.commit()
    #mutex.release()
    return

#message send successfully, main thread wait for UResponses
def loadingfinished_handler(loadingfinished_handle_list, world_id, amazon_fd, world_fd):
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    loading_status_update(loadingfinished_handle_list, world_id, amazon_fd, world_fd)
    UCommands = world_ups_pb2.UCommands()
    #mutex.acquire()
    for loadingfinished in loadingfinished_handle_list:
        go_deliver = UCommands.deliveries.add()
        go_deliver.truckid = loadingfinished.truckid
        go_deliver.seqnum = get_seqnum()
        db_cur.execute("select location_x, location_y from package"
                       " where worldid = '"+str(world_id)+"' and truckid = '"+str(go_deliver.truckid)+"' and status = 'L'")
        rows = db_cur.fetchall()
        for row in rows:
            package = go_deliver.packages.add()
            package.packageid = loadingfinished.packageid
            package.x = int(row[0])
            package.y = int(row[1])
            db_cur.execute("update package set status = 'O' "
                            "where truckid = '" + str(go_deliver.truckid) +
                            "' and worldid = '" + str(world_id) + "' and packageid = '"
                            + str(package.packageid) + "'")
            db_conn.commit()
            db_cur.execute("update truck set status = 'O'  "
                            " where truckid = '" + str(go_deliver.truckid) +
                            "' and worldid = '" + str(world_id) + "' and packageid = '"
                            + str(package.packageid) + "'")
            db_conn.commit()
    #while True:
    send_to_world(UCommands, world_fd)
    #    if go_deliver.seqnum in world_ack_list:
    #        break
    db_conn.commit()
    return

def ups_world_receiver(UResponses, world_id, amazon_fd, world_fd):
    completions  = []
    delivered = []
    truckstatus = []
    err = []
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    if len(UResponses.completions)!=0:
        for complete in UResponses.completions:
            completions.append(complete)
            send_ack_to_world(complete.seqnum,world_fd)
        completions_handler(completions,world_id, amazon_fd, world_fd)
    if len(UResponses.delivered)!=0:
        for deliver in UResponses.delivered:
            delivered.append(deliver)
            send_ack_to_world(complete.seqnum,world_fd)
        delivered_handler(delivered, world_id, amazon_fd, world_fd)
    #if UResponses.HasField("finished"):
    #    print("Disconnect from world")
    #    disconnect(world_fd)
    if len(UResponses.acks)!=0 :
        for ack in UResponses.acks:
            world_ack_list.append(ack)
    if len(UResponses.truckstatus)!=0:
        for truck in UResponses.truckstatus:
            truckstatus.append(truck)
        truckstatus_handler(truckstatus)
        truckstatus.clear()
    if len(UResponses.error)!=0:
        for error in UResponses.error:
            err.append(error)
            error_handler(err)
    return

def amazon_ups_receiver(ACommun, world_id, amazon_fd, world_fd):
    truck_list = []
    orderplaced_handle_list = []
    loadingfinished_handle_list = []
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    if len(ACommun.aorderplaced)!=0:
        #assign thread for orderplaced_handler
        for orderplaced in ACommun.aorderplaced:
            truckid = truckid_selector()
            if(truckid == -1):
                continue
            orderplaced_handle_list.append(orderplaced)
            truck_list.append(truckid)
            send_ack_to_amazon(orderplaced.seqnum,amazon_fd)
        if len(orderplaced_handle_list) != 0:
            print("111111111111")
            orderplaced_handler(orderplaced_handle_list,world_id,amazon_fd,world_fd, truck_list)
    if len( ACommun.aloaded)!=0:
        #only part of packages loaded, need to wait
        for loadingfinished in ACommun.aloaded:
            loadingfinished_handle_list.append(loadingfinished)
            send_ack_to_amazon(loadingfinished.seqnum,amazon_fd)
        loadingfinished_handler(loadingfinished_handle_list,world_id,amazon_fd,world_fd)
    if len(ACommun.acks)!=0:
        for ack in ACommun.acks:
            amazon_ack_list.append(ack)
    return

def recv_amazon_msg(world_id, amazon_fd, world_fd):
    # create a thread pool to handle received messages
    #pool = ThreadPoolExecutor(5)
    while 1:
        # receive a message from Amazon and assign a thread to handle it
        message = ups_amazon_pb2.ACommunicate()
        message = recv_from_amazon(message, amazon_fd)
        print(message)
        #amazon_msg = recv_message(amazon_fd, amz_ups_pb2.AUMessages)
        thread1 = threading.Thread(target=amazon_ups_receiver, args=(message, world_id, amazon_fd, world_fd))
        #pool.submit(amazon_ups_receiver, message, world_id, amazon_fd, world_fd)
        thread1.start()
        thread1.join()


# receive messages from world
def recv_world_msg(world_id, amazon_fd, world_fd):
    # create a thread pool to handle received messages
    #pool = ThreadPoolExecutor(5)
    while 1:
        # receive a message from Amazon and assign a thread to handle it
        message = world_ups_pb2.UResponses()
        message = recv_from_world(message, world_fd)
        print(message)
        #world_msg = recv_message(world_fd, ups_pb2.UResponses)
        thread1 = threading.Thread(target=ups_world_receiver, args=(message, world_id, amazon_fd, world_fd))
        #pool.submit(ups_world_receiver, message, world_id, amazon_fd, world_fd)
        thread1.start()
        thread1.join()
