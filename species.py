#!/usr/bin/env python3
from loguru import logger

class Species:
    def __init__(self, queen_genome, sid):
       self.queen = queen_genome
       self.identity = sid
       self.population = []
       self.add_genome(self.queen)
       self.population_limit = 50
       self.population_fitness = 0

    def evaluate_population(self, fitness_function):
        """evaluate the entire population by passing each genome to a fitness
        function, assign fitness scores according to
        their performance, and calculate the entire spiecies average fitness.

        A fitness function is any function that takes a genome as an argument,
        evaluates it's performance, and returns a score.
        """

        total_score = 0
        for genome in self.population:
            score = fitness_function(genome)
            genome.fitness = score
        self.population_fitness = total_score / len(self.population)

    def add_genome(self, genome):
        self.population.append(genome)
        genome.species = self

    def remove_genome(self, genome):
        self.population.remove(genome)

    def get_compatibility_score(self, genome):
        """check a genome to find out if it's compatible with this spiecies"""

        # TODO: differentiate between disjoint and excess genes
        # currently all non-matching genes are considered disjoint and are
        # scored the same
       
        # compatibility coefficients.
        # TODO: pull compatibility coefficients from a configuration
        c1, c2, c3 = 1, 1, .5

        queen_innovs = {g.innovation:g for g in self.queen.connection_genes}
        comp_innovs = {g.innovation:g for g in genome.connection_genes}
        queen_set = set(queen_innovs)
        comp_set = set(comp_innovs)
        matching_genes = queen_set & comp_set
        disjoint_genes = queen_set ^ comp_set

        # TODO: find out why the fuck this piece of shit is not working.
        # it's outputting zero weight difference, even though there's definitely
        # matching innovations with different weight values.
        # i'm an actual retard. I was printing it as an integer, even though it
        # was correctly calculating the float value all along.
        # I'll keep this here just as a reminder.
        # fuckassdickshitcuntfuckteemo

        weight_diff = 0.0
        weight_diff = sum(
            [abs(queen_innovs[i].weight - comp_innovs[i].weight)
            for i in matching_genes], 0.0)

        score = len(disjoint_genes)*c1 + weight_diff*c3
        logger.debug('genome had {} matching genes and {} disjoint genes',
                     len(matching_genes),
                     len(disjoint_genes))

        logger.debug('difference in matching genes is {:.3f} and contributes {:.3f} to the total score',
                     weight_diff, weight_diff*c3)

        return score

    def get_adjusted_fitness_sum(self):
        return sum(genome.fitness / len(self.genomes) for genome in self.population)
