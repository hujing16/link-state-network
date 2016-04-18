__author__ = 'montanawong'

from threading import Thread, \
    ThreadError
from linkmsg import LinkMsg
from config import NODE as NAME, \
    DEBUG
import socket
import time

class LMListener(Thread):
    """
    Thread that listens for Link State Messages and updates the router's link table accordingly
    """
    def __init__(self, link_table, listen_port):
        # call superclass constructor
        Thread.__init__(self)
        #initialize the attributes
        self.link_table = link_table
        self.listen_port = listen_port
        #create a socket to receive Link State message
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def receive(self):
        while self.isAlive():
            # continue to receive messages from other nodes until thread is killed
            msg, client_address = self.socket.recvfrom(512)
            print "Received {} from {}".format(msg, client_address)


            # call worker thread to update link table based on message
            updater = LMUpdater(self.link_table, msg)
            updater.start()


    def run(self):
        """
        Overriding the default thread run method
        :return: void
        """
        self.socket.bind((self.get_ip() if not DEBUG else socket.gethostname(), self.listen_port))
        print "Bound socket on {}: {}".format(self.get_ip() if not DEBUG else socket.gethostname(), self.listen_port)
        try:
            self.receive()
            print 'LM Listener manually killed'
        except ThreadError as e:
            print 'thread error: %s' % str(e)
        finally:
            self.socket.close()
            print 'LM Listener shutting down'

    def get_ip(self):
        """
        http://stackoverflow.com/a/33245570

        because socket.gethostbyname(socket.gethostname()) was returning 127.0.0.1
        """
        import os
        _file = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
        ip = _file.read().strip('\n')
        return ip

    def kill(self):
        self.is_alive = False


class LMUpdater(Thread):
    """
    Utility thread to update a link table
    """
    def __init__(self, link_table, json_link_msg):
        Thread.__init__(self)
        self.link_table = link_table

        # decode json obj
        link_msg = LinkMsg()
        link_msg.reconstitute_(json_link_msg)
        self.link_msg = link_msg

    def run(self):
        """
        Runs the updater, logic is done to update the link table accordingly
        :return:
        """
        # check if msg is expired
        if self.link_msg.expiration <= time.time():
            return

        # recall {'student0': [('denver', 123123)]}
        search_link_table = lambda value: value[0] == self.link_msg.to_node
        # if the nodes is already in our link table, we would store a->b and b->a so 2 checks...
        if self.link_msg.from_node in self.link_table and self.link_msg.to_node in self.link_table:
            # check if the link is stored
            _tuple = filter(search_link_table, self.link_table[self.link_msg.from_node])
            if _tuple == []:
                # create the links if they dont exist.
                link_list = self.link_table[self.link_msg.to_node]
                link_list_mirror = self.link_table[self.link_msg.from_node]
                link_list.append(
                    [self.link_msg.from_node, self.link_msg.expiration]
                )
                link_list_mirror.append(
                    [self.link_msg.to_node, self.link_msg.expiration]
                )
            else:
                # update the expiration times
                _tuple[0][1] = self.link_msg.expiration
                # update in the mirror link
                search_link_table = lambda value: value[0] == self.link_msg.from_node
                mirror_tuple = filter(search_link_table, self.link_table[self.link_msg.to_node])
                if mirror_tuple == []:
                    raise RuntimeError("Horrible error")
                else:
                    mirror_tuple[0][1] = self.link_msg.expiration
        else:
            # otherwise the nodes don't even exist as table keys. We need to create everything from scratch
            if self.link_msg.from_node not in self.link_table.keys():
                self.link_table[self.link_msg.from_node] = [
                    [self.link_msg.to_node, self.link_msg.expiration]
                ]
            else:
                # otherwise it fromNode exists as a key
                self.link_table[self.link_msg.from_node].append(
                    [self.link_msg.to_node, self.link_msg.expiration]
                )
            # do mirror
            if self.link_msg.to_node not in self.link_table.keys():
                self.link_table[self.link_msg.to_node] = [
                    [self.link_msg.from_node, self.link_msg.expiration]
                ]
            else:
                self.link_table[self.link_msg.to_node].append(
                    [self.link_msg.from_node, self.link_msg.expiration]
                )
