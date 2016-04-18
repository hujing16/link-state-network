__author__ = 'montanawong'

from threading import Thread, \
    ThreadError
from echomessage import EchoMessage
from config import NODE as NAME, \
    DEBUG, \
    ECHO_CLIENT_PORT
import socket



class FwdEchoThread(Thread):
    def __init__(self, routing_table, node_port_map, listen_port):
        Thread.__init__(self)
        self.routing_table = routing_table
        self.node_port_map = node_port_map
        self.listen_port = listen_port
        self.host_name = socket.gethostname() if DEBUG else self.get_ip()

        #create a socket to receive echo  message
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    def receive(self):
        msg, client_address = self.socket.recvfrom(512)
        print("Received {} from {}".format(msg, client_address))
        return msg

    def respond(self, msg):
        port_fwd = -1
        node_fwd = None

        if msg is None or msg == '':
            # discard and ignore
            return

        echo_msg = EchoMessage()
        echo_msg.decode(msg)

        # if message was intended for us, generate response and send UNLESS the message starts with receieved
        if echo_msg.to_node == NAME:
            if echo_msg.msg.lower().find('received') != -1:
                # generate response
                echo_msg.msg = 'Received your message: %s' % echo_msg.msg
                node_fwd = self.routing_table[echo_msg.from_node]
                port_fwd = self.node_port_map[node_fwd][1]
            # otherwise we read the message and discard it.
            else:
                print echo_msg.msg
                # send to echo client
                self.send(ECHO_CLIENT_PORT, msg)
                return
        else:
            # if the destination is not in our routing table, send error msg to originator
            if echo_msg.to_node not in self.routing_table.keys():
                echo_msg.msg = "Could not route message: '%s' to %s \nYour's truly -- %s" % (
                    echo_msg.msg,
                    echo_msg.to_node,
                    NAME
                )
                node_fwd = self.routing_table[echo_msg.from_node]
                # if the message origianlly came from our echo client, send it to its custom port
                # otherwise send to next hop
                port_fwd = self.node_port_map[node_fwd][1] if echo_msg.from_node != NAME else int(ECHO_CLIENT_PORT)
            # otherwise fwd the message based on our routing table
            else:
                node_fwd = self.routing_table[echo_msg.to_node]
                port_fwd = self.node_port_map[node_fwd][1]
        self.send(port_fwd, echo_msg)

    def send(self, port, echo_msg):
        """
        Send a message to a node listening at a specific port
        :param port: port number of receiving node
        :param echo_msg: Echo message object to send
        :return: void
        """
        addr = (self.host_name, port)
        print 'Sending message {} to {}'.format(echo_msg.encode(), addr)
        sent_message = self.socket.sendto(echo_msg.encode(), addr)

    def run(self):
        """
        Overriding the default thread run method
        :return: void
        """
        self.socket.bind((self.host_name, self.listen_port))
        print "Bound socket on {}: {}".format(self.host_name, self.listen_port)
        try:
            while self.isAlive():
                msg = self.receive()
                self.respond(msg)
            print 'FwdEchoer manually killed'
        except ThreadError as e:
            print 'thread error: %s' % str(e)
        finally:
            self.socket.close()
            print 'FwdEchoer shutting down'

    def kill(self):

        self.is_alive = False

    def __str__(self):
        return 'FwdEchoThread instance listening at port: %s' % self.listen_port

    def get_ip(self):
        """
        http://stackoverflow.com/a/33245570

        because socket.gethostbyname(socket.gethostname()) was returning 127.0.0.1
        """
        import os
        _file = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
        ip = _file.read().strip('\n')
        return ip

