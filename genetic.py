import random
import argparse
from LZ77 import Compressor
import bitarray
from midi_strings import *
import string #for getting list of ascii characters for alphabet

#TODO:
#[ ] add functionality for multiple target strings, ie a guide set
#		will just need to modify the fitness function, to sum the guide set distances
#
#

#class to genetrate a list that resembles target using a genetic algorithm
#with Nomralized Compression Distance as the Fitness function
#Individuals are represented as chromosomes where their genes are a string and the fitness of that 
#individual is the NCD calcualted for the string as shown below
#
#initalization parameters:
    #target = list of items that the algorithm will attempt to replicate
    #gene_set = list comprised of all the possible items in the alphabet for target
    #generation size = int for number of individuals in a generation
    #n_reporduce = int for the number fo individuals in a generation that will reporduce, (determined by highest fitness)
    #mutaion_rate = float for the rate at which individual mutations in the gene strings are introduced into the offspring
    #corssover_rate = float for the percentage of parent1 chromosome that is taken in the child,
    #    a value of 1, means all of parent 1 is taken, a value of 0.5 means the chromosome is crossed over halfway
class Generator():
    def __init__(self, target, gene_set, generation_size = 30, n_reproduce = 2, mutation_rate = 0.9, crossover_rate = 0.5, iterations = 30, verbose=False):
        global verbose_print
        verbose_print = print if verbose else lambda *a, **k: None

        self.target = target
        self.target_string = ''.join(target)
        self.gene_set = gene_set
        self.generation_size = generation_size
        self.n_reproduce = n_reproduce
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.iterations = iterations

        #the generation is initalized to an empty array
        #self.generation = []

    #begin genetic algorithm
    def run(self):

        #first create generation_size random chromosomes and populate in the generation array
        self.generation = [chromosome(genes = self._random_gene(), target=self.target) for x in range(self.generation_size)]

        for i in range(self.iterations):
            #sort this generation by individual fitness
            self.generation.sort(key = lambda x: x.fitness, reverse=True)

            #restrict the generation to the n_reproduce strongest individuals as parents
            parents = self.generation[:self.n_reproduce]

            #crossover the parents to create children at the given crossover rate
            children = [chromosome(genes = self._crossover(parents), target=self.target) for x in range(self.generation_size - len(parents))]

            #mutate the children according to the mutation rate
            children = self._mutate(children)

            #concatenate lists of parents and children to form final generation, then repeate on the this generation
            self.generation = parents + children

            verbose_print("Generation:", i)
            for x in self.generation:
                verbose_print("\tgenes:",x.genes, " fitness:", x.fitness)

        #return the fittest individual
        return self.generation[0].genes


    #helper function to return a radom gene
    def _random_gene(self):
        return random.choices(self.gene_set, k = len(self.target))

    #returns a new gene from random parents selected from gene_pool
    def _crossover(self, gene_pool):
        parent1 = random.choice(gene_pool)
        parent2 = random.choice(gene_pool)

        crossover_point = int(round(self.crossover_rate * len(self.target)))

        #concatenate parent genes at crossover point
        new_gene = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]

        return new_gene

    #mutation function which flips one note to a random other note, at the given mutation rate
    #note this function is applied to the entire generation simultaneousl
    def _mutate(self, gene_pool):
        for child in gene_pool:
            if random.randint(0,99) < (self.mutation_rate * 100):
                child.genes[random.randint(0,len(child.genes)-1)] = random.choice(self.gene_set)
                #if there is a mutation we need to recalculate fitness
                child.set_fitness(child.compute_fitness())

        return gene_pool



#this class represents a chromosome(individual) of the population. An individual is merely its genes, which is a list of strings,
#and its fitness as described below. The individual also holds its target whcih is needed for calcualting fitness
#
#Iitialization Parameters:
#	genes: the list of strings
#	target: the list of strings it is targeting to compute fitness
#	fitness: optionally a predetermined fitness can be given, but this is not used in the above algorithm
class chromosome():
	#note chromosome needs to know the target, in order to calculate its fitness
    def __init__(self, genes, target, fitness = 0,):
        self.genes = genes
        self.target = target
        self.target_string = ''.join(target)
        self.fitness = self.compute_fitness()

    #The function to Compute fitness for each individual. It is called upon initailation of a chromosome.
    #The function compares the "differnece" between its current gene (string) and the target gene (string)
    #The Normalized Information Distance is used with the LZ77 compression algorithm
    #Please see the comments below for more details
    def compute_fitness(self):
        #compute using NCD

        #convert list of whatever to a bit array for passing to the compressor
        gene_string = ''.join(self.genes)
        #print(gene_string)
        gene_bit_array = bitarray.bitarray()
        gene_bit_array.frombytes(gene_string.encode('utf-8'))
        
        compressor = Compressor()
       

        C_x_y = len(compressor.compress(gene_string+self.target_string))
        C_x = len(compressor.compress(gene_string))
        C_y_x = len(compressor.compress(self.target_string+gene_string))
        C_y = len(compressor.compress(self.target_string))

        verbose_print("length of data:", len(gene_string), " length of compression: ", C_x)

        #compute normalized compression distance as given in https://ieeexplore.ieee.org/document/4424858/
        #ncd is between 0 and 1, values closer to 0 indicate similarity to the target, distances near 1 indicate dissimilarity
        ncd = (max((C_x_y - C_x),(C_y_x - C_y)))/(max(C_x,C_y))

        #we invert ncd so that values closer to zero are given a higher fitness value
        fitness = 1/ncd

        verbose_print("Nomralized Compression Distance:", ncd, "fitness:, ", fitness)

        return fitness


    def set_fitness(self, new_fitness):
        self.fitness = new_fitness







