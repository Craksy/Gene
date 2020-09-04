#!/usr/bin/env python3

from genome import Genome
from species import Species
from logger import logger
from typing import List

class Gene:
    def __init__(self, configuration):
        # self.config = configuration
        # TODO: actually implement this, instead of this duct tape solution.
        self.config = dict(
            fitness_function = lambda g: ...,
            compatibility_threshold = .2
        )
        self._next_id = 0
        self.species:List[Species] = []
        logger.debug('initializing Gene')

    def get_next_species_id(self):
        self._next_id += 1
        return self._next_id

    def init_population(self):
        logger.debug('creating initial population')
        first_queen = Genome(3,2)
        initial_species = self.add_new_species(first_queen)
        while len(initial_species.population) < initial_species.population_limit:
            new_genome = initial_species.queen.clone()
            new_genome.mutate()
            initial_species.population.append(new_genome)

    def add_new_species(self, queen):
        logger.debug('adding new species from queen genome %s', queen)
        new_species = Species(queen, self.get_next_species_id())
        self.species.append(new_species)
        return new_species

    def speciate_population(self):
        # compile a list of all genomes from all species. this is done to avoid
        # modifying the length of an iterator as we're looping through it

        logger.debug('speciating')
        logger.debug('compiling population list')
        population = []
        for sp in self.species:
            for genome in sp.population:
                population.append(genome)
        comp_threshold = 5

        # TODO: add some logging to this function.
        # it's gonna be a bitch to debug otherwise
        for genome in population:
            logger.debug('checking genome %s', genome)
            compatible = False
            for sp in self.species:
                if genome.species.identity == sp.identity:
                    continue
                if sp.get_compatibility_score(genome) < comp_threshold:
                    # if genome already belongs to a species remove it from that
                    # species
                    if genome.specees:
                        genome.species.remove_genome(genome)
                    sp.add_genome(genome)
                    compatible = True
                    break
            if compatible:
                continue

            self.add_new_species(genome)


    def evaluate_all_species(self):
        for sp in self.species:
            sp.evaluate_population(self.config['fitness_function'])
