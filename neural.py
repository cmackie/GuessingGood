#!/usr/bin/env python3
""" Neural network for prediction of satisfying assignments """

import os
import os.path
import dataset
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation

# TODO: Try 'sigmoid', and 'softmax'
model = Sequential([
    Dense(98, activation='tanh', input_dim=98),
    Dropout(0.5),
    Dense(128, activation='tanh'),
    Dropout(0.5),
    Dense(64, activation='tanh'),
    Dropout(0.5),
    Dense(32, activation='tanh'),
    Dropout(0.5),
    Dense(16, activation='tanh'),
    Dropout(0.5),
    Dense(8, activation='tanh'),
    Dropout(0.5),
    Dense(1, activation='tanh'),
])
model.compile(optimizer='rmsprop', # TODO: Try 'sgd', 'adagrad', 'adadelta'
              loss='binary_crossentropy',
              metrics=['accuracy'])

inputs, outputs = load_dataset(
    ['samples/partial-5-13-s', 'samples/vmpc_30'],
    demean=True,
    false=-1
)

model.fit(inputs, outputs, epochs=16, batch_size=32)
