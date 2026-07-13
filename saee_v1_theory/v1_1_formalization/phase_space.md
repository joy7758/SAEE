# SAEE v1.1 Phase Space

## Phase Space Definition

The SAEE phase space is:

Omega = G x S x T x R x L

A full state is:

x_t = (P_t, S_t, T_t, R_t, L_t)

with:

P_t in mu(G)

## Why This Is Not a Fitness Landscape

A fitness landscape usually treats selection as fixed or externally given.
SAEE treats selection as part of the evolving phase state.

Thus the system does not move over a fixed landscape. It moves through a
space in which:

- population changes;
- transformation operators change;
- selection fields change;
- observer state changes;
- lineage topology changes.

## Coupled Flow

The phase flow is:

(P_t, R_t, S_t, T_t, L_t) ->
(P_(t+1), R_(t+1), S_(t+1), T_(t+1), L_(t+1))

with:

P_(t+1) = S_t o T_t(P_t)

R_(t+1) = Phi(R_t, P_t, L_t)

T_(t+1) = U_T(T_t, R_(t+1), L_(t+1))

S_(t+1) = U_S(S_t, R_(t+1), P_(t+1))

L_(t+1) = Lambda(L_t, P_t, P_(t+1), T_t, S_t)

## Regimes

A regime is a region of Omega with characteristic flow behavior.

Possible regimes include:

- stable regime;
- exploratory regime;
- chaotic regime;
- collapse regime;
- regenerative regime;
- identity-stable regime;
- multi-attractor regime.

## Regime Transition

A transition occurs when:

rho(x_t) != rho(x_(t+1))

where rho maps phase states to regime classes.

Regime transitions may be caused by:

- selection topology change;
- transformation operator change;
- observer-state drift;
- lineage bottleneck;
- population collapse;
- attractor convergence;
- identity constraint crossing.

## Attractors

An attractor A subset Omega satisfies:

dist(F^k(x), A) -> 0

for x in a basin B_A.

Because Omega includes S, T, R, and L, an attractor may be:

- population attractor;
- selection topology attractor;
- reflexive observer attractor;
- lineage topology attractor;
- coupled attractor.

## Collapse and Regeneration

Collapse is contraction of reachable futures:

|A(x_(t+1))| << |A(x_t)|

Regeneration is expansion of reachable futures after contraction:

|A(x_(t+k))| > |A(x_t)|

for k > 0 after collapse.

## Dimensional Emergence

If the effective phase space changes:

Omega_t -> Omega_(t+1)

through emergence of new active dimensions, then the system undergoes
dimension-changing evolution.

This is stronger than movement inside a phase space. It is alteration of the
coordinates by which future movement is defined.

