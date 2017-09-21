from random import randrange
import time
from math import sqrt
from math import ceil
from copy import copy
import random

def getFileLines(file):
    with open(file) as f:
        lines = f.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].strip('\n')
    return lines

class Graph:
    def __init__(self, vertexNumber = None, edgeNumber = None, edges = None):
        '''
        :param vertexNumber: Number of vertices in the graph
        :param edgeNumber: Number of edges in the graph
        :param edges: list of edges (v1, v2, w)
        '''
        if vertexNumber == None:
            self.vertexNumber = 0
            self.edgeNumber = 0
            self.graph = {}
            self.vertices = set()
        else:
            self.vertexNumber = vertexNumber
            self.edgeNumber = edgeNumber
            edges = [i + [0] for i in edges]#add age to edges
            self.graph = self.createGraph(edges)
            self.vertices = self.createVerticesSet(edges)

    def createVerticesSet(self, edges):
        vertices = set()
        for edge in edges:
            vertices.add(edge[0])
            vertices.add(edge[1])
        return vertices

    def createGraph(self, edges):
        '''
        Create the graph, one entry from e1 to e2 and one from e2 to e1
        :param edges: list of edges ([[v1, v2, weight, age]])
        :return: graph ({v1:{v2_1:{"W":weight, "A":age}, v2_2:{"W":weight,\
         "A":age}, ...}})
        '''
        graph = {}
        for edge in edges:
            graph[edge[0]] = {}
            graph[edge[1]] = {}
        for edge in edges:
            graph[edge[0]][edge[1]] = {"W":edge[2], "A":edge[3]}
            graph[edge[1]][edge[0]] = {"W":edge[2], "A":edge[3]}
        return graph

    def addEdge(self, edge):
        if edge[0] not in self.graph:
            self.graph[edge[0]] = {}
        if edge[1] not in self.graph:
            self.graph[edge[1]] = {}
        self.graph[edge[0]][edge[1]] = {"W":edge[2], "A":edge[3]}
        self.graph[edge[1]][edge[0]] = {"W":edge[2], "A":edge[3]}
        self.vertices.add(edge[0])
        self.vertices.add(edge[1])

    def addVertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = {}
        self.vertices.add(vertex)

    def removeEdge(self, edge):
        del self.graph[edge[0]][edge[1]]
        if len(self.graph[edge[0]]) == 0:
            del self.graph[edge[0]]
            self.vertices.remove(edge[0])
        del self.graph[edge[1]][edge[0]]
        if len(self.graph[edge[1]]) == 0:
            del self.graph[edge[1]]
            self.vertices.remove(edge[1])
        self.vertexNumber -= 1
        self.edgeNumber -= 1

    def addAgeToEdge(self, edge, age):
        self.graph[edge[0]][edge[1]]["A"] += age
        self.graph[edge[1]][edge[0]]["A"] += age

    def getEdgesConnectedToVertex(self, vertex):
        edges = set()
        if vertex in self.graph:
            vList = self.graph[vertex].keys()
            for v in vList:
                edges.add((vertex, v, self.graph[vertex][v]["W"], \
                           self.graph[vertex][v]["A"]))
        return edges
    def getEdges(self):
        edges = []
        edge_mirror = []
        for origin in self.graph:
            for destiny in self.graph[origin]:
                edge = [origin, destiny, self.graph[origin][destiny]["W"], \
                        self.graph[origin][destiny]["A"]]
                if edge not in edge_mirror:
                    edges.append(edge)
                    edge_mirror.append([destiny, origin, self.graph[origin] \
                        [destiny]["W"], self.graph[origin][destiny]["A"]])
        return edges

    def printEdges(self):
        edges = self.getEdges()
        for edge in edges:
            print(edge)

    def getSize(self):
        size = 0
        for edge in self.getEdges():
            size += edge[2]
        return size
    def getCopy(self):
        gCopy = Graph()
        gCopy.vertexNumber = self.vertexNumber
        gCopy.edgeNumber = self.edgeNumber
        for edge in self.getEdges():
            gCopy.addEdge(edge)
        for vertex in self.vertices:
            gCopy.addVertex(vertex)
        return gCopy

