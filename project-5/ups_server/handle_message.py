import psycopg2
import threading
from concurrent.futures import ThreadPoolExecutor
import random
import world_ups_pb2
import ups_amazon_pb2
from send_recv import disconnect, get_seqnum, send_ack_to_amazon, send_ack_to_world, send_to_world, send_to_amazon, recv_from_world, recv_from_amazon


db_host = "localhost"
#db_port = "6666"
db_port = "5432"

def truckid_selector():
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    db_cur.execute("SELECT * from truck WHERE status = 'I'")
    row = db_cur.fetchone()
    if row is not None:
        db_cur.execute("UPDATE truck SET status ='E' WHERE truckid = '{}';".format(str(row[2])))
        db_conn.commit()
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
    return -1

def completions_handler(completions, world_id, amazon_fd, world_fd):
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()

    UCommu = ups_amazon_pb2.UCommunicate()
    print("in completions_handler")
    for completion in completions:
        if completion.status == "ArrivedAtWarehouse":
            UArrivedAtWarehouse = UCommu.uarrived.add()
            UArrivedAtWarehouse.truckid = completion.truckid
            UArrivedAtWarehouse.seqnum = get_seqnum()
            location_x = completion.location_x
            location_y = completion.location_y
            truckid = completion.truckid
            db_cur.execute("update truck set status = 'W', "
                            "location_x ='"+str(location_x)+"',"+"location_y = '"+str(location_y)
                            +"'where truckid = '" + str(truckid) +
                            "' and worldid = '" + str(world_id) + "'")
            db_cur.execute("select packageid from ups_frontend_package where "
                           "worldid = '" + str(world_id) + "' and truckid = '" +
                           str(completions.truckid) + "' and status = 'E'")
            rows = db_cur.fetchall()
            for row in rows:
                db_cur.execute("update ups_frontend_package set status = 'W' where "
                           "packageid = '" + str(row['packageid']) +
                           "' and worldid = '" + str(world_id) + "'")
        if completion.status == "PackageDelivered":
            location_x = completion.location_x
            location_y = completion.location_y
            truckid = completion.truckid
            db_cur.execute("update truck set status = 'I', "
                           "location_x = '"+str(location_x)+"',"+"location_y = '"+str(location_y)
                           +"'where truckid = '" + str(truckid) +
                           "' and worldid = '" + str(world_id) + "'")
            #TODO: add lock
   #while True
    send_to_amazon(UCommu, amazon.fd)
   #     if UPackageDelivered.seqnum in amazon_ack_list:
   #         break
    db_conn.commit()
    print("completions_handler finished")

def delivered_handler(deliveries, world_id, amazon_fd, world_fd):
    UCommu = ups_amazon_pb2.UCommunicate()
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    print("in delivered_handler")
    for delivery in deliveries:
        UPackageDelivered = UCommu.udelivered.add()
        UPackageDelivered.packageid = deliver.packageid
        UPackageDelivered.seqnum = get_seqnum()
        #TODO: add lock
        db_cur.execute("select location_x, location_y from package"
                       "where worldid = '"+str(worldid)+"' and packageid = '"+str(deliver.packageid)+"' and status = 'O'")
        row = cur.fetchone()
        package_x = row['location_x']
        package_y = row['location_y']
        # A package delivered, change status to delivered
        db_cur.execute("update package set status = 'D', "
                       "where truckid = '" + str(deliver.truckid) +
                       "' and worldid = '" + str(world_id) + "' and packageid = " + deliver.packageid)
        db_cur.execute("update truck set location_x = '"+ str(package_x)+ "', location_y = ' "
                        + str(package_y) + "'where truckid = '" + str(deliver.truckid) +
                        "' and worldid = '" + str(world_id) + "')")
    #while True:
    send_to_amazon(UCommu, amazon)
    #    if UPackageDelivered.seqnum in amazon_ack_list:
    #        break
    db_conn.commit()
    print("delivered_handler finished")


def error_handler(errors, world_id, amazon_fd, world_fd):
    print("in error_handler")
    for error in errors:
        print("ERROR-----")
        print(error.err,str(error.originseqnum),str(error.seqnum))

