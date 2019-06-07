#!/usr/bin/env python3

import os.path
import subprocess
import dataset

for instance in dataset.instances:
    features = instance + '.feat'
    if not os.path.exists(features):
        subprocess.call(
            ['preprocess/preprocess {}'.format(instance)],
            shell=True
        )
