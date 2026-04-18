# GB-style Extension-Field Arithmetic: Experimental Repository

Implementation and experimental material for studying a GB-style structural view of multiplication over extension fields of the form **GF(2^m)[x]/<g(x)>**.

## Scope

The repository supports a paper whose main contribution is **structural and algorithmic** rather than a universal performance claim. The work studies how multiplication can be interpreted as the composition of:

1. An **accumulation / Toeplitz-like convolution** stage
2. A **fixed reduction** stage induced by the modulus polynomial

The goal is to evaluate **when this view is competitive**, under bounded experimental conditions.

## What This Repository Provides

- Arithmetic components for polynomial and extension-field operations
- GB-style multiplication variants
- Reference/direct multiplication baselines
- Correctness checks across selected parameter ranges
- Phase-separated benchmarking infrastructure
- Reporting utilities for tables and figures

## Intended Claims Supported by This Repository

The repository is intended to support the following bounded claims:

- A **structural reformulation** of GB-style arithmetic
- **Phase-separated measurement** of accumulation and reduction costs
- **Comparable evaluation settings** for selected algorithmic variants
- Empirical evidence that the approach can be **competitive in some regimes**
- Observational evidence of **more regular computational structure**

## Important Limitations

This repository does **not** by itself establish:

- Universal superiority over existing methods
- A general performance theorem
- Broad applicability beyond the tested regimes
- A proof of constant-time behavior
- A proof of side-channel resistance

Any regularity-oriented measurements or fixed-shape execution observations should be interpreted only as **proxy-style evidence**, not as a security proof.

## Installation

### Requirements
- Python 3.10+
- pip or conda

### Setup

```bash
