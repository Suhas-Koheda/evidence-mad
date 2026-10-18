import json, shutil, pathlib, collections, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

src=pathlib.Path('/home/ssp/projects/Python/MAD-2/final_results_openrouter_uniform_v2')
out=src/'matched_96_analysis'
question_ids={x['id'] for x in json.loads((src/'common_questions.json').read_text())}
systems=['single_llm','standard_mad','proposed_mad','no_gate','no_typed_strategy','no_relevance_filter']
labels=['Single LLM','Standard MAD','Evidence-MAD','No gate','No typed strategy','No relevance filter']
out.mkdir(exist_ok=True)
for child in ('traces','plots'):
    shutil.rmtree(out/child, ignore_errors=True)
# All analyses are computed from the 96 matched trace JSONs. Preserve input traces.
rows={}
for sys in systems:
    d=out/'traces'/sys; d.mkdir(parents=True)
    fs=sorted((src/sys).glob('qacc_test_*.json'))
    fs=[f for f in fs if f.stem in question_ids]
    if len(fs)!=96: raise RuntimeError(f'{sys}: expected 96 matched traces, got {len(fs)}')
    traces=[]
    for f in fs:
        shutil.copy2(f,d/f.name)
        traces.append(json.loads(f.read_text()))
    rows[sys]=traces

def evidence_state(t):
    e=t.get('evidence_decision') or {}
    return e.get('state') or 'not_recorded'
def role_counts(t):
    # call counters are nested in trace metrics; return successful and failed counts when present.
    m=t.get('metrics') or {}
    ok=m.get('total_llm_calls_ok', m.get('llm_calls_ok', m.get('llm_calls_successful',0))) or 0
    fail=m.get('total_llm_calls_failed', m.get('llm_calls_failed',0)) or 0
    return ok,fail
summary={}
for sys,ts in rows.items():
    states=collections.Counter(evidence_state(t) for t in ts)
    lat=[float((t.get('metrics') or {}).get('latency_seconds') or t.get('evaluation_seconds') or 0) for t in ts]
    calls=[role_counts(t) for t in ts]
    statuses=collections.Counter(t.get('evaluation_status','missing') for t in ts)
    models=collections.Counter(((t.get('evaluation_signature') or {}).get('opencode_model') or 'not_recorded') for t in ts)
    debates=sum(bool(t.get('debate_triggered')) for t in ts)
    outcomes=collections.Counter(((t.get('debate_outcome') or {}).get('status') or 'not_triggered') if t.get('debate_triggered') else 'not_triggered' for t in ts)
    agents=[int((t.get('metrics') or {}).get('usable_agents', len([a for a in (t.get('agent_evidence') or []) if a.get('status')=='ok']))) for t in ts]
    claims=[sum(len(a.get('claims') or []) for a in (t.get('agent_evidence') or [])) for t in ts]
    summary[sys]={
      'n':len(ts),'evaluation_status':dict(statuses),'opencode_model_signature_counts':dict(models),'debate_triggered':debates,'debate_rate':debates/len(ts),'debate_outcome_counts':dict(outcomes),
      'evidence_state_counts':dict(states),'latency_seconds':{'median':float(np.median(lat)),'p95':float(np.percentile(lat,95)),'mean':float(np.mean(lat))},
      'successful_calls_per_question_mean':float(np.mean([x for x,y in calls])),
      'failed_calls_per_question_mean':float(np.mean([y for x,y in calls])),
      'usable_retrieval_agents_per_question_mean':float(np.mean(agents)),
      'retrieved_claims_per_question_mean':float(np.mean(claims)),
      'key_fact_accuracy':'not scored in these traces; no gold labels available'
    }
(out/'trace_derived_summary.json').write_text(json.dumps(summary,indent=2)+'\n')

# Consistent neutral publication style: white canvas, black typography, color only for data.
plt.rcParams.update({'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white','text.color':'black','axes.labelcolor':'black','xtick.color':'black','ytick.color':'black','axes.edgecolor':'black','font.family':'DejaVu Sans','font.size':10})
colors=['#4C78A8','#F58518','#54A24B','#E45756','#72B7B2','#B279A2']
def save(name):
    plt.tight_layout(); plt.savefig(out/'plots'/f'{name}.png',dpi=220,bbox_inches='tight'); plt.savefig(out/'plots'/f'{name}.pdf',bbox_inches='tight'); plt.close()
(out/'plots').mkdir()
x=np.arange(len(systems)); short=['Single LLM','Standard','Evidence-MAD','No gate','No typed','No relevance']
# Debate frequency
vals=[summary[s]['debate_rate']*100 for s in systems]
plt.figure(figsize=(10,4.8)); bars=plt.bar(x,vals,color=colors,edgecolor='black',linewidth=.5)
plt.xticks(x,short,rotation=20,ha='right'); plt.ylabel('Traces with debate triggered (%)'); plt.ylim(0,max(vals)*1.25+2); plt.title('Debate activation across 96 matched questions')
for b,v in zip(bars,vals): plt.text(b.get_x()+b.get_width()/2,b.get_height()+1,f'{v:.1f}%',ha='center',va='bottom',color='black')
save('debate_activation')
# Evidence state counts for systems that record state
states=['agreement','disagreement','uncertain','insufficient','not_recorded']; statecols=['#59A14F','#E15759','#F28E2B','#BAB0AC','#4E79A7']
plt.figure(figsize=(10,5)); bottom=np.zeros(len(systems))
for state,col in zip(states,statecols):
    v=np.array([summary[s]['evidence_state_counts'].get(state,0) for s in systems]);
    plt.bar(x,v,bottom=bottom,label=state.title(),color=col,edgecolor='black',linewidth=.35); bottom+=v
