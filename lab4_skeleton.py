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


# Don't change any variable's name.
# Use this hashmap to store the information of your neighbor nodes.
neighbor_information = {}
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

    
    while True:
        # print(server)
    # TODO: write logic for sending broadcasts.
        
        data = node_uuid+" ON "+str(tcp_port)
        print(data)
        address = ('<broadcast>',get_broadcast_port())
        broadcaster.sendto(bytes(data,'UTF-8'),address)
        print("sent")
        time.sleep(1)   # Leave as is.


def receive_broadcast_thread():
    """
    Receive broadcasts from other nodes,
    launches a thread to connect to new nodes
    and exchange timestamps.
    """
    
    while True:
        # TODO: write logic for receiving broadcasts.
        data, (ip, port) = broadcaster.recvfrom(4096)
        parsed_data = data.decode().split(" ")
        port = int(parsed_data[2])
        recieved_uuid = parsed_data[0]
        recieved_tcp_port = parsed_data[2]
        print_blue(f"RECV: {data.decode()} FROM: {ip}:{port}")

        th3 = daemon_thread_builder(target =exchange_timestamps_thread,args=(recieved_uuid,ip,recieved_tcp_port))
        th4= daemon_thread_builder(target = tcp_server_thread)
        th3.start()
        th4.start()
        th3.join()
        th4.join()
        


def tcp_server_thread():
    """
    Accept connections from other nodes and send them
    this node's timestamp once they connect.
    """
    node_socket,(node_ip,port_ip) = server.accept()
    timestamp = node_socket.recvfrom(4096)[0].decode()
    print(timestamp)
    pass


def exchange_timestamps_thread(other_uuid: str, other_ip: str, other_tcp_port: int):
    """
    Open a connection to the other_ip, other_tcp_port
    and do the steps to exchange timestamps.
    Then update the neighbor_info map using other node's UUID.
    """
    other_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    other_socket.connect((other_ip,int(other_tcp_port)))
    timestamp = UtcNow()
    other_socket.send(bytes(str(timestamp),'utf-8'))
    print_yellow(f"ATTEMPTING TO CONNECT TO {other_uuid}")
    
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

    
    
    th1.start()
    th2.start()   
    
    th1.join()
    th2.join() 

    
    
    pass

############################################
############################################


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