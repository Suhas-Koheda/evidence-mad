import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from pathlib import Path

OUT=Path('/home/ssp/projects/Python/MAD-2/final_results_openrouter_uniform_v2/matched_96_analysis')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.2,'text.color':'black'})
fig,ax=plt.subplots(figsize=(7.16,3.75))
fig.patch.set_facecolor('white'); ax.set_facecolor('white')
ax.set_xlim(0,7.16); ax.set_ylim(0,3.75); ax.axis('off')

def rect(cx,cy,w,h,title,detail=None,ts=8.4,ds=7.2):
    ax.add_patch(FancyBboxPatch((cx-w/2,cy-h/2),w,h,boxstyle='square,pad=0.025',facecolor='white',edgecolor='black',linewidth=.75))
    if detail:
        ax.text(cx,cy+.105,title,ha='center',va='center',fontsize=ts,fontweight='bold',color='black')
        ax.text(cx,cy-.105,detail,ha='center',va='center',fontsize=ds,color='black',linespacing=1.15)
    else:
        ax.text(cx,cy,title,ha='center',va='center',fontsize=ts,color='black')

def arrow(a,b):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=8,linewidth=.72,color='black',shrinkA=0,shrinkB=0))

# Straight pipeline; labels name the operations rather than implementation files.
y=3.12
stages=[
    (.48,.76,'Query',None),
    (1.70,1.12,'Router','Select agents'),
    (3.18,1.40,'Parallel agents','Web | Reference\nScholarly'),
    (4.88,1.22,'Normalize','Filter evidence'),
    (6.48,1.17,'NLI gate','Pairwise NLI\n4 evidence states')
]
for x,w,t,d in stages: rect(x,y,w,.64,t,d)
for left,right in zip(stages,stages[1:]):
    arrow((left[0]+left[1]/2+.035,y),(right[0]-right[1]/2-.055,y))

# The evidence state fans out into three response paths.
branch_y=2.48
arrow((6.48,y-.34),(6.48,branch_y))
centers=[1.13,3.58,6.03]
ax.plot([centers[0],6.48],[branch_y,branch_y],color='black',linewidth=.72)
ax.add_patch(Circle((6.48,branch_y),.025,color='black'))
items=[
    ('AGREEMENT','Synthesize\ncompatible claims'),
    ('UNCERTAIN / INSUFFICIENT','Qualify answer;\nstate evidence gap'),
    ('DISAGREEMENT','Classify type; debate\nPropose / critique / revise\nJudge against evidence')
]
box_y=1.59; box_h=1.02; box_w=2.02
for x,(title,detail) in zip(centers,items):
    arrow((x,branch_y),(x,box_y+box_h/2+.025))
    rect(x,box_y,box_w,box_h,title,detail,ts=7.8,ds=7.0)

# The three paths join only after their response has been resolved or qualified.
merge_y=.73
for x in centers:
    ax.plot([x,x],[box_y-box_h/2-.025,merge_y],color='black',linewidth=.72)
ax.plot([centers[0],centers[-1]],[merge_y,merge_y],color='black',linewidth=.72)
ax.add_patch(Circle((centers[1],merge_y),.025,color='black'))
rect(centers[1],.33,2.5,.40,'Final response and trace',ts=8.0)
arrow((centers[1],merge_y),(centers[1],.33+.20+.015))

plt.subplots_adjust(left=.015,right=.985,top=.985,bottom=.025)
fig.savefig(OUT/'architecture/evidence_mad_architecture.png',dpi=400,facecolor='white',bbox_inches='tight',pad_inches=.035)
fig.savefig(OUT/'architecture/evidence_mad_architecture.pdf',facecolor='white',bbox_inches='tight',pad_inches=.035)
plt.close(fig)
