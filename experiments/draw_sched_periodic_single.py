from __future__ import division
import sys
import numpy as np
import matplotlib
import itertools
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter
from matplotlib import rcParams
import matplotlib.ticker as ticker

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Tahoma']

rcParams['ps.useafm'] = True
rcParams['pdf.use14corefonts'] = True
rcParams['text.usetex'] = True

figlabel=['a','b','c','d','e','f','g','h','i','j']

#'o', 'v','+' ,'x','*'
#marker = ['o', 'v','+','*','D','x','+','p']
#'b','r','g','k','y'
#colors = ['b','r','k','g','c','y','m','b']
marker = itertools.cycle (('D', 'o', 'v', 'D', 'o', 'v', 's',))
#marker = ['o', '+','*','D','x','+','p',]
#'b','r','g','k','y'
#colors = ['b','r','k','g','c','y','m','b']
colors = itertools.cycle (('blue','orange','green','red','purple','brown','black','gray',))
#colors = ['c','k','b','r','g','y','m','b']
#line = ['--','--','--','--','--','--','-','-','-','-','-','-']
#line = [':',':',':',':',':',':','-','-','-','-','-','-']
line = itertools.cycle (('-','-',))

interval = ['sslen: Short', 'sslen: Moderate', 'sslen: Long']


fig=plt.figure()

## create a virtual outer subsplot for putting big x-ylabel
ax=fig.add_subplot(111)
fig.subplots_adjust(top=0.8,bottom=0.35,left=0.25,right=0.85,hspace =0.2,wspace=0.16)