class Instance:
    def __init__(self, file = None):
        '''
        :param file: get the instance file location, if "None" init an empty \
        instance.
        '''
        if file == None:
            self.graph = None
            self.terminals = None
        else:
            iList = self.loadInstance(file)
            self.graph = Graph(iList[0][0], iList[0][1], iList[1:-2])
            self.terminals = iList[-1] 

    def loadInstance(self, file):
        lines = getFileLines(file)
        instance = []
        for line in lines:
            info = line.split(" ")
            offset = 0
            for i in range(len(info)):
                if info[i - offset] == "":
                    del info[i - offset]
                    offset += 1
            instance.append([int(i) for i in info])
        return instance

    def isThereDisconnectedTerminals(self):
        for t in self.terminals:
            if t not in self.graph.vertices:
                return True
        return False

    def simplify(self):
        done = False
        while not done:
            done = True
            for v in list(self.graph.graph):
                if len(self.graph.graph[v]) == 1 and v not in self.terminals:
                    done = False
                    self.graph.removeEdge([v, list(self.graph.graph[v])[0]])
                    break

def moddedPrim(graph, origin, terminals, alpha):
    graph = graph.getCopy()
    if graph.graph == {}:
        return graph
    _graph = Graph()
    _graph.addVertex(origin)
    terminals = set(terminals)
    visitedVertices = set()
    availableEdges = set()
    while terminals != _graph.vertices.intersection(terminals):
        for vertex in _graph.vertices.difference(visitedVertices):
            availableEdges = availableEdges.union(graph.getEdgesConnectedToVertex(vertex))
            visitedVertices.add(vertex)
        minE = min(availableEdges, key=lambda edge: edge[2])[2]
        maxE = max(availableEdges, key=lambda edge: edge[2])[2]
        validEdges = [edge for edge in availableEdges if edge[2] <= (\
            minE + alpha*(maxE - minE))]
        chosenEdge = validEdges[randrange(len(validEdges))]
        if chosenEdge[1] not in _graph.vertices:
            _graph.addEdge(chosenEdge)
        graph.removeEdge(chosenEdge)
        availableEdges.remove(chosenEdge)
        rChosenEdge = (chosenEdge[1], chosenEdge[0], chosenEdge[2], chosenEdge[3])
        if rChosenEdge in availableEdges:
            availableEdges.remove(rChosenEdge)
    return _graph

def dreyfusWagner(graph, terminals):
    return moddedPrim(graph, terminals[0], terminals, 0)

def adapt(instance, redInsSolution, ageMax):
    edges = instance.graph.getEdges()
    solEdges = redInsSolution.getEdges()
    for index in range(len(solEdges)):
        solEdges[index][3] += 1
    for index in range(len(edges)):
        instance.graph.addAgeToEdge(edges[index], 1)
        edges[index][3] += 1
    for index in range(len(edges)):
        if edges[index] in solEdges:
            instance.graph.addAgeToEdge(edges[index], -(edges[index][3]))
    for index in range(len(edges)):
        if edges[index][3] > ageMax:
            instance.graph.removeEdge(edges[index])

def cmsa(instance, hProp, ageMax, alpha, execTime = 1):
    instance.simplify()
    solBest = Instance()
    solBest.terminals = copy(instance.terminals)
    solBest.graph = instance.graph.getCopy()
    redInstance = Instance()
    redInstance.terminals = copy(instance.terminals)
    redInstance.graph = Graph()
    initTime = time.time()
    sqrtVNumberCeil = ceil(sqrt(len(instance.graph.vertices)))
    while time.time() - initTime < execTime*sqrtVNumberCeil:
        hSolution = Instance()
        hSolution.terminals = copy(instance.terminals)
        for iteration in range(int(ceil(hProp*sqrtVNumberCeil))):
            hSolution.graph = moddedPrim(copy(instance.graph), random.choice(\
                instance.terminals), instance.terminals, alpha)
            hSEdges = hSolution.graph.getEdges()
            redInsEdges = redInstance.graph.getEdges()
            for i in range(len(hSEdges)):
                if hSEdges[i] not in redInsEdges:
                    hSEdges[i][3] = 0
                    redInstance.graph.addEdge(hSEdges[i])
        redInstance.simplify()
        optSolRedIns = dreyfusWagner(redInstance.graph, redInstance.terminals)
        if optSolRedIns.getSize() < solBest.graph.getSize():
            solBest.graph = optSolRedIns.getCopy()
        adapt(redInstance, optSolRedIns, ageMax)
        solBest.simplify()
    return solBest

def main():
    i = "Instances/steine11.txt"
    instance = Instance(i)
    if instance.isThereDisconnectedTerminals():
        print("There is no Steiner tree in this instance")
        return None
    print(len(instance.graph.vertices))
    solution = cmsa(instance, 0.1, 12, 0.11, 2)
    print(solution.graph.getSize())

main()