def package_db_handle(orderplaced_handle_list, world_id, amazon_fd, world_fd,truckid):
    print("in package_db_handle")
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    for order in orderplaced_handle_list:
        userid = 'unknown'
        if order.HasField("UPSuserid"):
            userid = order.UPSuserid
       # product = order.things.name        
#        description = order.things.description
 #       count = order.things.count
        location_x = order.x
        location_y = order.y
        packageid = order.packageid
        for product in order.things:
            tmp = """insert into package (worldid, name, status, product_name, description, count, location_x,location_y, packageid, truckid) values(%s,%s, 'C', %s ,%s ,%s,%s,%s ,%s ,%s) """
            db_cur.execute(tmp,(str(world_id),str(userid), str(product.name),str(product.description),int(product.count),str(location_x),str(location_y),str(packageid),str(truckid)))
    db_conn.commit()
    print("in package_db_handle")

def orderplaced_handler(orderplaced_handle_list, world_id, amazon_fd, world_fd):
    print("in orderplaced_handler")
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    UCommands = world_ups_pb2.UCommands()
    UCommu = ups_amazon_pb2.UCommunicate()
    package_db_handle(orderplaced_handle_list,world_id, amazon_fd,world_fd,truckid_selector())
   
    for order in orderplaced_handle_list:
        UGoPickup = UCommands.pickups.add()
        UGoPickup.truckid = int(truckid_selector())
        UGoPickup.whid = order.whid
        UGoPickup.seqnum = get_seqnum()
        #edited
        UOrderPlaced = UCommu.uorderplaced.add()
        UOrderPlaced.packageid = order.packageid
        UOrderPlaced.truckid = int(truckid_selector())
        UOrderPlaced.seqnum = get_seqnum()
        tmp1= """update package set status = 'E' where truckid = %s and worldid =%s and packageid = %s"""      
        db_cur.execute(tmp1,(str(UGoPickup.truckid),str(world_id),int(order.packageid )))
        tmp2 = """update truck set status = 'E' where truckid =  %s and worldid =%s"""
        db_cur.execute(tmp2,(str(UGoPickup.truckid), str(world_id)))
    #while True:
    send_to_amazon(UCommu, amazon_fd)
    #    if UOrderPlaced.seqnum in amazon_ack_list:
    #        break
    #while True:
    send_to_world(UCommands, world_fd)
    #    if  UGoPickup.seqnum in world_ack_list:
    #        break
    db_conn.commit()
    print("orderplaced_handler finished")

def loading_status_update(loadingfinished_handle_list, world_id, amazon_fd, world_fd):
    print("in loading_status_update")
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()

    for loadingfinished in loadingfinished_handle_list:
        db_cur.execute("update package set status = 'L', "
                             "where truckid = '" + str(loadingfinished.truckid) +
                             "' and worldid = '" + str(world_id) + "' and packageid =  "
                             + loadingfinished.packageid)

    for loadingfinished in loadingfinished_handle_list:
        db_cur.execute("update truck set status = 'L', "
                             "where truckid = '" + str(loadingfinished.truckid) +
                             "' and worldid = '" + str(world_id) +"' and packageid =  "
                             + loadingfinished.pickageid)
    db_conn.commit()
    print("loading_status_update finished")

#message send successfully, main thread wait for UResponses
def loadingfinished_handler(loadingfinished_handle_list, world_id, amazon_fd, world_fd):
    print("in loadingfinished_handler")
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    loading_status_update(loadingfinished_handle_list, world_id, amazon_fd, world_fd)
    UCommands = world_ups_pb2.UCommands()
    for loadingfinished in loadingfinished_handle_list:
        go_deliver = UCommands.deliveries.add()
        go_deliver.truckid = loadingfinished.truckid
        go_deliver.seqnum = get_seqnum()
        db_cur.execute("select location_x, location_y from package"
                       "where worldid = '"+str(world_id)+"' and truckid = '"+str(go_deliver.truckid)+"' and status = 'L'")
        rows = cur.fetchall()
        for row in rows:
            package = go_deliver.packages.add()
            package.packageid = loadingfinished.packageid
            package.x = row['location_x']
            package.y = row['location_y']
            db_cur.execute("update package set status = 'O', "
                            "where truckid = '" + str(go_deliver.truckid) +
                            "' and worldid = '" + str(world_id) + "' and packageid =  "
                            + package.packageid)
            db_cur.execute("update truck set status = 'O', "
                            " where truckid = '" + str(go_deliver.truckid) +
                            "' and worldid = '" + str(world_id) + "' and packageid = "
                            + package.packageid)
    #while True:
    send_to_world(UCommands, world_fd)
    #    if go_deliver.seqnum in world_ack_list:
    #        break
    db_conn.commit()
    print("loadingfinished_handler finished")

