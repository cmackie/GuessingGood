#!/bin/bash

for (( i=1; i<=32; i++ ))
do
    $1 &>/dev/null &
    sleep 2
done
