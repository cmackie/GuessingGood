#!/usr/bin/env python3
""" Logistic regression for prediction of satisfying assignments """

import sys
import numpy as np
from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM
from keras.datasets import mnist
from keras.utils import np_utils
import dataset


n_variable = 1000
n_clause = 5000


def parse_formula(cnf_file, n=-1):
    comments = []
    formula = []
    num_variables = n_variable
    for line in open(cnf_file):
        if line.startswith('c'):
            comments.append(line[2:])
        elif line.startswith('p '):
            p, cnf, nv, nc = line.split()
            num_variables = int(nv)
            num_clauses = int(nc)
            assert p == "p" and cnf == "cnf"
            assert 0 < num_variables <= n_variable and 0 < num_clauses <= n_clause
        elif not line.startswith('Solved'):  # formula clause
            if len(formula) == n:
                return np.array(formula)
            c = list(map(int, line.split()))
            assert c.pop() == 0
            c = sorted(c, key=abs)
            clause = []
            v = 1
            for lit in c:
                var = abs(lit)
                assert v <= var <= num_variables
                for _ in range(v, var):
                    clause.append(0)
                    v += 1
                clause.append(-1 if lit < 0 else 1)
                v += 1
            for _ in range(v, n_variable + 1):
                clause.append(0)
                v += 1
            assert v == n_variable + 1
            formula.append(clause)
    return np.array(formula)


def load_dataset(instances, true=1, false=0):
    """ Construct the input matrix X and output vector y

    The argument 'instances' should be a list of strings like 'samples/vmpc_30',
    so that appending '.cnf', '.sat', or '.feat' gives the full path to the
    expected file for the SAT instance.
    """
    assign = np.vectorize(lambda l: true if l > 0 else false)
    X = []
    y = np.empty((0, n_variable))
    for instance in instances:
        cnf_file = instance + '.cnf'
        try:
            Xc = parse_formula(cnf_file)
        except AssertionError:
            print(cnf_file, 'malformed')
            continue
        log_file = instance + '.log'
        try:
            Xl = parse_formula(log_file, n_clause - Xc.shape[0])
        except AssertionError:
            print(log_file, 'malformed')
            continue

        with open(instance + '.sat', 'r') as sat_file:
            y0 = assign(np.loadtxt(sat_file, comments=[' 0'], dtype=int))
            if y0.ndim > 1:
                y0 = y0[np.random.choice(y0.shape[0], 1, replace=False), :]
                y0 = y0.flatten()
            if y0.size < n_variable:
                y0 = np.concatenate([y0, np.zeros(n_variable - y0.size)])
            y0 = y0.reshape((1, n_variable))
            y = np.concatenate([y, y0])

        X0 = np.empty((0, n_variable))
        X0 = np.concatenate([X0, Xc])
        X0 = np.concatenate([X0, Xl])
        if X0.shape[0] < n_clause:
            X0 = np.concatenate([np.zeros((n_clause - X0.shape[0], n_variable)), X0])
        X.append(X0)
    return np.array(X), y


def build_lstm_model():
    model = Sequential()
    model.add(LSTM(n_variable, input_shape=(n_clause, n_variable), activation='sigmoid', dropout=0.3, recurrent_dropout=0.25))

    model.summary()
    model.compile(loss='binary_crossentropy', optimizer='sgd', metrics=['binary_accuracy'])
    return model


def experiment(train, test):
    batch_size = 64
    epochs = 2

    X_train, Y_train = load_dataset(train, true=1, false=-1)
    X_test, Y_test = load_dataset(test, true=1, false=-1)

    model = build_lstm_model()

    # compile the model
    history = model.fit(X_train, Y_train,
                        batch_size=batch_size, epochs=epochs,
                        verbose=1)
    score = model.evaluate(X_test, Y_test, verbose=0)

    print('Test score:', score[0])
    print('Test accuracy:', score[1])

    # save model as json and yaml
    json_string = model.to_json()
    open('clause_based.json', 'w').write(json_string)
    yaml_string = model.to_yaml()
    open('clause_based.yaml', 'w').write(yaml_string)

    # save the weights in h5 format
    model.save_weights('clause_based.h5')


if __name__ == '__main__':
    pre = sys.argv[1]
    train = open('datasets/' + pre + 'training.txt', 'r').read().split('\n')[:-1]
    test = open('datasets/' + pre + 'testing.txt', 'r').read().split('\n')[:-1]
    experiment(train, test)
