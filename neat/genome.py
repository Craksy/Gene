#!/usr/bin/env python3
from dataclasses import dataclass
from enum import Enum
from copy import deepcopy
from functools import namedtuple
import random
from loguru import logger

class Innovation:
    next_innovation = 0

    @classmethod
    def get_next(cls):
        cls.next_innovation += 1
        return cls.next_innovation


@dataclass
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

    def copy(self):
        return deepcopy(self)

    def __repr__(self):
         return 'Connection(in{}|out{}|inno{})'.format(self.in_node,
                                                    self.out_node,
                                                    self.innovation)

class Genome:
    # TODO: give each genome an ID.
    def __init__(self, num_inputs, num_outputs):
        """
        Initialize a genome. Since reproduction happens through cloning, this
        function is used solely to create the initial ~queen genome~
        """
        self.next_node_id = 0
        self.fitness = 0
        self.node_genes = {}
        self.connection_genes = []
        self.species = None
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

        for inp in range(num_inputs):
            self.add_node('input')

        for out in range(num_outputs):
            self.add_node('output')


    def initialize_genome(self):
        """
        initialize the genome with input and output nodes and fully connect
        them
        """
        logger.debug('creating genome')

        for inp in self.get_nodes_by_type('input'):
            for out in self.get_nodes_by_type('output'):
                rweight = self.generate_random_weight()
                con = ConnectionGene(inp, out, rweight)
                self.connection_genes.append(con)

    def get_nodes_by_type(self, typ):
        return [nid for nid,t in self.node_genes.items() if t == typ]

    def has_connection(self, in_node, out_node):
        for con in self.connection_genes:
            if con.in_node == in_node and con.out_node == out_node:
                return True
        return False

    def has_node(self, node_id):
        return node_id in self.node_genes

    def generate_random_weight(self):
        return random.uniform(-2, 2)

    def add_node(self, typ):
        identity = self.next_node_id
        self.next_node_id += 1
        self.node_genes[identity] = typ
        return identity

    def clone(self):
        return deepcopy(self)

    def mutate(self):
        # Randomly apply different mutations according to configured
        # probabilities

        # TODO: pull mutate probabilities from config
        probabilities = dict(
            new_node = .20,
            new_weight = .35,
            modify_weight = .6,
            mutate_again = .2
        )
        logger.debug('mutating')

        r = random.random()
        if r <= probabilities['new_node']:
            self.mutate_new_node()

        r = random.random()
        if r <= probabilities['new_weight']:
            self.mutate_new_weight()

        r = random.random()
        if r <= probabilities['modify_weight']:
            self.mutate_modify_weight()

        r = random.random()
        if r <= probabilities['mutate_again']:
            logger.debug('mutating again')
            self.mutate()

    def mutate_modify_weight(self):
        logger.debug('modifying existing weight')
        con = random.choice(self.connection_genes)
        amount = random.random() - .5
        con.weight += amount

    def mutate_new_node(self):
        logger.debug('mutating new node')
        old_con:ConnectionGene = random.choice(self.connection_genes)

        node = self.add_node('hidden')
        mirror_in = old_con.in_node
        fresh_out = old_con.out_node
        old_con.enabled = False

        new_weight = self.generate_random_weight()
        mirror_connection = ConnectionGene(mirror_in, node, old_con.weight)
        fresh_connection = ConnectionGene(node, fresh_out, new_weight)
        self.connection_genes.append(mirror_connection)
        self.connection_genes.append(fresh_connection)

    def mutate_new_weight(self):
         # find possibly pairs of unconnected nodes

         # TODO: see if i can't find a better solution here than looping through
         # every connection, for every node, for every node. it's 3 nested
         # loops, potentially looping through every single combination of
         # elements in the network.

         # REVIEW: if we add a weight that has previously been disabled, should we just reenable it instead?

         matches = []
         logger.debug('mutating new weight')
         for id1, typ1 in self.node_genes.items():
            for id2, typ2 in self.node_genes.items():
                if typ2 == 'input' or \
                   typ1 == 'output' or \
                   id1 == id2:
                    continue

                # search through all connection genes to find out if any of them
                # connects n1 and n2
                connected = False
                # logger.debug('\tchecking node pair: {}, {}',
                             # id1, id2)
                for con in self.connection_genes:
                    # logger.debug('checking connection: {}',
                                 # repr(con))
                    if (con.in_node == id1 and con.out_node == id2):
                        # logger.debug('{},{} is connected by {}. continue',
                                     # id1, id2, repr(con))
                        connected = True
                        break

                # if no gene connects the pair, add that pair to our list of
                # viable connections
                if not connected:
                    # logger.debug('\t\tpair not connected. adding to matches')
                    matches.append((id1, id2))

         if not matches:
            return
            raise Exception('Failed to mutate weight. No unconnected nodes excist')
         # logger.debug('\tmatches {}', str(matches))

         # pick a pair randomly from the found matches.
         n1, n2 = random.choice(matches)
         logger.debug('adding new weight between: {}, {}', n1, n2)
         new_weight = self.generate_random_weight()
         new_con = ConnectionGene(n1, n2, new_weight)
         self.connection_genes.append(new_con)
