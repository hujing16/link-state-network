__author__ = 'montanawong'

from FwdEchoThread import FwdEchoThread
from LMBroadcastThread import LMBroadcaster
from LMReceiveThread import LMListener
import config
import time


class LSRouter(object):
    """
    Class represents a master router that spawns multiple threads to handle UDP communication in a simulated
    Link state network.
    """
    def __init__(self):
        self.name = config.NODE
        self.neighbors = ['student0']  #contains student0
        self.routing_table = {self.name: None}  # add route to itself -- no hop
        self.link_table = {self.name: list()}
        self.node_port_map = dict()
        self.threads = list()
        self.ECHO_PORT = config.ECHO_PORT
        self.LINK_STATE_PORT = config.LINK_STATE_PORT

        # initialize data structures
        self.init_port_map(); self.init_link_table(); self.init_routing_table()

        # create routing table updater object
        self.rc = RouteUpdater(self.name, self.routing_table, self.link_table, self.neighbors)

    def start(self):
        """
        Start the Router
        """
        # create thread objects
        lm_listener = LMListener(self.link_table, self.LINK_STATE_PORT)
        lm_broadcaster = LMBroadcaster(self.node_port_map, self.link_table)
        fwd_echoer = FwdEchoThread(self.routing_table, self.node_port_map, self.ECHO_PORT)

        # organize into list
        self.threads = [lm_listener, fwd_echoer, lm_broadcaster]
        # start all threads
        [thread.start() for thread in self.threads]

        while 1 == 1:
            # every 30 seconds recompute routing table using Djikstra's algorithm
            time.sleep(30)
            self.update_table()

    def init_routing_table(self):
        # initialize routing table w/ closest neighbors and set next hop to itself
        map(lambda neighbor: self.routing_table.__setitem__(neighbor, neighbor), self.neighbors)

    def init_link_table(self):
        # structure: {'student0': [['denver', EXPIRATION_TIME], ['salida', EXPIRATION_TIME]] }
        # initialize link table, set expiration times to now + 120 sec
        map(lambda neighbor: self.link_table.__setitem__(neighbor, [[self.name, time.time() + 120]]), self.neighbors)
        # also store the reverse
        map(lambda neighbor: self.link_table[self.name].append([neighbor, time.time() + 120]), self.neighbors)

    def init_port_map(self):
        """
        Initalize the port to node map
        """
        with open(config.PORT_LIST, 'r') as _file:
            # ignore first line in file (header)
            _file.readline()

            for line in _file.readlines():
                # Map each node name to its ports from the csv file
                node, lm_port, fwd_port = line.split(',')
                # e.g. {'student0': (20020, 20021)}
                self.node_port_map[node] = (int(lm_port), int(fwd_port))
            # We have read all lines in the file

    def update_table(self):
        """
        call to update the routing table by applying dijkstra's algorithm on our link table
        """
        print 'Updating routing table'
        self.rc.apply_dijkstras()
        print str(self)

    def shutdown(self):
        """
        Gracefully shut down the router and all of its threads
        """
        [thread.kill() for thread in self.threads]

    def __str__(self):
        return 'Routing table: %s\n\nLink table: %s\n\nNeighbors: %s\n\nListening on ports:%d & %d' % (
            str(self.routing_table),
            str(self.link_table),
            str(self.neighbors),
            self.LINK_STATE_PORT,
            self.ECHO_PORT
        )


class RouteUpdater(object):
    """
    Utility class that provides an interface to update a routing table
    in a Link State based network node
    """
    def __init__(self, our_node, routing_table, link_table, neighbors):
        self.our_node = our_node

        self.routing_table = routing_table
        self.link_table = link_table
        self.neighbors = neighbors

    def apply_dijkstras(self):
        """
        Applies Dijkstra's algorithm to update routing table.
        :return:
        """
        # initialize the initial frontier
        frontier = [[self.our_node]]
        explored = set()
        explored.add(self.our_node)
        while len(frontier) > 0:
            # Do a best first search until there are no more paths to explore.
            curr_path = frontier.pop(0)
            node = curr_path[-1]
            # first get neighbors of this node
            for neighbor in self.get_neighbors(node):
                if neighbor in explored:
                    # if we have already seen this node, then
                    # we can ignore it because we have found a faster
                    # route to it than the current path
                    continue
                else:
                    # we haven't seen this node yet, and we are setting
                    # the first node in the path as our first hop.
                    # our node is at index 0, so we use index 1 here.
                    # need conditional to handle case where we are searching our node's
                    # direct neighbors.
                    self.routing_table[neighbor] = curr_path[1] if len(curr_path) >= 2 else neighbor
                    # add this neighbor to explored so we can ignore all future sightings
                    explored.add(neighbor)
                    # add neighbor to the end of this path so we can check its neighbors
                    # when Dijkstra's gets further down on its iterations.
                    frontier.append(curr_path + [neighbor])
        # no more paths to explore. Give control back to router obj.

    def get_neighbors(self, node):
        """
        returns the neighbors of a given node by parsing the link table, only non
        expired links are considered
        example tuple: ('student0', 123131332)
        :param node: the node whose neighbors we want to return
        :return: list of neighbors strings
        """
        return [_tuple[0] for _tuple in self.link_table[node] if _tuple[1] > time.time()]


if __name__ == '__main__':
    router = LSRouter()
    try:
        router.start()
    except KeyboardInterrupt as ki:
        print 'Shutting down router'
    finally:
        router.shutdown()


