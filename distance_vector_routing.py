# Author: Elia Mercatanti
# Matricola: 5619856

import inspect
import copy

class DVRouting:

    def __init__(self, network_graph):
        if not self.check_links_costs(network_graph):
            raise Exception('The cost of some links is negative.')
        if not self.check_costs_symmetry(network_graph):
            raise Exception('The cost of some links are not symmetrical.')
        if not self.check_autolink(network_graph):
            raise Exception('The autolink of some node is not 0.')
        self.network_graph = network_graph
        self.dvList = self.initialize_dvList()
        self.routing_tables = self.initialize_routing()

    def check_links_costs(self, network_graph):
        for links_costs in network_graph:
            for cost in links_costs.itervalues():
                if cost < 0:
                    return False
        return True

    def check_costs_symmetry(self, network_graph):
        for node_x in range(len(network_graph)):
            for node_y in network_graph[node_x].iterkeys():
                if node_x in network_graph[node_y]:
                    if network_graph[node_x][node_y] != network_graph[node_y][node_x]:
                        return False
                else:
                    return False
        return True

    def check_autolink(self, network_graph):
        for node in range(len(network_graph)):
            if (node in network_graph[node]) and (network_graph[node][node] != 0):
                return False
        return True

    def initialize_dvList(self):
        dvList = []
        for i in range(len(self.network_graph)):
            dvList.append([])
            for j in range(len(self.network_graph)):
                if i == j:
                    dvList[i].append(0)
                elif j in self.network_graph[i]:
                    dvList[i].append(self.network_graph[i][j])
                else:
                    dvList[i].append(None)
        return dvList

    def initialize_routing(self):
        routing_tables = []
        for i in range(len(self.network_graph)):
            routing_tables.append([])
            for j in range(len(self.network_graph)):
                if i == j:
                    routing_tables[i].append(i)
                elif j in self.network_graph[i]:
                    routing_tables[i].append(j)
                else:
                    routing_tables[i].append(None)
        return routing_tables

    def is_an_index_node(self, index):
        if 0 <= index < len(self.network_graph):
            return True
        else:
            return False

    def weight(self, x, y):
        if not self.is_an_index_node(x):
            return None
        elif y in self.network_graph[x]:
            return self.network_graph[x][y]
        elif x == y:
            return 0
        else:
            return None

    def set(self, x, y, w):
        if (w is not None) and (w < 0):
            raise Exception('The cost of the specified link is negative.')
        elif (not self.is_an_index_node(x)) or (not self.is_an_index_node(y)):
            raise Exception('The index of a node does not exist.')
        elif (x == y) and (w != 0):
            raise Exception('The cost of an autolink must be 0.')
        elif w is None:
            if y in self.network_graph[x]:
                del self.network_graph[x][y]
            if x in self.network_graph[y]:
                del self.network_graph[y][x]
        else:
            self.network_graph[x][y] = w
            self.network_graph[y][x] = w

    def add(self):
        self.network_graph.append({len(self.network_graph): 0})
        for i in range(len(self.network_graph)):
            if i != len(self.network_graph) - 1:
                self.dvList[i].append(None)
                self.routing_tables[i].append(None)
            else:
                self.dvList.append([])
                self.routing_tables.append([])
                for j in range(len(self.network_graph)):
                    if j != len(self.network_graph) - 1:
                        self.routing_tables[i].append(None)
                        self.dvList[i].append(None)
                    else:
                        self.routing_tables[i].append(j)
                        self.dvList[i].append(0)
        return len(self.network_graph) - 1

    def remove(self, x):
        if self.is_an_index_node(x):
            for node_index in range(len(self.network_graph)):
                if node_index != x:
                    self.set(x, node_index, None)

    def setdv(self, dvlist):
        if len(dvlist) == len(self.network_graph):
            for i in range(len(self.network_graph)):
                if all(element is None for element in dvlist[i]):
                    dvlist[i][i] = 0
            self.dvList = dvlist
        else:
            raise Exception('The dvlist as a different number of nodes compare to the network.')

    def getdv(self, x):
        if self.is_an_index_node(x):
            return self.dvList[x]
        else:
            return None

    def dv_algorithm(self):
        temp_dvList = copy.deepcopy(self.dvList)
        temp_routeT = copy.deepcopy(self.routing_tables)
        limit = len(self.network_graph)
        for node_x in range(limit):
            for node_y in range(limit):
                if node_x == node_y and self.dvList[node_x][node_y] != 0:
                    temp_dvList[node_x][node_y] = 0
                elif node_x != node_y:
                    min = float("inf")
                    for v in range(limit):
                        if (v in self.network_graph[node_x]) and (v != node_x):
                            dv_cost = self.getdv(v)[node_y]
                            if dv_cost is None:
                                dv_cost = float("inf")
                            new_cost = self.weight(node_x, v) + dv_cost
                            if new_cost < min:
                                min = new_cost
                                v_route = v
                    if min == float("inf"):
                        temp_dvList[node_x][node_y] = None
                    else:
                        temp_dvList[node_x][node_y] = min
                        temp_routeT[node_x][node_y] = v_route
        return temp_dvList, temp_routeT

    def step(self):
        temp_dvList, temp_routeT = self.dv_algorithm()
        if temp_dvList == self.dvList:
            return True
        else:
            self.dvList = copy.deepcopy(temp_dvList)
            self.routing_tables = copy.deepcopy(temp_routeT)
            return self.isstable()

    def isstable(self):
        temp_dvList , temp_routeT = self.dv_algorithm()
        if temp_dvList == self.dvList:
            return True
        else:
            return False

    def compute(self):
        iter = 0
        if not self.isstable():
            while True:
                iter += 1
                if self.step():
                    break
        return iter

    def route(self, x, y):
        if self.is_an_index_node(x) and self.is_an_index_node(y):
            if x != y:
                z = self.routing_tables[x][y]
                if (z is not None) and (self.weight(x, z) is not None) and (self.dvList[z][y] is not None):
                    w = self.weight(x, z) + self.dvList[z][y]
                    return z, w
                else:
                    return None
            else:
                return x, 0
        else:
            return None