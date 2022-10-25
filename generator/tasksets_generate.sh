#!/bin/bash
rmod='0 1 2'
smod='0 1 2'
for rm in $rmod
do
  for sm in $smod
  do
    python3 tasksets_generator.py -r $rm -s $sm &
    sleep 1
  done
done