plt.xticks(x,short,rotation=20,ha='right'); plt.ylabel('Number of traces'); plt.ylim(0,105); plt.title('Recorded evidence decisions (counts)'); plt.legend(ncol=3,frameon=False,loc='upper center',bbox_to_anchor=(.5,-.22)); save('evidence_states')
# latency percentiles
med=[summary[s]['latency_seconds']['median'] for s in systems]; p95=[summary[s]['latency_seconds']['p95'] for s in systems]
plt.figure(figsize=(10,4.8)); w=.36
plt.bar(x-w/2,med,w,label='Median',color='#4C78A8',edgecolor='black',linewidth=.4)
plt.bar(x+w/2,p95,w,label='95th percentile',color='#F58518',edgecolor='black',linewidth=.4)
plt.xticks(x,short,rotation=20,ha='right'); plt.ylabel('Seconds (log scale)'); plt.yscale('log'); plt.title('End-to-end trace latency'); plt.legend(frameon=False); save('latency')
# call attempts from traces
ok=[summary[s]['successful_calls_per_question_mean'] for s in systems]; fail=[summary[s]['failed_calls_per_question_mean'] for s in systems]
plt.figure(figsize=(10,4.8)); plt.bar(x,ok,color='#59A14F',label='Successful calls / question',edgecolor='black',linewidth=.4); plt.bar(x,fail,bottom=ok,color='#E15759',label='Failed calls / question',edgecolor='black',linewidth=.4)
plt.xticks(x,short,rotation=20,ha='right'); plt.ylabel('Mean calls per question'); plt.title('Recorded model-call outcomes'); plt.legend(frameon=False); save('model_calls')
# Debate outcomes as written in the debate_outcome object.
outcome_names=['completed','partial','failed','not_triggered']
outcome_cols=['#59A14F','#F2CF5B','#E15759','#BAB0AC']
plt.figure(figsize=(10,4.8)); bottom=np.zeros(len(systems))
for state,col in zip(outcome_names,outcome_cols):
    v=np.array([summary[s]['debate_outcome_counts'].get(state,0) for s in systems]); plt.bar(x,v,bottom=bottom,label=state.replace('_',' ').title(),color=col,edgecolor='black',linewidth=.35); bottom+=v
plt.xticks(x,short,rotation=20,ha='right'); plt.ylabel('Number of traces'); plt.ylim(0,105); plt.title('Debate outcomes recorded in traces'); plt.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,-.22),ncol=4); save('debate_outcomes')
# Recorded model signatures. These are metadata labels and may not prove which provider actually served a response.
model_names=sorted(set((t.get('evaluation_signature') or {}).get('opencode_model') or 'not_recorded' for ts in rows.values() for t in ts))
model_names=[m for m in model_names if m!='not_recorded']+(['not_recorded'] if 'not_recorded' in model_names else [])
model_cols=['#4C78A8','#F58518','#59A14F','#E15759']
plt.figure(figsize=(10,4.8)); bottom=np.zeros(len(systems))
for j,name in enumerate(model_names):
    v=np.array([summary[s]['opencode_model_signature_counts'].get(name,0) for s in systems]); plt.bar(x,v,bottom=bottom,label=name.replace('console-openrouter/',''),color=model_cols[j%len(model_cols)],edgecolor='black',linewidth=.35); bottom+=v
plt.xticks(x,short,rotation=20,ha='right'); plt.ylabel('Traces (out of 96)'); plt.ylim(0,105); plt.title('Model identifiers recorded in trace metadata'); plt.legend(frameon=False,fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.22),ncol=2); save('model_signature_mix')
# Retrieval coverage
usable=[summary[s]['usable_retrieval_agents_per_question_mean'] for s in systems]; claims=[summary[s]['retrieved_claims_per_question_mean'] for s in systems]
fig,ax=plt.subplots(figsize=(10,4.8)); ax.bar(x-w/2,usable,w,label='Usable retrieval agents / question',color='#4C78A8',edgecolor='black',linewidth=.4); ax.bar(x+w/2,claims,w,label='Retrieved claims / question',color='#72B7B2',edgecolor='black',linewidth=.4)
ax.set_xticks(x,short,rotation=20,ha='right'); ax.set_ylabel('Mean count'); ax.set_title('Retrieval output recorded in traces'); ax.legend(frameon=False); save('retrieval_coverage')

readme='''# Matched-result analysis (96 questions)\n\nThis folder preserves the 96 question traces shared by all six system configurations and includes seven Matplotlib plots (PNG and PDF) plus a JSON summary derived directly from those traces.\n\n## What the plots show\n\n- Debate activation by configuration.\n- Evidence-decision state counts.\n- Median and 95th-percentile end-to-end latency.\n- Mean successful and failed model calls per question.\n- Mean usable retrieval agents and retrieved claims per question.
- Debate outcomes (completed, partial, failed, or not triggered).
- Model identifiers recorded in the traces, showing the run's model-metadata mixture.\n\n## Interpretation limits\n\nThe six folders contain matching questions, but the trace files do not provide gold answer labels for this 96-question set. The saved metrics mark key-fact accuracy as unscored (zero scored samples); these zeros must not be interpreted as 0% accuracy. Accordingly, this analysis reports operational behavior only and makes no accuracy or superiority claim. Latencies and call outcomes are single-run observations.\n\nAll figures use white backgrounds and black text. The source data are copied under `traces/`; the generation script is `analysis/generate_plots.py`.\n'''
(out/'README.md').write_text(readme)
print('Wrote',out)
print(json.dumps(summary,indent=2))
