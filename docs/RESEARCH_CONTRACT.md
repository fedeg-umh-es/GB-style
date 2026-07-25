# Research contract: exact frontier gate

## Scientific question

For the quotient algebra

\[
\mathcal A_G = GF(2^m)[y]/\langle G(y)\rangle,
\]

under which support, coefficient-class and operation-cost conditions is a
separated convolution-then-reduction DAG preferable to a fused realization?

## Primary architectures

- `SEP_SB`: schoolbook convolution materialized in `2k-1` coefficients,
  followed by descending fixed reduction.
- `FUS_CAN`: diagnostic canonical fused DAG with independent output sums.
- `TMVP_REF`: mandatory source-matched published comparator before any Q1 claim.

## Cost vector

\[
C = (M_v, M_c, A, D, S),
\]

where `M_v` is variable-variable multiplication, `M_c` is multiplication by a
fixed coefficient, `A` is addition in `GF(2^m)`, `D` is DAG depth, and `S` is
materialized-node count.

The sensitivity model is

\[
C_\rho = \rho_v M_v + \rho_c M_c + A.
\]

The values of `rho_c` in the configuration are scenarios, not hardware
measurements.

## Shared implementation policy

1. Fan-out is free.
2. A variable product `a_i*b_j` is built once.
3. The same scalar multiple of the same signal by the same constant may fan out.
4. No other CSE is performed.
5. Every explicit binary addition is one node.
6. No wall-clock result is admissible as Q1 evidence.

## Scope limits

- `FUS_CAN` is not called Mastrovito or TMVP.
- A positive SEP/FUS result only permits implementation of `TMVP_REF`.
- The quotient is called a field only when irreducibility of `G` is verified.
- No area, power, frequency or Throughput claim is made without RTL and synthesis.
- No deterministic irreducible-construction claim is made.

## Binary gate

### PROMOTE_TO_TMVP

A model-dependent SEP/FUS crossover occurs across multiple degrees and support
families under the preregistered thresholds. The next and only allowed action is
to reproduce a named TMVP/Mastrovito comparator under the same model.

### CLOSE_LINE

No stable crossover appears, or the effect is attributable only to the chosen
sharing asymmetry. No manuscript and no additional multiplier variant are opened.

## Q1 gate

A manuscript is allowed only after all of the following exist:

1. a verified prior-art gap;
2. a source-matched `TMVP_REF`;
3. an exact theorem or tight bound explaining the frontier;
4. validation on held-out degrees or families;
5. a non-trivial architecture-selection consequence.
