#!/usr/bin/env python3

import os.path
import subprocess
import dataset

for instance in dataset.instances:
    command = 'minumerate -cpu-lim=1200 {0}.cnf {0}.sat {0}.log'.format(instance)
    if not os.path.exists(instance + '.sat'):
        print(command)
        subprocess.call(['source ~/.bashrc\n' + command], shell=True)
