#!/usr/bin/env python3
from gene import ConnectionGene
from dataclasses import dataclass
from enum import Enum
from copy import deepcopy
from functools import namedtuple
import random
from logger import logger


class Innovation:
    next_innovation = 0

    @classmethod
    def get_next(cls):
        cls.next_innovation += 1
        return cls.next_innovation

class NodeType(Enum):
    # TODO: decide if i actually want this is an enum.
    # so far i've just been checking against raw strings anyway.
    input = 'input'
    output = 'output'
    bias = 'bias'
    hidden = 'hidden'

@dataclass()
class NodeGene:
    identity: int
    typ: str

    def __repr__(self):
        return 'N' + str(self.identity)



class ConnectionGene:
    def __init__(self, in_node, out_node, weight):
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.enabled = True
        self.innovation = Innovation.get_next()

    def __repr__(self):
         return 'ConnectionGene({}, {}, {})'.format(self.in_node,
                                                    self.out_node,
                                                    self.weight)

class Genome:
    def __init__(self, num_inputs, num_outputs):
        """
        Initialize a genome. Since reproduction happens through cloning, this
        function is used solely to create the initial ~queen genome~
        """
        self.node_genes = []
        self.connection_genes = []
        logger.debug('creating genome')

        # generator for node ids
        # this might make the implementation prettier elsewhere in the code, but
        # this in itself is pretty ugly
        def id_gen():
            next_id = 0
            while True:
                yield next_id
                next_id += 1

        self.node_ids = id_gen()

        # initialize the genome with input and output nodes and fully connect
        # them
        for out in range(num_outputs):
            self.add_node(NodeType.output)

        for inp in range(num_outputs, num_inputs+num_outputs):
            self.add_node(NodeType.input)
            for out in range(num_outputs):
                con = ConnectionGene(inp, out, 0)
                self.connection_genes.append(con)

    def add_node(self, typ):
        identity = next(self.node_ids)
        self.node_genes.append(NodeGene(identity=identity, typ=typ))
        return identity

    def clone(self):
        return deepcopy(self)

    def mutate(self):
        # Randomly apply different mutations according to configured
        # probabilities
        pass

    def mutate_new_node(self):
        # TODO: disable old weight and create two entirely new connection genes.
        logger.debug('mutating new node')
        con:ConnectionGene = random.choice(self.connection_genes)
        node = self.add_node(NodeType.hidden)
        old_out = con.out_node
        con.out_node = node
        new_connection = ConnectionGene(node, old_out, 0)
        self.connection_genes.append(new_connection)

    def mutate_new_weight(self):
         # find possibly pairs of unconnected nodes

         # TODO: see if i can't find a better solution here than looping through
         # every connection, for every node, for every node. it's 3 nested
         # loops, potentially looping through every single combination of
         # elements in the network.
         matches = []
         logger.debug('mutating new weight')
         for n1 in self.node_genes:
            for n2 in self.node_genes:
                if n2.typ.value == 'input' or \
                   n1.typ.value == 'output' or \
                   n1 is n2:
                    continue

                # search through all connection genes to find out if any of them
                # connects n1 and n2
                connected = False
                logger.debug('\tchecking node pair: %s, %s',
                             n1, n2)
                for con in self.connection_genes:
                    logger.debug('\t\tchecking connection: %s',
                                 con)
                    if (con.in_node == n1.identity and con.out_node == n2.identity):
                        logger.debug('\t\t%s,%s is connected by %s. continue',
                                     n1, n2, con)
                        connected = True
                        break

                # if no gene connects the pair, add that pair to our list of
                # viable connections
                if not connected:
                    logger.debug('\t\tpair not connected. adding to matches')
                    matches.append((n1.identity, n2.identity))

         if not matches:
            raise Exception('Failed to mutate weight. No unconnected nodes excist')
         logger.debug('\tmatches %s', matches)

         # pick a pair randomly from the found matches.
         n1, n2 = random.choice(matches)
         logger.debug('\tpicked match: %s, %s', n1, n2)
         new_con = ConnectionGene(n1, n2, 0)
         self.connection_genes.append(new_con)
