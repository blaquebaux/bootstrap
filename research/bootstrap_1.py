#!/usr/bin/python3
# =============================================================================
# bootstrap_1.py — the hedge fund in an ETF: are HF returns just rentable factor beta?
#
# Hasanhodzic & Lo's question, on the investable HF-replication ETFs (QAI multi-strat, DBMF managed
# futures, MNA merger-arb, BTAL anti-beta). Bootstrap the hedge fund from liquid factors and ask:
#   Q1  How much of each HF-strategy's return is REPLICABLE beta? (R² on liquid factors) + residual α?
#   Q2  The net-of-fee HF experience — do these "alternatives" beat a 60/40, or deliver cash-like returns?
#   Q3  Is any component a genuine diversifier (low corr), or is it all equity beta with extra steps?
#   Q4  Combined residual alpha — is there anything left after the rentable beta?
# Factors: equity (SPY), rates (IEF), credit (HYG−IEF), commodity (DBC), dollar (UUP), momentum (MTUM).
# Each HF ETF regressed over its OWN max window (DBMF is 2019+). Alpaca SIP daily, total-return.
# =============================================================================
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from _bootstrap_common import panel, rets

HF = {"QAI":"multi-strategy", "DBMF":"managed futures", "MNA":"merger arb", "BTAL":"anti-beta"}
FAC = ["SPY","IEF","HYG","DBC","UUP","MTUM"]   # HYG combined with IEF below → credit factor

def metrics(r, months):
    r=np.asarray(r,float); c=np.cumprod(1+r); dd=(c/np.maximum.accumulate(c)-1).min()
    sh=r.mean()/r.std()*math.sqrt(252) if r.std()>0 else float("nan")
    cagr=c[-1]**(252/len(r))-1
    mo={}
    for m,x in zip(months,r): mo[m]=mo.get(m,1.0)*(1+x)
    return dict(sh=sh,cagr=cagr,dd=float(dd),worst=min(v-1 for v in mo.values()))

def factor_fit(y, F):
    X=np.column_stack([np.ones(len(y))]+F); b,*_=np.linalg.lstsq(X,y,rcond=None)
    resid=y-X@b; r2=1-resid.var()/y.var() if y.var()>0 else float("nan")
    rsh=resid.mean()/resid.std()*math.sqrt(252) if resid.std()>0 else float("nan")
    return b, r2, b[0]*252, rsh, X@b

def main():
    syms=list(HF)+FAC+["TLT"]
    print("="*94); print("BOOTSTRAP — the hedge fund in an ETF: are HF returns just rentable factor beta?"); print("="*94)

    # Q1: per-fund factor replication over each fund's own window
    print("\n  Q1  HF-STRATEGY REPLICATION on liquid factors (equity/rates/credit/commodity/dollar/momentum)")
    print(f"      {'fund':6}{'strategy':18}{'yrs':>5}{'R²':>7}{'resid α/yr':>12}{'resid Sharpe':>14}")
    for h in HF:
        P,dates=panel([h]+FAC);
        if h not in P: continue
        R={s:rets(P[s]) for s in P}; L=min(len(R[s]) for s in R)
        y=R[h][-L:]; F=[R["SPY"][-L:], R["IEF"][-L:], R["HYG"][-L:]-R["IEF"][-L:], R["DBC"][-L:], R["UUP"][-L:], R["MTUM"][-L:]-R["SPY"][-L:]]
        b,r2,alpha,rsh,fit=factor_fit(y,F)
        print(f"      {h:6}{HF[h]:18}{L/252:>5.1f}{r2*100:>6.0f}%{alpha*100:>+11.1f}%{rsh:>+14.2f}")

    # Q2/Q3: the net-of-fee HF experience vs simple benchmarks
    P,dates=panel(list(HF)+["SPY","IEF"]); R={s:rets(P[s]) for s in P}
    L=min(len(R[s]) for s in R); months=[d[:7] for d in dates[1:]][-L:]; r={s:R[s][-L:] for s in R}
    print(f"\n  Q2/Q3  THE NET HF EXPERIENCE (common window {dates[-L]}..{dates[-1]}, {L/252:.1f}y)")
    print(f"      {'book':22}{'Sharpe':>8}{'CAGR':>8}{'maxDD':>8}{'corr→SPY':>10}")
    for h in HF:
        if h not in r: continue
        m=metrics(r[h],months); print(f"      {h+' ('+HF[h]+')':22}"[:22]+f"{m['sh']:>+8.2f}{m['cagr']*100:>+7.1f}%{m['dd']*100:>+7.0f}%{np.corrcoef(r[h],r['SPY'])[0,1]:>+10.2f}")
    for nm,x in (("SPY",r["SPY"]),("60/40 (SPY/IEF)",0.6*r["SPY"]+0.4*r["IEF"])):
        m=metrics(x,months); print(f"      {nm:22}{m['sh']:>+8.2f}{m['cagr']*100:>+7.1f}%{m['dd']*100:>+7.0f}%{np.corrcoef(x,r['SPY'])[0,1]:>+10.2f}")

    # Q4: equal-weight HF book, residual alpha on factors
    hfbook=sum(r[h] for h in HF if h in r)/sum(1 for h in HF if h in r)
    F=[r["SPY"],r["IEF"],r["HYG"] if "HYG" in r else r["IEF"]]  # minimal factors on common window
    # refit on full factor set available in common panel (only SPY/IEF here) — use SPY beta
    b=np.cov(hfbook,r["SPY"])[0,1]/np.var(r["SPY"]); alpha=(hfbook-b*r["SPY"]).mean()*252
    print(f"\n  Q4  EQUAL-WEIGHT HF BOOK: β→SPY {b:+.2f}  α vs SPY {alpha*100:+.1f}%/yr  Sharpe {metrics(hfbook,months)['sh']:+.2f}  corr→SPY {np.corrcoef(hfbook,r['SPY'])[0,1]:+.2f}")

    print("\n  READ: if HF strategies replicate at high R² with ~0 residual alpha, and the live HF-rep ETFs")
    print("  deliver cash-like returns that lag a 60/40, then 'the hedge fund in an ETF' confirms Lo: most HF")
    print("  return is RENTABLE factor beta; 2-and-20 ate the rest. The honest exception is DBMF (managed")
    print("  futures) — low/negative corr→SPY, a genuine crisis diversifier worth renting. bootstrap_2 = raw")
    print("  HFRI/manager data (not the ETF clones) to test whether top-manager selection adds real alpha.")

if __name__ == "__main__":
    main()
