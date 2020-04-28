import sys
import os
import threading
import socket
import time
import uuid
import struct
from datetime import timezone 
import datetime 
# https://bluesock.org/~willkg/dev/ansi.html
ANSI_RESET = "\u001B[0m"
ANSI_RED = "\u001B[31m"
ANSI_GREEN = "\u001B[32m"
ANSI_YELLOW = "\u001B[33m"
ANSI_BLUE = "\u001B[34m"

_NODE_UUID = str(uuid.uuid4())[:8]



def print_yellow(msg):
    print(f"{ANSI_YELLOW}{msg}{ANSI_RESET}")


def print_blue(msg):
    print(f"{ANSI_BLUE}{msg}{ANSI_RESET}")


def print_red(msg):
    print(f"{ANSI_RED}{msg}{ANSI_RESET}")


def print_green(msg):
    print(f"{ANSI_GREEN}{msg}{ANSI_RESET}")


def get_broadcast_port():
    return 35498


def get_node_uuid():
    return _NODE_UUID


def UtcNow():
    now = datetime.datetime.utcnow()
    return (now - datetime.datetime(1970, 1, 1)).total_seconds()


class NeighborInfo(object):
    def __init__(self, delay, last_timestamp, ip=None, tcp_port=None):
        # Ip and port are optional, if you want to store them.
        self.delay = delay
        self.last_timestamp = last_timestamp
        self.ip = ip
        self.tcp_port = tcp_port



############################################
#######  Y  O  U  R     C  O  D  E  ########
############################################
devices_counter = 0
first_delay = True

# Don't change any variable's name.
# Use this hashmap to store the information of your neighbor nodes.
neighbor_information = {}
neighbor_numbers = {}
# Leave the server socket as global variable.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.listen(20)
tcp_port = server.getsockname()[1]




# Leave broadcaster as a global variable.
broadcaster = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcaster.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
broadcaster.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broadcaster.bind(('0.0.0.0',get_broadcast_port()))

# Setup the UDP socket



def send_broadcast_thread():
    node_uuid = get_node_uuid()
    broadcast_count = -1
    while True:


        # print(server)
    # TODO: write logic for sending broadcasts.

        data = node_uuid+" ON "+str(tcp_port)
        address = ('<broadcast>',get_broadcast_port())
        broadcaster.sendto(bytes(data,'UTF-8'),address)
        time.sleep(1)   # Leave as is.




def receive_broadcast_thread():
    """
    Receive broadcasts from other nodes,
    launches a thread to connect to new nodes
    and exchange timestamps.
    """
    global devices_counter
    # devices_counter += 1
    # neighbor_numbers[recieved_uuid] = devices_counter
    while True:

        # TODO: write logic for receiving broadcasts.

        data, (ip, port) = broadcaster.recvfrom(4096)
        
        parsed_data = data.decode().split(" ")
        if len(parsed_data) == 3:
            if parsed_data[1] == "ON" and len(parsed_data[0]) == 8:
                port = int(parsed_data[2])
                recieved_uuid = parsed_data[0]
                recieved_tcp_port = parsed_data[2]
                
                if recieved_uuid != get_node_uuid():
                    if neighbor_information.get(recieved_uuid) == None:
                        empty_neighborInfo = NeighborInfo(0,0,None,None)
                        neighbor_information[recieved_uuid] = (empty_neighborInfo,0)
                        neighbor_numbers[recieved_uuid] = devices_counter
                        devices_counter += 1
                    first_delay = True
                    # print(neighbor_numbers)
                    # print_yellow(("[UDP] Device "+str(devices_counter)+" -> EVERYBODY : "+data.decode()))
                    # print_yellow(f"RECV: {data.decode()} FROM: {ip}:{port}")
                    
                    th3 = daemon_thread_builder(target =exchange_timestamps_thread,args=(recieved_uuid,ip,recieved_tcp_port))    
                    th3.start()
                    th3.join()
        else:
            print_red("Wrong Protocol Format")





def tcp_server_thread():
    """
    Accept connections from other nodes and send them
    this node's timestamp once they connect.
    """
    
    while True:
        node_socket,(node_ip,port_ip) = server.accept()
        timestamp = float(node_socket.recvfrom(4096)[0].decode())
        new_timestamp = UtcNow()
        node_socket.send(bytes(str(new_timestamp),'utf-8'))
    pass


def exchange_timestamps_thread(other_uuid: str, other_ip: str, other_tcp_port: int):
    """
    Open a connection to the other_ip, other_tcp_port
    and do the steps to exchange timestamps.
    Then update the neighbor_info map using other node's UUID.
    """
    global first_delay
    # if neighbor_information.get(other_uuid) == None:
    
    other_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    other_socket.connect((other_ip,int(other_tcp_port)))    
    timestamp = UtcNow()
    other_socket.send(bytes(str(timestamp),'utf-8'))
    
    # print_yellow(f"ATTEMPTING TO CONNECT TO {other_uuid}")
    
    new_timestamp = float(other_socket.recvfrom(4096)[0].decode())
    delay = new_timestamp - timestamp
    



    count = neighbor_information.get(other_uuid)[1]
    if(count == 10):
        # new_node = NeighborInfo(None,None)
        print(neighbor_information.get(other_uuid)[0].delay)
        new_node = neighbor_information.get(other_uuid)[0]
        new_node.delay = delay
        new_node.last_timestamp = new_timestamp #sambosak
        neighbor_information[other_uuid] = (new_node,1)
        
    else:
        if first_delay == True:
            print_blue(("[TCP] Device "+str(neighbor_numbers.get(other_uuid))+" connects to port "+str(other_tcp_port)+"of device"+str(neighbor_numbers.get(get_node_uuid()))))
            new_node = NeighborInfo(delay,new_timestamp,other_ip,other_tcp_port)
            neighbor_information[other_uuid] = (new_node,neighbor_information.get(other_uuid)[1]+1)
            first_delay = False
        else:
            neighbor_information[other_uuid] = (neighbor_information.get(other_uuid)[0],neighbor_information.get(other_uuid)[1]+1)
    # print(neighbor_information.get(other_uuid)[0].delay,       neighbor_information.get(other_uuid)[1])
    print_green(("[TCP] Device "+str(neighbor_numbers.get(other_uuid))+" -> Device "+str(neighbor_numbers.get(get_node_uuid()))+"  : [ "+str(other_uuid)+"'s "+str(timestamp)+" ]"))
    pass


def daemon_thread_builder(target, args=()) -> threading.Thread:
    """
    Use this function to make threads. Leave as is.
    """
    th = threading.Thread(target=target, args=args)
    th.setDaemon(True)
    return th


def entrypoint():
    
    th1 = daemon_thread_builder(target = send_broadcast_thread)
    th2= daemon_thread_builder(target = receive_broadcast_thread)
    th4= daemon_thread_builder(target = tcp_server_thread)

    th1.start()
    th2.start()
    th4.start()
    th1.join()
    th2.join()
    th4.join()
    pass

def main():
    """
    Leave as is.
    """
    print("*" * 50)
    
    print_red("To terminate this program use: CTRL+C")
    print_red("If the program blocks/throws, you have to terminate it manually.")
    print_green(f"NODE UUID: {get_node_uuid()}")
    print("*" * 50)
    time.sleep(2)   # Wait a little bit.
    entrypoint()


if __name__ == "__main__":
    main()