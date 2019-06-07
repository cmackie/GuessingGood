#!/usr/bin/env python3
""" Dataset management """

import sys
import os
import os.path
import random
import numpy as np


def instances(data, pre=''):
    return [
        data + '/' + os.path.basename(filename)
        for (filename, ext) in map(os.path.splitext, os.listdir(data + '/'))
        if ext == ".cnf" and filename.startswith(pre)
    ]


def partition(data, pre=''):
    """ Partition the dataset 90/10 into training and testing sets """
    ins = instances(data, pre)
    random.shuffle(ins)
    n = len(ins)
    k = int(0.9 * n)
    with open('datasets/' + pre + 'training.txt', 'w') as f:
        print(*ins[:k], sep='\n', file=f, flush=True)
    with open('datasets/' + pre + 'testing.txt', 'w') as f:
        print(*ins[k:], sep='\n', file=f, flush=True)


def load_dataset(instances, demean=False, true=1, false=0):
    """ Construct the input matrix X and output vector y

    The argument 'instances' should be a list of strings like 'samples/vmpc_30',
    so that appending '.cnf', '.sat', or '.feat' gives the full path to the
    expected file for the SAT instance. If the argument 'demean' is true, then
    the feature vectors should be demeaned within each individual SAT instance.
    """
    assign = np.vectorize(lambda l: true if l > 0 else false)
    X = np.empty((0,112))
    y = np.empty(0)
    for instance in instances:
        with open(instance + '.sat', 'r') as sat_file:
            if sat_file.readline().strip() != 'SAT':
                continue
            y0 = assign(np.loadtxt(sat_file, comments=[' 0'], dtype=int))
            y = np.concatenate([y, y0])

        with open(instance + '.feat', 'r') as feat_file:
            X0 = np.loadtxt(feat_file, comments=['VARIABLE'], skiprows=2)
            if demean:
                X0 = X0 - X0.mean(axis=0)
            X = np.concatenate([X, X0])
    return X, y


if __name__ == '__main__':
    partition('data', sys.argv[1])