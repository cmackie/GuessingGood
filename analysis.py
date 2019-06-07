#!/usr/bin/env python3
""" Feature analysis of SAT instances """

import os
import os.path
import dataset
from sat import *

def analyze(instance):
    """ Perform feature analysis on a SAT instance """
    feat_file = open(instance + '.feat', 'w')
    sat = SAT(instance, solution=False)
    phi = sat.formula # the real formula
    small = [[cls for cls in phi if len(cls) == k] for k in range(1, 5)]
    horn = [cls for cls in phi if SAT.is_horn(cls)]
    antihorn = [cls for cls in phi if SAT.is_antihorn(cls)]
    subphi = small + [horn, antihorn, phi] # all subformulae of interest
    for phi in subphi:
        print(len(phi), end=' ', file=feat_file)
    print(file=feat_file)
    for var in range(1, sat.num_variables + 1):
        print('VARIABLE', var, file=feat_file)
        for lit in [var, -var]:
            for phi in subphi:
                relphi = [cls for cls in phi if lit in cls] # relevant clauses
                print(len(relphi), end=' ', file=feat_file)
                print(sum(map(lambda cls: 1 / len(cls), relphi)), end=' ', file=feat_file)
                print(max(map(len, relphi), default=0), end=' ', file=feat_file)
                print(min(map(len, relphi), default=0), end=' ', file=feat_file)
                print(sum([2 ** -len(cls) for cls in relphi]), end=' ', file=feat_file)
                sigphi = [sum(map(sign, cls)) for cls in relphi]
                print(sigphi.count(1), end=' ', file=feat_file)
                print(sigphi.count(-1), end=' ', file=feat_file)
        print(file=feat_file)
        feat_file.flush()
    feat_file.close()

for instance in dataset.instances:
    if not os.path.exists('dataset/' + instance + '.feat'):
        try:
            analyze('dataset/' + instance)
        except:
            os.remove('dataset/' + instance + '.feat')
