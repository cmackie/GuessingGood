#!/usr/bin/env python3
""" Manipulation of CNF formulae and satisfying assignments """

import os.path
import subprocess

def sign(x):
    return 0 if x == 0 else int(x / abs(x))

class FormatError(IOError):
    """ Failure to parse a CNF/SAT file """
    def __init__(self, message):
        super().__init__(message)

class SAT(object):
    """ A (CNF) formula and a satisfying assignment for a SAT problem """

    def __read_formula(self, cnf_file):
        self.comments = []
        self.formula = []
        self.width = 0
        try:
            for line in open(cnf_file):
                if line.startswith('c '):
                    self.comments.append(line[2:])
                elif line.startswith('p '):
                    p, cnf, nv, nc = line.split()
                    self.num_variables = int(nv)
                    self.num_clauses = int(nc)
                    assert p == "p" and cnf == "cnf"
                    assert self.num_variables > 0 and self.num_clauses > 0
                else: # formula clause
                    clause = list(map(int, line.split()))
                    assert clause.pop() == 0
                    for literal in clause:
                        assert abs(literal) <= self.num_variables
                    self.width = max(self.width, len(clause))
                    self.formula.append(clause)
        except:
            raise FormatError("Invalid CNF file")

    def __read_solution(self, sat_file):
        self.solution = {}
        file = open(sat_file)
        try:
            result = file.readline()
            if result == 'UNSAT\n' or result == 'INDET\n':
                self.solution = None
                return
            assert result == 'SAT\n'
            assignment = [int(lit) for lit in file.readline().split()]
            assert assignment.pop() == 0
            for literal in assignment:
                self.solution[abs(literal)] = sign(literal)
        except:
            raise FormatError("Invalid SAT file")

    def __init__(self, instance,
                 command='source ~/.bashrc\nminisat {} {}',
                 solution=True):
        """ Process a formula from a file in DIMACS CNF format """
        cnf_file = instance + '.cnf'
        sat_file = instance + '.sat'
        self.__read_formula(cnf_file)
        if solution:
            if not os.path.exists(sat_file):
                subprocess.call([command.format(cnf_file, sat_file)], shell=True)
            self.__read_solution(sat_file)

    @staticmethod
    def is_horn(clause):
        return len([lit for lit in clause if lit > 0]) <= 1

    @staticmethod
    def is_antihorn(clause):
        return len([lit for lit in clause if lit < 0]) <= 1
