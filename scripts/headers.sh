#!/bin/bash

for cnf in data/*.cnf
do
    grep -m 1 -H -e '^p cnf' $cnf
done