def ups_world_receiver(UResponses, world_id, amazon_fd, world_fd):
    print("in ups_world_receiver,UResponses is:")
    print(UResponses)
    completions  = []
    delivered = []
    truckstatus = []
    err = []
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    while 1:
        if len(completions) != 0 :
            for complete in UResponses.completions:
                completions.append(complete)
                send_ack_to_world(complete.seqnum,world_fd)
            completions_handler(completions)
            completions.clear()
        if len(delivered)!= 0:
            for deliver in UResponses.delivered:
                delivered.append(deliver)
                send_ack_to_world(complete.seqnum,world_fd)
            delivered_handler(delivered)
            delivered.clear()
        if UResponses.HasField("finished"):
            print("Disconnect from world")
            disconnect(world_fd)
        if len(acks)!=0 :
            for ack in UResponses.acks:
                world_ack_list.append(ack)
        if len(truckstatus)!=0:
            for truck in UResponses.truckstatus:
                truckstatus.append(truck)
            truckstatus_handler(truckstatus)
            truckstatus.clear()
        if len(error)!=0:
            for error in UResponses.error:
                err.append(error)
            error_handler(err)
            err.clear()
    print("ups_world_receiver finished")

def amazon_ups_receiver(ACommun, world_id, amazon_fd, world_fd):
    print("in amazon_ups_receiver,ACommun is:")
    print(ACommun)
    orderplaced_handle_list = []
    loadingfinished_handle_list = []
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password='passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'") 
    db_cur = db_conn.cursor()
    while 1:
        if len(ACommun.aorderplaced)!=0:
            #assign thread for orderplaced_handler
            for orderplaced in ACommun.aorderplaced:
                if(truckid_selector() == -1):
                    continue
                orderplaced_handle_list.append(orderplaced)
                send_ack_to_amazon(orderplaced.seqnum,amazon_fd)
            orderplaced_handler(orderplaced_handle_list,world_id,amazon_fd,world_fd)
            orderplaced_handle_list.clear()
        if len( ACommun.aloaded)!=0:
            #only part of packages loaded, need to wait
            for loadingfinished in ACommun.aloaded:
                loadingfinished_handle_list.append(loadingfinished)
                send_ack_to_amazon(loadingfinished.seqnum,amazon_fd)
            loadingfinished_handler(loadingfinished_handle_list,world_id,amazon_fd,world_fd)
            loadingfinished_handle_list.clear()
        if len(ACommun.acks)!=0:
            for ack in ACommun.acks:
                amazon_ack_list.append(ack)
            pass
    print("amazon_ups_receiver finished")

def recv_amazon_msg(world_id, amazon_fd, world_fd):
    print("in recv_amazon_msg")
    # create a thread pool to handle received messages
    # pool = threadpool.ThreadPool(num_threads)
    while 1:
        # receive a message from Amazon and assign a thread to handle it
        message = ups_amazon_pb2.ACommunicate()
        message = recv_from_amazon(message, amazon_fd)
        #amazon_msg = recv_message(amazon_fd, amz_ups_pb2.AUMessages)
        thread1 = threading.Thread(target=amazon_ups_receiver, args=(message, world_id, amazon_fd, world_fd))
        thread1.start()
        thread1.join()


# receive messages from world
def recv_world_msg(world_id, amazon_fd, world_fd):
    print("in recv_world_msg")
    # create a thread pool to handle received messages
    while 1:
        # receive a message from Amazon and assign a thread to handle it
        message = world_ups_pb2.UCommands()
        message = recv_from_world(message, world_fd)
        #world_msg = recv_message(world_fd, ups_pb2.UResponses)
        thread1 = threading.Thread(target=ups_world_receiver, args=(message, world_id, amazon_fd, world_fd))
        thread1.start()
        thread1.join()