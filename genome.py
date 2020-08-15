#!/usr/bin/env python3
from gene import ConnectionGene
from dataclasses import dataclass
from enum import Enum

class NodeType(Enum):
    input = 'input'
    output = 'output'
    bias = 'bias'
    hidden = 'hidden'

class Genome:
    def __init__(self, num_inputs, num_outputs):
        """
        Initialize a genome. Since reproduction happens through cloning, this
        function is used solely to create the initial ~queen genome~
        """
        self.node_genes = []
        self.connection_genes = []

        for out in range(num_outputs):
            self.node_genes[out] = 'output'

        for inp in range(num_inputs):
            self.node_genes[inp] = 'input'
            for out in range(num_outputs):
                con = ConnectionGene(inp, out)
                self.connection_genes.append(con)

