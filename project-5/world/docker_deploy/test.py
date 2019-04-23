from UPS_WORLD_PROTOCOL import world_ups_pb2
import sys

def UPS_WORLD_CONNECT():
    uConnect.isAmazon = False
    truck_id = 0
    for i in range (0, 10):
        truck =  uConnect.trucks.add()
        truck.id = truck_id
        truck.x = truck_id
        truck.y = truck_id
        truck_id += 1 

def ListTrucks(uConnect):
    
    for truck in uConnect.trucks:
        print ("Truck ID:", truck.id)
        print ("Truck X:", truck.x)
        print ("Truck Y:", truck.y)

        
uConnect = world_ups_pb2.UConnect()
#try:
 #   f = open(sys.argv[1], "rb")
  #  uConnect.ParseFromString(f.read())
   # f.close()
#except IOError:
 # print (sys.argv[1] + ": Could not open file.  Creating a new one.")

#uConnect.isAmazon = False
#1;95;0ctruck_id = 0
UPS_WORLD_CONNECT()
print ("Is Amazon or not:", uConnect.isAmazon)
#f = open(sys.argv[1], "wb")
#f.write(uConnect.SerializeToString())
#f.close()

ListTrucks(uConnect)