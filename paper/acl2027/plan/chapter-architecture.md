# Chapter architecture

| Section | Purpose | Main evidence | Target length |
|---|---|---|---:|
| 1 Introduction | Establish the evaluation problem and method idea | Prior work + result-independent framing | 550 words |
| 2 Related Work | Position the work against generative expansion and hybrid retrieval | Verified citations | 450 words |
| 3 Method | Define generation, Dense residual, Sparse anchor, and access analysis | Equations and properties | 600 words |
| 4 Experiments | Freeze evaluation and statistical protocol | Reproducibility record | 700 words |
| 5 Results | Answer the paper's empirical questions | Frozen CSV artifacts and paired tests | 1,050 words |
| 6 Conclusion | State the result and its boundary | Sections 3--5 | 180 words |

## Results chapter logic

The chapter begins with the evaluation claim because it motivates the paper's
measurement protocol. It then gives the primary result, explains that result
through the fixed $2\times2$ operator analysis, compares complete methods, and
ends with robustness and the observed failure case. Tables report macro and
per-dataset values; prose interprets rather than repeats every cell.
