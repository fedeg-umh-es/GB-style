# Paper Mapping

This document explicitly maps the theoretical, algorithmic, and empirical claims of the GB-style formulation to specific code modules and reproducible experiments within this repository. 

| Claim | Claim Type | Module | Test | Experiment | Output Table/Figure | Limitation / Scope |
| --- | --- | --- | --- | --- | --- | --- |
| Convolution over $GF(2^m)$ admits redundancy matrix $T(a)$ | Mathematical | `gbstyle.linear_operator` | `test_toeplitz_equivalence` | `correctness_matrix` | `correctness_summary.csv` | Limited to generic $T(a)$ matrix materialization for small sizes. |
| Polynomial multiplication in quotient ring decomposes into Toeplitz mapping and fixed reduction | Mathematical | `gbstyle.multiply_schoolbook` | `test_gb_multiplication` | `correctness_matrix` | N/A | Procedural implementation doesn't strictly formulate sparse arrays. |
| Accumulation decoupled from reduction yields more regular control flow | Algorithmic | `gbstyle.multiply_karatsuba` | `test_ct_proxy` | `ct_proxy_study` | `ct_proxy_stats.csv` & plot | Proxy metrics only (branch count/loop iterations); NOT side-channel proof. |
| GB-style scales better for sparse module $g(x)$ in specific $k$ branches | Empirical | `gbstyle.multiply_karatsuba` | `test_sparse_cost` | `sparse_modulus_study` | `sparse_ratios.csv` & plot | Depends greatly on Numba / baseline Python overheads vs compiled code. |
| Empirical Break-even analysis over various $(m, k)$ | Empirical | `experiments.break_even_study` | N/A | `break_even_study` | `theory_vs_empirical.csv` & plot | Affected by interpreter cache and Python object overhead vs C implementations. |

> [!WARNING]
> Claims related to "regular control flow" or "constant-time proxy metrics" strictly refer to algorithmic instruction layout and conditional branching. They **DO NOT** constitute a proof of side-channel resilience, nor do they guarantee constant time under actual hardware compilation or execution.
