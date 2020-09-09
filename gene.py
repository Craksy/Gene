#!/usr/bin/env python3

from genome import Genome
from species import Species
# from logger import logger
from typing import List
import math
import random
from loguru import logger

class Gene:
    def __init__(self, configuration):
        # self.config = configuration
        # HACK: actually implement this, instead of this duct tape solution.
        # in fact i'm not even using this anywhere.
        # at this point i'm just writting meaningless comments to procrastinate.
        self.config = dict(
            fitness_function = lambda g: ...,
            compatibility_threshold = .2
        )
        self._next_id = 0
        self.species:List[Species] = []

        logger.remove()
        logger.add('debug.log',
                   format='<green>{time:HH:mm:ss}</green> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
                   level='DEBUG', colorize=True)

    def get_next_species_id(self):
        self._next_id += 1
        return self._next_id

    def init_population(self):
        logger.debug('creating initial population')
        first_queen = Genome(3,2)
        first_queen.initialize_genome()

        initial_species = self.add_new_species(first_queen)
        while len(initial_species.population) < initial_species.population_limit:
            new_genome = initial_species.queen.clone()
            new_genome.mutate()
            initial_species.add_genome(new_genome)

    def add_new_species(self, queen):
        logger.debug('adding new species from queen genome {}', queen)
        new_species = Species(queen, self.get_next_species_id())
        self.species.append(new_species)
        return new_species

    def speciate_population(self):
        """
        Speciate the population by comparing each genome and grouping them by
        similarity in topology.
        """

        # compile a list of all genomes from all species. this is done to avoid
        # modifying the length of an iterator as we're looping through it
        #
        # REVIEW: consider if i should just maintain the population list
        # continously, instead of compiling it every time i speciate

        logger.debug('speciating')
        logger.debug('compiling population list')
        population = []
        for sp in self.species:
            for genome in sp.population:
                population.append(genome)
        # TODO: pull comparison threshold from config
        comp_threshold = 7

        for genome in population:
            # yeah this doesn't really make sense untill i give genomes ids.
            logger.debug('checking genome {}', genome)
            compatible = False
            for sp in self.species:
                logger.debug('checking compatibility with species ({})',
                             sp.identity)
                comp_score = sp.get_compatibility_score(genome)
                if comp_score < comp_threshold:
                    logger.debug('genome was compatible({}). assigning to species.', comp_score)
                    # if genome already belongs to a species remove it from that
                    # species
                    if genome.species:
                        genome.species.remove_genome(genome)
                    sp.add_genome(genome)
                    compatible = True
                    break
            if compatible:
                continue

            logger.debug('found no compatible species. creating new one from genome')
            genome.species.remove_genome(genome)
            self.add_new_species(genome)

    def cull_population(self):
        """
        Eliminate the worst performing genomes from each species
        """
        for sp in self.species:
            # TODO: culling should probably be a method of the species class
            sp.population = sorted(sp.population, key=lambda g: g.fitness)
            popsize = len(sp.populaton)
            halfpop = math.floor(popsize/2)
            sp.population = sp.population[halfpop:]


    def crossover(self, parent_a:Genome, parent_b:Genome):
        pa_innovs = {g.innovation:g for g in parent_a.connection_genes}
        pb_innovs = {g.innovation:g for g in parent_b.connection_genes}
        pa_set = set(pa_innovs)
        pb_set = set(pb_innovs)
        matching_genes = pa_set & pb_set
        disjoint_genes = pa_set ^ pb_set

        new_genome_connections = []

        new_genome = Genome(3,2)
        # for every matching innovation pick a random parent and pass on that
        # parents corresponding gene to the child
        for gene in matching_genes:
            if random.randint(0,1):
                new_genome.connection_genes.append(pa_innovs[gene].copy())
            else:
                new_genome.connection_genes.append(pb_innovs[gene].copy())

        # create the new genome and add the in- and outputs from a parent.


        # for every disjoint gene find out which parent it belongs to, and pass
        # it on
        logger.debug('passing disjoint genes')
        logger.debug('{}', disjoint_genes)
        for innov in disjoint_genes:
            logger.debug('\tchecking {}', innov)
            if innov in pa_innovs:
                gene = pa_innovs[innov]
                logger.debug('\t\tinnovation {} was in a', innov)
            elif innov in pb_innovs:
                logger.debug('\t\tinnovation {} was in b', innov)
                gene = pb_innovs[innov]
            else:
                continue

            if not new_genome.has_connection(gene.in_node, gene.out_node):
                new_genome.connection_genes.append(gene.copy())

        logger.debug('added all genes. new gene pool:{}',
                     [g.innovation for g in new_genome_connections])


        for con in new_genome.connection_genes:
            if not new_genome.has_node(con.in_node):
                new_genome.add_node('hidden')
            if not new_genome.has_node(con.out_node):
                new_genome.add_node('hidden')

        # new_genome.connection_genes = new_genome_connections
        logger.debug('{}', new_genome.connection_genes)
        return new_genome

    def assign_population_cap(self):
        # TODO: assign population caps based on shared fitness.
        # to do this first compile a list of adjusted fitness scores of all
        # species. normalize the list and assign each species a population cap
        # equal to the total population limit multiplied by their normalized
        # score.

        population_size = 50

        score_total = sum(sp.get_adjusted_fitness() for sp in self.species)
        for sp in self.species:
            norm = float(sp.get_adjusted_fitness_sum()/score_total)
            sp.population_limit = norm * population_size

        logger.debug('assigned population limits. total population: {}',
                     sum(sp.population_limit for sp in self.species))
       


    def evaluate_all_species(self):
        # TODO: evaluation should not be done per species but on the entire population.
        for sp in self.species:
            sp.evaluate_population(self.config['fitness_function'])
