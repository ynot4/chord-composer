import random


class Vertex(object):
    def __init__(self, value):
        self.value = value  # the value will be the chord
        self.adjacent = {}  # nodes that it points to
        self.neighbors = []
        self.neighbors_weights = []

    def __str__(self):
        return self.value + ' '.join([node.value for node in self.adjacent.keys()])
    # node is a key and self.adjacent.keys is a list of keys

    def add_edge_to(self, vertex, weight=0):
        # adding an edge to the vertex we input with weight
        self.adjacent[vertex] = weight

    def increment_edge(self, vertex):
        # incrementing weight of edge
        self.adjacent[vertex] = self.adjacent.get(vertex, 0) + 1

    def get_adjacent_nodes(self):
        return self.adjacent.keys()

    # initializes probability map
    def get_probability_map(self):
        for (vertex, weight) in self.adjacent.items():
            # items returns each dict item as tuples in a list
            self.neighbors.append(vertex)
            self.neighbors_weights.append(weight)

    def next_word(self):
        # randomly select next word based on weights
        return random.choices(self.neighbors, weights=self.neighbors_weights)[0]


class Graph(object):
    # object accepts no arguments and returns a new featureless instance when called
    def __init__(self):
        self.vertices = {}

    def get_vertex_values(self):
        # return all possible chords
        return set(self.vertices.keys())

    def add_vertex(self, value):
        self.vertices[value] = Vertex(value)
        # access dict item with key of 'value' variable

    def get_vertex(self, value):
        if value not in self.vertices:
            self.add_vertex(value)  # add to dict if not added already
        return self.vertices[value]

    def get_next_word(self, current_vertex):
        return self.vertices[current_vertex.value].next_word()

    def generate_probability_mappings(self):
        for vertex in self.vertices.values():
            vertex.get_probability_map()
