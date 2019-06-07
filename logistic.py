#!/usr/bin/env python3
""" Logistic regression for prediction of satisfying assignments """

import os
import os.path
from dataset import load_dataset
import tensorflow as tf

features = []
for sign in ["x", "-x"]:
    for phi in ["phi_1", "phi_2", "phi_3", "phi_4", "phi_horn", "phi_cohorn", "phi"]:
        features += [
            'num({}, {})'.format(sign, phi),
            'avg({}, {})'.format(sign, phi),
            'max({}, {})'.format(sign, phi),
            'min({}, {})'.format(sign, phi),
            'jw({}, {})'.format(sign, phi),
            'neg({}, {})'.format(sign, phi),
            #'neut({}, {})'.format(sign, phi),
            'pos({}, {})'.format(sign, phi),
        ]

inputs, outputs = load_dataset(['samples/vmpc_30'], demean=True)
inputs = dict(zip(features, inputs.T.tolist())) # This is kinda bullshit

def iterator(randomize):
    dataset = tf.data.Dataset.from_tensor_slices((inputs, outputs))
    if randomize:
        dataset = dataset.shuffle(1024).batch(16).repeat(2)
    return dataset.make_one_shot_iterator()

model = tf.estimator.LinearClassifier(
    model_dir='models/',
    feature_columns=map(tf.feature_column.numeric_column, features),
    optimizer=tf.train.FtrlOptimizer(
        learning_rate=0.1,
        l1_regularization_strength=0.1,
        #l2_regularization_strength=1.0,
    ),
)
model.train(input_fn=iterator(True).get_next)

results = model.evaluate(input_fn=iterator(False).get_next)
print("PREDICT\tACTUAL")
for point in results:
    print("%s\t%s".format(results[point], outputs[point]))