ax.set_xlabel(r'Utilization (\%) / M',labelpad=25.0,size=28)
ax.set_ylabel('Acceptance Ratio (\%)',labelpad=25.0,size=28)
ax.spines['top'].set_color('none')
ax.spines['bottom'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['right'].set_color('none')

ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')

# initialize the input configuration
ntasks = 10
msets = 100
processors = 1
rmod = 2
smod = 0

x1 = []
x2 = []
x3 = []
x4 = []
x5 = []
x6 = []
x7 = []
x8 = []
x9 = []
for i in range(5, 101, 5):
    x1.append(i)
    x2.append(i)
    x3.append(i)
    x4.append(i)
    x5.append(i)
    x6.append(i)
    x7.append(i)
    x8.append(i)
    x9.append(i)

for i in range(1, 2):

    # ax = fig.add_subplot(3, 3, i)
    ax = fig.add_subplot(1, 1, i)

    if (i == 1):
        rmod = 2
        smod = 0

    if (i == 2):
        rmod = 0
        smod = 1

    if (i == 3):
        rmod = 0
        smod = 2

    if (i == 4):
        rmod = 1
        smod = 0

    if (i == 5):
        rmod = 1
        smod = 1

    if (i == 6):
        rmod = 1
        smod = 2

    if (i == 7):
        rmod = 2
        smod = 0

    if (i == 8):
        rmod = 2
        smod = 1

    if (i == 9):
        rmod = 2
        smod = 2



    sched_name_ss = './outputs/results_sched_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(
        processors) + '_r' + str(rmod) + '_s' + str(smod) + '.npy'
    results_sim = np.load(sched_name_ss)

    EDAGMF_OPA_name = './outputs/EDAGMF-OPA10_r' + str(rmod) + '_s' + str(smod) + '.npy'
    results_SCAIR_OPA = np.load(EDAGMF_OPA_name)

    sched_comb_name_ss = './outputs/results_combined_sched_n' + str(ntasks) + '_m' + str(msets) + '_p' + str(
        processors) + '_r' + str(rmod) + '_s' + str(smod) + '.npy'
    results_sim_comb = np.load(sched_comb_name_ss)

    EDAGMF_OPA_detail_name = './outputs/edagmf_opa_results_r' + str(rmod) + '_s' + str(smod) + '.npy'
    results_EDAGMF_OPA_detail = np.load(EDAGMF_OPA_detail_name)


    y1 = []

    y2 = []

    y3 = []

    y4 = []


    for j in range (len(results_sim)-1):

        y1.append(int(results_sim[j][0]))
        y2.append(int(results_sim[j][1]))
        y3.append(int(results_SCAIR_OPA[1][j]*100))
        temp = []
        for ttt in range(100):
            temp.append(max(results_sim_comb[j][0][ttt], results_EDAGMF_OPA_detail[j][ttt]))
        y4.append(sum(temp))

    y1.append(0)
    y2.append(0)
    y3.append(0)
    y4.append(0)
    #y1.append(0)

    ax.axis([3,103,-5,105])
    major_ticks = np.arange(5, 103, 10)
    minor_ticks = np.arange(5, 103, 5)
    ax.plot(x1, y1, color='red', label='SIM-EDF', linewidth=2.0, marker='D', markersize=18, markevery=1, fillstyle='none')
    ax.plot(x2, y2, color='red', label='SIM-RM', linewidth=2.0, marker='o', markersize=18, markevery=1, fillstyle='none')
    #ax.plot(x3, y3, color='green', label='SIM-EDF-OB', linewidth=2.0, marker='X', markersize=12, markevery=1, fillstyle='none')
    #ax.plot(x4, y4, color='green', label='SIM-RM-OB', linewidth=2.0, marker='H', markersize=12, markevery=1, fillstyle='none')

    ax.plot(x3, y3, color='maroon', label='EDAGMF-OPA', linewidth=2.0, marker='p', markersize=18, markevery=1, fillstyle='none')
    ax.plot(x4, y4, color='blue', label='COMB-ALL', linewidth=2.0, marker='s', markersize=18, markevery=1, fillstyle='none')
    #ax.plot(x6, y6, color='blue', label='SCAIR-RM', linewidth=2.0, marker='s', markersize=12, markevery=1, fillstyle='none')

    #ax.plot(x7, y7, color='orange', label='SCEDF', linewidth=2.0, marker='v', markersize=12, markevery=1,fillstyle='none')
    #ax.plot(x8, y8, color='orange', label='SCRM', linewidth=2.0, marker='s', markersize=12, markevery=5, fillstyle='none')
    #ax.plot(x9, y9, color='maroon', label='EDAGMF-OPA', linewidth=2.0, marker='p', markersize=12, markevery=1, fillstyle='none')


    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    if (i == 1):
        ax.legend(bbox_to_anchor=(0.5, 1.15),
            loc=10,
            ncol=4,
            markerscale =1.5,
            borderaxespad=0.,
            prop={'size':25})
    if (smod == 0):
        sus_num = 'Rare'
    elif (smod == 1):
        sus_num = 'Moderate'
    else:
        sus_num = 'Frequent'

    if (rmod == 0):
        sus_len = 'Short'
    elif (rmod == 1):
        sus_len = 'Medium'
    else:
        sus_len = 'Long'

    # ax.set_title('('+ figlabel[i-1]+') '+ sus_len + ', ' + sus_num,size=25, y=1.02)
    #if (i == 1):
    #    ax.set_title(r'\ \ \ \ \ \ (a)-(b) ' + r'\textbf{Number~of~Cores}' + '\n'+ '('+ figlabel[i-1]+') m='+ str(processors) + ' r=' + str(res_num) +' '+r'$\alpha$='+iaccessU,size=25, y=1.02, ha='center')
    #if (i == 3):
    #    ax.set_title(r'\ \ \ \ \ \ (c)-(d) ' + r'\textbf{Number of Resources}' + '\n'+ '('+ figlabel[i-1]+') m='+ str(processors) + ' r=' + str(res_num) +' '+r'$\alpha$='+iaccessU,size=25, y=1.02)
    #if (i == 5):
    #    ax.set_title(r'\ \ \ \ \ \ (e)-(f) ' + r'\textbf{Ratio of Shared Resources}' + '\n'+ '('+ figlabel[i-1]+') m='+ str(processors) + ' r=' + str(res_num) +' '+r'$\alpha$='+iaccessU,size=25, y=1.02)
    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.grid(which='both')
    ax.set_aspect(0.38)

plt.show()
sys.exit()
