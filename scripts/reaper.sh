#!/bin/bash

for pid in $(ps u | sed -n 's/^ec2-user[ ]*\([0-9]*\)[ ].*minumerate.*$/\1/p')
do
    if [[ -e /proc/$pid/ ]]
    then
        file=$(ls -l /proc/$pid/fd | sed -n 's/^.*\/GuessingGood\/\([\/a-zA-Z0-9_-\.]*\.sat\)$/\1/p')
        rm ${file%sat}*
    fi
done
killall python3 python minumerate
kill $pid
