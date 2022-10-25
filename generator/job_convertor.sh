#!/bin/bash
#!/bin/bash
rmod='0 1 2'
smod='0 1 2'
for rm in $rmod
do
  for sm in $smod
  do
    python3 convert_to_jobs.py -r $rm -s $sm &
    sleep 1
  done
done
