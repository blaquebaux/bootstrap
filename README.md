# bootstrap

**The hedge fund in an ETF — are hedge-fund returns just rentable factor beta?**

Hasanhodzic & Lo's question, run on the investable HF-replication ETFs: `QAI` (multi-strategy), `DBMF`
(managed futures), `MNA` (merger arb), `BTAL` (anti-beta). Bootstrap each hedge-fund strategy from liquid
factors — equity, rates, credit, commodity, dollar, momentum — and ask what's replicable beta and what,
if anything, is left. Alpaca SIP daily, total-return; each fund regressed over its own max window.

## Verdict

**CONDITIONAL — mostly rentable factor beta, with one real exception.** The multi-strategy hedge fund
clone is ~75% replicable with zero residual alpha and delivers cash-like returns that lag a 60/40 —
confirming Lo: 2-and-20 ate the rest. The honest exception is **managed futures (`DBMF`)**, a genuinely
low-correlation crisis diversifier the linear clone can't capture. Rent that; skip the complex.

## Q1 — how much is replicable beta?

| fund | strategy | R² on liquid factors | residual α/yr | residual Sharpe |
|---|---|---|---|---|
| **QAI** | multi-strategy | **75%** | −0.3% | ~0 |
| MNA | merger arb | 27% | +0.4% | ~0 |
| BTAL | anti-beta | 29% | +5.2% | ~0 |
| **DBMF** | managed futures | **18%** | +5.2% | ~0 |

The multi-strat clone is three-quarters rentable beta with **no residual alpha**. Managed futures and
anti-beta have *low* R² — but that's because they're nonlinear (trend, convexity), not because they hide
linear alpha; the residual Sharpe is ~0 in every case.

## Q2/Q3 — the net hedge-fund experience (2019–2026)

| book | Sharpe | CAGR | maxDD | corr→SPY |
|---|---|---|---|---|
| QAI (multi-strat) | +0.67 | +4.5% | −15% | +0.82 |
| DBMF (managed futures) | +0.65 | +7.9% | −21% | **+0.11** |
| MNA (merger arb) | +0.37 | +2.4% | −17% | +0.52 |
| BTAL (anti-beta) | −0.21 | −5.7% | −53% | −0.53 |
| SPY | +0.86 | +15.9% | −34% | +1.00 |
| 60/40 (SPY/IEF) | +0.88 | +10.1% | −21% | +0.97 |

The "alternatives" delivered cash-to-mediocre returns and lagged a 60/40 — the net-of-fee hedge-fund
experience in investable form. `QAI` is equity beta (corr 0.82) at a fraction of SPY's return; `BTAL`
bled (anti-beta is a structural short). The standout is `DBMF`: a respectable +7.9% at **0.11
correlation** to equities — the one thing here that actually diversifies.

## Q4 — is there anything left as a book?

An equal-weight basket of the four is **market-neutral**: β→SPY +0.01, corr→SPY +0.03, with +2.8%/yr
over SPY-beta and Sharpe +0.53. Genuinely diversifying — and genuinely low-return. That's the honest
shape of "liquid alternatives": uncorrelated, not high-octane.

## How to use it (and what it is *not*)

bootstrap is a **diversifier** finding, not an aggressive engine — the aggressive capstone is
[`belligerent`](https://github.com/blaquebaux/belligerent). The usable conclusion: **rent managed
futures (`DBMF`) as a low-correlation diversifier** (it pairs with `boulder`/`bridgewater`), and don't
pay for the rest of the HF complex, which is rentable beta the clone already proves. For the family's
books, DBMF is a sleeve ingredient; QAI/MNA/BTAL are a lesson.

## `bootstrap_2`

The ETF clones are themselves fee'd replicas. The real test is raw **HFRI / manager-level** data: does
*top-decile manager selection* (not the index) add alpha beyond the rentable beta — the one place the
"2-and-20 is worth it" claim could still be true. That needs manager databases, not ETFs.

## Reproduce

```bash
export ALPACA_KEY_ID=... ALPACA_SECRET_KEY=...
python3 research/bootstrap_1.py
```

---

*Blaque Baux — a Carter Warrens research initiative. Research only; not investment advice. The verdict
falls where the data puts it — most of the hedge fund was rentable; the part that wasn't is the part that diversifies.*
