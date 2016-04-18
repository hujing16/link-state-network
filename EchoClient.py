__author__ = 'montanawong'
import socket
import argparse
import sys
from config import DEBUG, ECHO_PORT, ECHO_CLIENT_PORT, NODE as NAME
from echomessage import EchoMessage

class EchoClient(object):
    """
    Object that allows a user to send messages to a specified server.
    """
    def __init__(self, port_listen, port_fwd):
        self.port_listen = port_listen
        self.port_fwd = port_fwd
        self.host_name = socket.gethostname() if DEBUG else self.get_ip()
        self.echo_addr = (self.host_name, self.port_fwd)
        self.socket = None



    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host_name, self.port_listen))
        print "Bound socket on {}: {}".format(self.host_name, self.port_listen)
        command = ''

        try:
            while 1:
                command = raw_input('Command syntax: <Receiver Name> <Message> (Do not use brackets)\nE.g. student0 Howdy there!\nEnter command: ')
                if command.lower() == 'quit' or command.lower() == 'q':
                    break
                node = command[:command.find(' ')]
                message = command[command.find(' ')+1:]

                echo_msg = self.create_msg(node, message)
                self.send_and_receive(echo_msg)

        except KeyboardInterrupt as ki:
            pass
        except Exception as e:
            print str(e)
        finally:
            self.shutdown()

    def shutdown(self):
        if self.socket: self.socket.close()

    def create_msg(self, node, message):
        echo_msg = EchoMessage(NAME, node, message)
        return echo_msg.encode()

    def send_and_receive(self, message):
        """
        Send a message to the server and return the server's response.  A message is
        sent by creating a socket and giving the socket the server's address.  The
        socket receives a message from the server where the data is stored, the socket
        is closed, and the data is returned.
        """


        print 'Sending message {} to {}'.format(message, self.echo_addr)
        sent_message = self.socket.sendto(message, self.echo_addr)

        print 'waiting for at least 20 seconds for response...\n\n'
        self.socket.settimeout(20)
        try:
            data, responder = self.socket.recvfrom(10000)
            echo_msg = EchoMessage()
            echo_msg.decode(data)
            print 'Response received: %s\nFrom: %s' % (echo_msg.msg, echo_msg.from_node)
        except socket.timeout:
            print 'No response received, timing out.'

    def get_ip(self):
        """
        http://stackoverflow.com/a/33245570

        because socket.gethostbyname(socket.gethostname()) was returning 127.0.0.1
        """
        import os
        _file = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
        ip = _file.read().strip('\n')
        return ip




if __name__ == "__main__":
    client = EchoClient(ECHO_CLIENT_PORT, ECHO_PORT)
    print 'running client'
    client.start()
    client.shutdown()
