#!/usr/bin/env python3

import math
from dataclasses import dataclass
from loguru import logger

@dataclass
class Weight:
    input_node: int
    output_node: int
    weight: float

class Neuron:
    def __init__(self, node_id, typ):
        self._id = node_id
        self.value = 0
        self._outputs = []
        self.excited = False
        self.activation_threshold = 0.5
        self.typ = typ

    def __repr__(self):
        return 'Neuron(id = {}, value = {})'.format(self._id, self.value)

    def add_output(self, weight):
        self._outputs.append(weight)

    def feed(self, value):
        self.value += value
        if abs(self.value) >= self.activation_threshold:
            self.excited = True

    def activate(self, value):
        # TODO: pull activation function from config
        return math.tanh(value)

    def fire(self):
        if not self.typ == 'input':
            self.value = self.activate(self.value)
        for weight in self._outputs:
            out_node = weight.output_node
            base_value = self.value * weight.weight
            out_node.feed(base_value)
        self.excited = False

class Network:
    def __init__(self, genome):
        self.nodes = []
        self.input_nodes = []
        self.output_nodes = []
        self.weights = []
        self.output = []
        self.output_fired = False

        for nid, typ in genome.node_genes.items():
            new_node = Neuron(nid,typ)
            self.nodes.append(new_node)
            if typ == 'input':
                self.input_nodes.append(new_node)
            if typ == 'output':
                self.output_nodes.append(new_node)

        for g in genome.connection_genes:
            if not g.enabled:
                continue
            in_neuron = self.get_neuron_by_id(g.in_node)
            out_neuron = self.get_neuron_by_id(g.out_node)
            w = Weight(in_neuron, out_neuron, g.weight)
            in_neuron.add_output(w)
            self.weights.append(w)


    def get_neuron_by_id(self, neuron_id):
        for n in self.nodes:
            if n._id == neuron_id:
                return n
        raise Exception('No neuron with id {}'.format(neuron_id))

    def get_current_state(self):
        return [n.activate(n.value) for n in self.output_nodes]

    def reset(self,):
        self.output_fired = False
        for n in self.nodes:
            n.value = 0
            n.excited = False

    def evaluate(self, input_values = None):
        # TODO: make proper debugging utilities to confirm that this is working
        # as intended

        # assert that the amount of input values matches the amount of input
        # neurons, and assign the values if it does
        logger.debug('evaluating network')
        if input_values:
            if len(input_values) != len(self.input_nodes):
                raise Exception('input size mismatch')

            for i, node in enumerate(self.input_nodes):
                node.value = input_values[i]
                node.excited = True

        excited_nodes = filter(lambda n: n.excited, self.nodes)
        exhausted_nodes = []

        for node in excited_nodes:
            node.value -= 0.1
            if node not in exhausted_nodes:
                if node.typ == 'output':
                    node.value = node.activate(node.value)
                    self.output_fired = True
                    continue
                node.fire()
                exhausted_nodes.append(node)
        if self.output_fired:
            self.output = self.get_current_state()
