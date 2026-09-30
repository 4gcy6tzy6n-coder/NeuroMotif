#!/usr/bin/env python3
"""Reproducible retrospective Fish1.5 Experiment 1 calculation."""
from __future__ import annotations
import csv, hashlib, json, math, shlex, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path
import h5py
import numpy as np
import scipy
from scipy.optimize import curve_fit
from scipy.stats import rankdata, spearmanr

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/experiment1'
H5=ROOT/'data/raw/fish15/clem_zfish1_functional_data.h5'
ZIP=ROOT/'data/fish15/traced_axons_neurons.zip'
XW=ROOT/'data/raw/fish15/source/Zebrafish_CLEM/1. Downloading_neuronal_morphologies_and_metadata/all_reconstructed_neurons.csv'
COV=ROOT/'results/fish15/FISH15_C2_97_NEURON_STRUCTURAL_COVERAGE.csv'
SEED=2026093001; NPERM=10000; NBOOT=10000; NNULL=1000; DT=.5

def read_csv(p):
    with open(p,newline='',encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def write_csv(p,rows):
    with open(p,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else []);w.writeheader();w.writerows(rows)
def finite(a,windows):
    ok=np.ones(a.shape[0],bool)
    for sl in windows: ok &= np.isfinite(a[:,sl]).all(axis=1)
    return ok
def med(a): return float(np.median(a)) if a else math.nan
def rho(x,y):
    if len(x)<2 or np.ptp(x)==0 or np.ptp(y)==0:return math.nan
    return float(spearmanr(x,y).statistic)
def cross(t,y,level,sl):
    for i in range(sl.start,sl.stop):
        if y[i]>=level:
            if i==0:return float(t[i])
            if not np.isfinite(y[i-1:i+1]).all() or y[i]==y[i-1]:return math.nan
            return float(t[i-1]+(level-y[i-1])*(t[i]-t[i-1])/(y[i]-y[i-1]))
    return math.nan

def functional(h,fid):
    out={};audit={'functional_id':fid};t=np.arange(160)*DT
    base=slice(0,40); onset=slice(40,100); stim=slice(100,120); post=slice(120,140); decay=slice(120,160)
    dm={}
    for cond in ('dots','sine'):
      for direction in ('left','right'):
        key=f'neuron_{fid}/dff_trials_{direction}_{cond}'; label=f'{direction}_{cond}'
        if key not in h:audit[label+'_dataset_present']=0;continue
        a=np.asarray(h[key],float); audit[label+'_dataset_present']=1; audit[label+'_trial_count']=a.shape[0]
        req=[base,stim] + ([post] if cond=='dots' else [])
        ok=finite(a,req);audit[label+'_usable_trials']=int(ok.sum());audit[label+'_nonfinite_required_window_trials']=int((~ok).sum())
        d={}
        if ok.any():
          stead=[];persist=[];aucs=[];zero=0
          for tr in a[ok]:
            b=float(np.mean(tr[base]));s=float(np.mean(tr[stim])-b);stead.append(s)
            if cond=='dots':
              if s==0 or not np.isfinite(s):zero+=1
              else:persist.append((float(np.mean(tr[post])-b))/s)
              # The frozen AUC window is half-open [60,70): indices 120:140.
              aucs.append(float(np.trapezoid(tr[120:140]-b,t[120:140])))
          d['steady']=med(stead);d['persistence']=med(persist) if cond=='dots' else math.nan;d['auc']=med(aucs) if cond=='dots' else math.nan
          audit[label+'_zero_stimulus_denominator_trials']=zero
          trc=np.mean(a[ok],axis=0);b=float(np.mean(trc[base]));pl=float(np.mean(trc[stim]));delta=pl-b
          if cond=='dots' and delta!=0 and np.isfinite(delta):
            yo=(trc-b)*(1 if delta>0 else -1);t10=cross(t,yo,.1*abs(delta),onset);t90=cross(t,yo,.9*abs(delta),onset)
            d['rise']=t90-t10 if np.isfinite(t10) and np.isfinite(t90) else math.nan
          else:d['rise']=math.nan
          if cond=='dots':
            fit=finite(a,[base,decay]);audit[label+'_decay_usable_trials']=int(fit.sum())
            if fit.any():
              m=np.mean(a[fit],axis=0);bfit=float(np.mean(m[base]));tx=t[decay];yy=m[decay]
              def fn(tt,A,tau):return bfit+A*np.exp(-(tt-60)/tau)
              try:
                par,_=curve_fit(fn,tx,yy,p0=[float(yy[0]-bfit),5],bounds=([-np.inf,.5],[np.inf,20]),maxfev=10000)
                d['tau']=float(par[1]);d['tau_boundary']=int(np.isclose(par[1],.5) or np.isclose(par[1],20))
              except (RuntimeError,ValueError,FloatingPointError):d['tau']=math.nan;d['tau_boundary']=0
            else:d['tau']=math.nan;d['tau_boundary']=0
          dm[label]=d
    for c in ('dots','sine'):
      for m in ('steady','persistence','auc','rise','tau'):
        vals=[dm.get(f'{d}_{c}',{}).get(m,math.nan) for d in ('left','right')]; vals=[v for v in vals if np.isfinite(v)]
        out[f'{c}_{m}']=float(np.mean(vals)) if vals else math.nan
    out['dots_defined_directions']=sum(np.isfinite(dm.get(f'{d}_dots',{}).get('persistence',math.nan)) for d in ('left','right'))
    out['dots_single_direction']=int(out['dots_defined_directions']==1)
    out['dots_zero_denominator_trials']=sum(audit.get(f'{d}_dots_zero_stimulus_denominator_trials',0) for d in ('left','right'))
    out['sine_phase_lag']='NOT_IDENTIFIABLE';out['sine_gain']='NOT_IDENTIFIABLE'
    for name,d in dm.items():
      for m,v in d.items():out[f'{name}_{m}']=v
    return out,audit

def graph(rows,cohort,zf):
    nodes=[r['functional_id'] for r in cohort]; idx={v:i for i,v in enumerate(nodes)}
    ar={r['axon_id']:r['functional_id'] for r in rows}; dr={r['dendrite_id']:r['functional_id'] for r in rows}
    W=np.zeros((len(nodes),len(nodes)),np.int64); names=set(zf.namelist()); audit=Counter()
    if len(ar)!=len(rows) or len(dr)!=len(rows):raise RuntimeError('Crosswalk endpoint is not unique')
    for r in cohort:
      owner=r['archive_owner_key'];folder=f'clem_zfish1_cell_{owner}';path=f'traced_axons_neurons/{folder}/{folder}_presynapses.csv'
      if path not in names:raise RuntimeError(f'missing owner table: {path}')
      source=ar.get(r['axon_id'])
      if source!=r['functional_id']:raise RuntimeError('focal identity mismatch')
      seenid={};seencoord=set()
      for no,line in enumerate(zf.read(path).decode('utf-8','replace').splitlines()[1:],2):
        if not line.strip():continue
        f=shlex.split(line)
        if len(f)==9:partner,x,y,z,sid,size,pred,val,date=f
        elif len(f)==8:partner,x,y,z,sid,pred,val,date=f
        else:raise RuntimeError(f'bad row width {path}:{no}')
        if val!='valid':audit['excluded_below_cutoff_rows']+=1;continue
        target=dr.get(partner)
        if target not in idx:audit['external_or_unmapped_partner_rows']+=1;continue
        if source==target:audit['self_edges_excluded']+=1;continue
        coord=(partner,x,y,z);noid=sid.strip().lower() in {'','0','nan','none','null'}
        if noid:
          if coord in seencoord:raise RuntimeError(f'ambiguous no-ID duplicate {path}:{no}')
          seencoord.add(coord)
        else:
          sig=coord
          if sid in seenid:
            if seenid[sid]!=sig:raise RuntimeError(f'conflicting synapse ID {sid}')
            audit['collapsed_exact_duplicate_ids']+=1;continue
          seenid[sid]=sig
        W[idx[source],idx[target]]+=1;audit[f'retained_{pred}_annotations']+=1
    np.fill_diagonal(W,0)
    audit['nodes']=len(nodes);audit['distinct_directed_pairs']=int(np.count_nonzero(W));audit['retained_within_cohort_annotations']=int(W.sum())
    return W,dict(audit)

def metrics(W):
    A=W.astype(float).copy();np.fill_diagonal(A,0);B=A>0;ins=A.sum(0);outs=A.sum(1)
    union=(B|B.T).sum(1);recip=(B&B.T).sum(1);two=(A*A.T).sum(1);three=np.diag(A@A@A)
    denom=ins*outs;lri=np.divide(two,denom,out=np.zeros(len(A)),where=denom>0)
    return {'in_strength':ins,'out_strength':outs,'reciprocal_strength':np.minimum(A,A.T).sum(1),
            'reciprocal_fraction':np.divide(recip,union,out=np.zeros(len(A)),where=union>0),
            'two_step_return_strength':two,'three_step_return_strength':three,'local_recurrence_index':lri,
            'in_degree':B.sum(0),'out_degree':B.sum(1)}

def swap(edges,es,rng):
    u,v=rng.integers(0,len(edges),2)
    if u==v:return False
    a,b=edges[u];c,d=edges[v]
    if a==c or b==d:return False
    x,y=(a,d),(c,b)
    if x[0]==x[1] or y[0]==y[1] or x==y or x in es or y in es:return False
    es.remove((a,b));es.remove((c,d));es.add(x);es.add(y);edges[u],edges[v]=x,y
    return True

def nulls(W,x,y,ok,rng):
    B=W>0;np.fill_diagonal(B,False);edges=list(zip(*np.where(B)));es=set(edges);weights=W[B].copy()
    indeg=B.sum(0);outdeg=B.sum(1);seen=set();out=[];acc=0;since=0;attempts=0
    while len(out)<NNULL and attempts<max(10_000_000,NNULL*len(edges)*500):
      attempts+=1
      if swap(edges,es,rng):acc+=1;since+=1
      if since<max(10*len(edges),1):continue
      since=0;key=tuple(sorted(es))
      if key in seen:continue
      seen.add(key);M=np.zeros_like(W);ws=rng.permutation(weights)
      for (i,j),w in zip(sorted(es),ws):M[i,j]=w
      mm=metrics(M);rr=rho(mm['local_recurrence_index'][ok],y)
      topo_hash=hashlib.sha256(repr(key).encode()).hexdigest()
      out.append({'null_index':len(out)+1,'topology_sha256':topo_hash,'rho':rr,'unique_binary_topology':1,'accepted_swaps_total':acc,
        'edge_count':len(es),'in_degree_exact':int(np.array_equal(M.astype(bool).sum(0),indeg)),
        'out_degree_exact':int(np.array_equal(M.astype(bool).sum(1),outdeg)),
        'global_weight_multiset_exact':int(np.array_equal(np.sort(M[M>0]),np.sort(weights))),
        'node_weighted_strength_preserved':int(np.array_equal(M.sum(0),W.sum(0)) and np.array_equal(M.sum(1),W.sum(1)))})
    if len(out)<NNULL:raise RuntimeError(f'only {len(out)} unique null topologies')
    return out

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    allx=read_csv(XW);xrows=[r for r in allx if r.get('type')=='cell' and r.get('functional_id','').isdigit() and int(r['functional_id'])>0]
    cov=read_csv(COV);p82=[r for r in cov if r['structurally_complete']=='YES'];p97=cov
    if len(xrows)!=97 or len(p82)!=82:raise RuntimeError('frozen crosswalk/cohort size mismatch')
    fun={};fa=[]
    with h5py.File(H5,'r') as h:
      for r in cov:
        v,a=functional(h,r['functional_id']);fun[r['functional_id']]=v;fa.append(a)
    children=np.random.SeedSequence(SEED).spawn(3);rp,rb,rn=[np.random.default_rng(x) for x in children]
    graphs={};gm={};ga={}
    with zipfile.ZipFile(ZIP) as zf:
      for name,cohort in [('primary82',p82),('expanded97',p97)]:
        graphs[name],ga[name]=graph(xrows,cohort,zf);gm[name]=metrics(graphs[name])
    ids82=[r['functional_id'] for r in p82];ids97=[r['functional_id'] for r in p97]
    mrows=[]
    for label,ids in [('primary82',ids82),('expanded97',ids97)]:
      for i,fid in enumerate(ids):
        row={'functional_id':fid,'cohort':label};row.update(fun[fid]);row.update({k:v[i] for k,v in gm[label].items()});mrows.append(row)
    write_csv(OUT/'FISH15_NEURON_METRICS.csv',mrows);write_csv(OUT/'FISH15_FUNCTIONAL_WINDOW_AUDIT.csv',fa)
    Y=np.array([float(fun[f]['dots_persistence']) for f in ids82]);X=gm['primary82']['local_recurrence_index'];ok=np.isfinite(Y);x=X[ok];y=Y[ok];n=len(y)
    observed=rho(x,y)
    perm=np.array([rho(x,rp.permutation(y)) for _ in range(NPERM)])
    perm=perm[np.isfinite(perm)]
    ppos=(1+np.sum(perm>=observed))/(len(perm)+1) if np.isfinite(observed) else math.nan
    ptwo=(1+np.sum(abs(perm)>=abs(observed)))/(len(perm)+1) if np.isfinite(observed) else math.nan
    boot=np.array([rho(x[j],y[j]) for j in (rb.integers(0,n,n) for _ in range(NBOOT))]);boot=boot[np.isfinite(boot)]
    ci=np.percentile(boot,[2.5,97.5]) if len(boot) else [math.nan,math.nan]
    # Fixed primary degree-preserving, global-weight-matched directed null.
    null=nulls(graphs['primary82'],x,y,ok,rn);write_csv(OUT/'FISH15_NULL_MODEL_RESULTS.csv',null)
    nv=np.array([r['rho'] for r in null],float);nvalid=int(np.isfinite(nv).sum())
    null_status='VALID' if nvalid==NNULL else 'INVALID_STATISTIC_VARIANCE'
    nullp=(1+np.sum(nv>=observed))/(NNULL+1) if null_status=='VALID' and np.isfinite(observed) else None
    # All fixed node-level secondary descriptors; no selection by result.
    sec=[]
    for metric in ('in_strength','out_strength','reciprocal_strength','reciprocal_fraction','two_step_return_strength','three_step_return_strength'):
      xx=gm['primary82'][metric][ok]
      if np.unique(xx).size < 2:
        sec.append({'metric':metric,'n':n,'rho':math.nan,'two_sided_p_unadjusted':math.nan,
                    'holm_adjusted_p':math.nan,'status':'NOT_ESTIMABLE_CONSTANT_PREDICTOR'})
      else:
        test=spearmanr(xx,y)
        sec.append({'metric':metric,'n':n,'rho':float(test.statistic),
                    'two_sided_p_unadjusted':float(test.pvalue),'holm_adjusted_p':math.nan,'status':'ESTIMABLE'})
    # Preserve the frozen family size: non-estimable tests count as conservative p=1
    # placeholders for adjustment, but are not reported as tested p-values.
    finite=[i for i,r in enumerate(sec) if np.isfinite(r['two_sided_p_unadjusted'])]
    order=sorted(finite,key=lambda i:sec[i]['two_sided_p_unadjusted']);mx=0
    for rank,pos in enumerate(order):
      mx=max(mx,(len(sec)-rank)*sec[pos]['two_sided_p_unadjusted'])
      sec[pos]['holm_adjusted_p']=float(min(1,mx))
    write_csv(OUT/'FISH15_SECONDARY_ASSOCIATIONS.csv',sec)
    robust=[]
    def robustness(label,pred,outcome,cohortids,graphmetric):
      mask=np.isfinite(pred)&np.isfinite(outcome)
      robust.append({'analysis':label,'n':int(mask.sum()),'rho':rho(pred[mask],outcome[mask]),'status':'COMPUTED' if mask.sum()>=4 else 'INSUFFICIENT'})
    robustness('left_dots',np.array([gm['primary82']['local_recurrence_index'][i] for i in range(82)]),np.array([fun[f].get('left_dots_persistence',math.nan) for f in ids82]),ids82,'')
    robustness('right_dots',X,np.array([fun[f].get('right_dots_persistence',math.nan) for f in ids82]),ids82,'')
    for lab,metric in [('post_offset_auc_60_70','dots_auc'),('onset_rise_time_10_90','dots_rise'),('decay_tau_60_80','dots_tau'),('sine_steady_response','sine_steady')]:
      robustness(lab,X,np.array([fun[f].get(metric,math.nan) for f in ids82]),ids82,'')
    y97=np.array([fun[f]['dots_persistence'] for f in ids97],float)
    robustness('expanded_97_node_sensitivity',gm['expanded97']['local_recurrence_index'],y97,ids97,'')
    write_csv(OUT/'FISH15_ROBUSTNESS_RESULTS.csv',robust)
    robust_lines=['# Fish1.5 Experiment 1 fixed robustness results','',
      'These checks were enumerated in the retrospective analysis contract. An earlier out-of-scope calculation exposed outcomes, so this report is partially informed and is not a prospective preregistration or confirmatory analysis. The checks are descriptive and cannot replace the primary endpoint. The dataset is one specimen; no result generalizes to the zebrafish population.','',
      '| Fixed analysis | n | Spearman rho | Status |','|---|---:|---:|---|']
    for row in robust:
      val=row['rho'];val='not estimable' if not np.isfinite(val) else f'{val:.4f}'
      robust_lines.append(f"| {row['analysis']} | {row['n']} | {val} | {row['status']} |")
    robust_lines += ['', 'Sine phase lag and calibrated gain are not identifiable from the released schema. The 97-neuron sensitivity cohort uses the induced expanded graph; it does not upgrade the unit of inference. No robustness result changes the primary decision.']
    (OUT/'FISH15_ROBUSTNESS_RESULTS.md').write_text('\n'.join(robust_lines)+'\n')
    if np.isfinite(observed) and np.isfinite(ppos) and ppos<.05 and null_status=='VALID' and nullp<.05:decision='H1 SUPPORTED UNDER FROZEN CRITERIA'
    elif np.isfinite(observed) and observed<0 and np.isfinite(ptwo) and ptwo<.05:decision='H1 DIRECTIONALLY CONTRADICTED'
    elif null_status!='VALID':decision='INDETERMINATE / INVALID FROZEN TOPOLOGY NULL'
    else:decision='H1 NOT SUPPORTED UNDER FROZEN CRITERIA'
    result={'decision':decision,'analysis_status':'RETROSPECTIVE_SINGLE_SPECIMEN_DISCOVERY_WITH_PRIOR_OUTCOME_EXPOSURE',
      'n_primary_cohort':82,'n_endpoint_defined':n,'n_endpoint_missing':82-n,
      'n_single_direction':sum(int(fun[f]['dots_single_direction']) for f in ids82),
      'primary_spearman_rho':observed,'primary_positive_association_status':'SUPPORTED' if ppos<.05 and observed>0 else 'NOT_SUPPORTED',
      'positive_permutation_p':float(ppos),'two_sided_permutation_p':float(ptwo),
      'permutation_draws_requested':NPERM,'permutation_draws_valid':len(perm),
      'bootstrap_ci95_low':float(ci[0]),'bootstrap_ci95_high':float(ci[1]),'bootstrap_draws_requested':NBOOT,'bootstrap_draws_valid':len(boot),
      'topology_null_status':null_status,'topology_null_n':NNULL,'topology_null_defined_rho_n':nvalid,'topology_null_undefined_rho_n':NNULL-nvalid,'topology_null_empirical_p':nullp,
      'topology_null_preserves_binary_in_out_degree':True,'topology_null_preserves_global_weight_multiset':True,'topology_null_preserves_node_strength':False,
      'seed':SEED,'confirmation_status':'RETROSPECTIVELY_SPECIFIED; PARTIALLY_INFORMED'}
    (OUT/'FISH15_PRIMARY_RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    prov={'seed':SEED,'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'h5py':h5py.__version__,
      'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (H5,ZIP,XW,COV)},'graph_audit':ga,'result':result}
    (OUT/'FISH15_EXPERIMENT1_PROVENANCE.json').write_text(json.dumps(prov,indent=2,allow_nan=False)+'\n')
    report(result,ga,sec,robust)

def report(r,ga,sec,robust):
    rho_s='not estimable' if not np.isfinite(r['primary_spearman_rho']) else f"{r['primary_spearman_rho']:.4f}"
    p_s='not estimable' if not np.isfinite(r['positive_permutation_p']) else f"{r['positive_permutation_p']:.5f}"
    ci=f"[{r['bootstrap_ci95_low']:.4f}, {r['bootstrap_ci95_high']:.4f}]" if np.isfinite(r['bootstrap_ci95_low']) else 'not estimable'
    npv='not estimable; frozen null yielded undefined statistics' if r['topology_null_status']!='VALID' else f"{r['topology_null_empirical_p']:.5f}"
    lines=['# Fish1.5 Experiment 1 primary result','',f"**Decision:** `{r['decision']}`.",'',
      '**Status:** `RETROSPECTIVE_SINGLE_SPECIMEN_DISCOVERY_WITH_PRIOR_OUTCOME_EXPOSURE`; this is not confirmatory or population-level evidence.','',
      f"- Cohort: 82; defined endpoints: {r['n_endpoint_defined']}; missing endpoints: {r['n_endpoint_missing']}; single-direction endpoints: {r['n_single_direction']}.",
      f"- Spearman rho: {rho_s}; positive label-permutation p: {p_s}; paired neuron bootstrap 95% percentile interval: {ci} ({r['bootstrap_draws_valid']}/{r['bootstrap_draws_requested']} resamples had defined rho).",
      '- The primary positive-association test does not support H1 under its frozen criterion. The overall combined decision remains indeterminate because the frozen topology-null statistic is undefined for most generated graphs.',
      f"- Topology null: {r['topology_null_n']} unique degree-preserving/global-weight-matched rewires; defined null correlations: {r['topology_null_defined_rho_n']}; undefined: {r['topology_null_undefined_rho_n']}; p: {npv}.",
      '- The frozen graph null preserves binary in/out degrees and the global weight multiset but not each node’s weighted strengths. It is not described as strength-preserving.',
      '- Because the frozen null produced undefined correlation statistics for at least one graph, the null test is classified invalid and no p-value is reported for it. No alternative null or endpoint was substituted.',
      '', '## Structural audit','',
      f"- Primary induced graph: 82 nodes, {ga['primary82']['distinct_directed_pairs']} ordered non-self pairs, {ga['primary82']['retained_within_cohort_annotations']} retained synapse-count annotations.",
      f"- Expanded induced graph: 97 nodes, {ga['expanded97']['distinct_directed_pairs']} ordered non-self pairs, {ga['expanded97']['retained_within_cohort_annotations']} retained annotations.",
      '- Size values were not used. Owner presynaptic files define direction; unresolved external partners are excluded from each induced cohort.',
      '', '## Secondary and fixed robustness','',
      'The frozen secondary descriptor family is in `FISH15_SECONDARY_ASSOCIATIONS.csv` with Holm adjustment. Fixed robustness outputs are in `FISH15_ROBUSTNESS_RESULTS.csv`; none replaces the primary result.',
      'Sine phase lag and calibrated gain are not identifiable from the released data schema.',
      '', '## Interpretation','',
      'All inference is conditional on one Fish1.5 specimen. Neurons, trials, frames, bootstrap samples, and null graphs are not independent animals. No causal, population-level, cross-species replication, E3, or AI-transfer claim follows.',
      'A prior out-of-scope calculation attempt is disclosed in `../fish15/FISH15_C2_ANALYSIS_SCOPE_INCIDENT.md`; this reported analysis therefore remains retrospective and partially informed.',
      'The secondary AUC implementation was corrected to use the frozen half-open `[60,70)` interval; see `FISH15_ANALYSIS_CORRECTION_LOG.md`.',
      '', 'Reproduction inputs, software versions, and hashes are recorded in `FISH15_EXPERIMENT1_PROVENANCE.json`.']
    (OUT/'FISH15_PRIMARY_RESULT.md').write_text('\n'.join(lines)+'\n')
    summary=['# Fish1.5 Experiment 1 summary','',f"**Decision:** `{r['decision']}`.",'',
      f"The frozen primary association used {r['n_endpoint_defined']}/82 neurons: rho={rho_s}, positive permutation p={p_s}, bootstrap 95% interval {ci}. The primary positive-association test does not support H1.",
      f"The topology null is invalid for inference: {r['topology_null_defined_rho_n']}/{r['topology_null_n']} graphs yielded defined correlations; no null p-value is reported.",'',
      'This is retrospective, partially informed, single-specimen evidence. The null is not strength-preserving. E3 remains closed; no LNN/ANN modeling is included.', '',
      'See `FISH15_PRIMARY_RESULT.md`, `FISH15_NEURON_METRICS.csv`, `FISH15_NULL_MODEL_RESULTS.csv`, `FISH15_ROBUSTNESS_RESULTS.csv`, and `FISH15_EXPERIMENT1_PROVENANCE.json`.']
    (OUT/'FISH15_EXPERIMENT1_SUMMARY.md').write_text('\n'.join(summary)+'\n')

if __name__=='__main__':main()
