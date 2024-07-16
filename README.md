# Segment-Level-Early-Execution

Generation process:
- ``` generator/tasksets_generate.sh ```
- ``` generator/job_convertor.sh ``` (Mabye also need to use ``` generator/convert_to_csv.py ``` in addition)

Run experiments:
- ``` experiments/sched_all.sh ```
- Use SSSEvaluation framework ( https://github.com/tu-dortmund-ls12-rt/SSSEvaluation )

Plot:
- ``` experiments/draw_sched_periodic_9.py ``` or ``` draw_sched_periodic_single.py ```
