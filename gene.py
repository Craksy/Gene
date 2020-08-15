#!/usr/bin/env python3
from functools import namedtuple

class Innovation:
    next_innovation = 0

    @classmethod
    def get_next(cls):
        cls.next_innovation += 1
        return cls.next_innovation

class ConnectionGene:
    def __init__(self, in_node, out_node, weight):
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.enabled = True
        self.innovation = Innovation.get_next()
