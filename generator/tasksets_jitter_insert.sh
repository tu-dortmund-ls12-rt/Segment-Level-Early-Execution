#!/bin/bash
rmod='0 1 2'
smod='0 1 2'
jmod='0 1 2 3'
for rm in $rmod
do
  for sm in $smod
  do
    for jm in $jmod
    do
      python3 tasksets_generator.py -r $rm -s $sm -j $jm &
      sleep 1
    done
  done
done

