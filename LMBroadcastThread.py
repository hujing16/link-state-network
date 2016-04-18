__author__ = 'montanawong'

from threading import Thread
from config import NODE as NAME, \
    DEBUG
from linkmsg import LinkMsg
import socket
import time


class LMBroadcaster(Thread):
    def __init__(self, node_port_map, link_table):
        Thread.__init__(self)
        self.node_port_map = node_port_map
        self.link_table = link_table
        self.socket = None
        self.host_name = socket.gethostname() if DEBUG else self.get_ip()

    def broadcast(self, interval):
        """
        Broadcast Link state messages to all nodes every interval number of seconds
        :param interval: number of seconds to broadcast between
        :return: void
        """
        while self.isAlive():
            # broadcast Link state message every "interval" # of seconds
            for node in self.node_port_map.keys():
                # send the port and the json serialized link state message to each
                # student whether or not they are listening
                for _tuple in self.link_table[NAME]:
                    # send each link that I am directly connected to
                    self.send(
                        self.node_port_map[node][0],
                        LinkMsg.encode(
                            LinkMsg(NAME, _tuple[0])
                        )
                    )

            time.sleep(interval)

    def send(self, port, msg):
        """
        Send a message to a node listening at a specific port
        :param port: port number of receiving node
        :param msg: json serialized message to send
        :return: void
        """
        addr = (self.host_name, port)
        print('Sending message {} to {}'.format(msg, port))
        sent_message = self.socket.sendto(msg, addr)

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print 'Broadcaster broadcasting LS messages'
        self.broadcast(30)
        if self.socket is not None: self.socket.close()

    def kill(self):
        self.is_alive = False

    def get_ip(self):
        """
        http://stackoverflow.com/a/33245570

        because socket.gethostbyname(socket.gethostname()) was returning 127.0.0.1
        """
        import os
        _file = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
        ip = _file.read().strip('\n')
        return ip
