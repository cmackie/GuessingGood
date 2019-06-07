#!/usr/bin/env python3
""" Logistic regression for prediction of satisfying assignments """

import sys
import numpy as np
from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.datasets import mnist
from keras.utils import np_utils
import dataset


n_feature = 112


def load_dataset(instances, demean=False, true=1, false=0):
    """ Construct the input matrix X and output vector y

    The argument 'instances' should be a list of strings like 'samples/vmpc_30',
    so that appending '.cnf', '.sat', or '.feat' gives the full path to the
    expected file for the SAT instance. If the argument 'demean' is true, then
    the feature vectors should be demeaned within each individual SAT instance.
    """
    assign = np.vectorize(lambda l: true if l > 0 else false)
    X = np.empty((0,n_feature))
    y = np.empty(0)
    for instance in instances:
        with open(instance + '.sat', 'r') as sat_file:
            y0 = assign(np.loadtxt(sat_file, comments=[' 0'], dtype=int))
            if y0.ndim > 1:
                y0 = y0[np.random.choice(y0.shape[0], 1, replace=False), :]
                y0 = y0.flatten()
            y = np.concatenate([y, y0])

        with open(instance + '.feat', 'r') as feat_file:
            X0 = np.loadtxt(feat_file, comments=['VARIABLE'], skiprows=2)
            if demean:
                X0 = X0 - X0.mean(axis=0)
            X = np.concatenate([X, X0])
    return X, y


def reg(w):
    return 0.001 * K.sum(K.square(w))


def build_logistic_model(dim):
    model = Sequential()
    model.add(Dense(dim, input_dim=dim, activation='sigmoid', kernel_regularizer=reg))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    model.summary()
    model.compile(optimizer='sgd', loss='binary_crossentropy', metrics=['binary_accuracy'])
    return model


def experiment(train, test):
    batch_size = 64
    epochs = 2
    dim = 112

    X_train, Y_train = load_dataset(train, demean=True, true=1, false=0)
    X_test, Y_test = load_dataset(test, demean=True, true=1, false=0)

    model = build_logistic_model(dim)

    # compile the model
    history = model.fit(X_train, Y_train,
                        batch_size=batch_size, epochs=epochs,
                        verbose=1)
    score = model.evaluate(X_test, Y_test, verbose=0)

    print('Test score:', score[0])
    print('Test accuracy:', score[1])

    # save model as json and yaml
    json_string = model.to_json()
    open('variable_based.json', 'w').write(json_string)
    yaml_string = model.to_yaml()
    open('variable_based.yaml', 'w').write(yaml_string)

    # save the weights in h5 format
    model.save_weights('variable_based.h5')


if __name__ == '__main__':
    pre = sys.argv[1]
    train = open('datasets/' + pre + 'training.txt', 'r').read().split('\n')[:-1]
    test = open('datasets/' + pre + 'testing.txt', 'r').read().split('\n')[:-1]
    experiment(train, test)
