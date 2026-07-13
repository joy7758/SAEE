# SAEE v1.1 Dynamics

## Population State

The population at time t is:

P_t in mu(G)

where mu(G) is the space of probability measures over genome space G.

For a measurable subset A subset G:

P_t(A)

denotes the mass of population states in A at time t.

## Main Equation

The SAEE evolution equation is:

P_(t+1) = S_t o T_t(P_t)

This equation separates transformation from selection while allowing both
operators to be state-dependent.

## Coupled Operators

The transformation operator is reflexively coupled:

T_t = T(G, R_t, L_t)

The selection field is reflexively coupled:

S_t = S(G, R_t, E_t)

The observer state is dynamically updated:

R_(t+1) = Phi(R_t, P_t, L_t)

The lineage relation is dynamically updated:

L_(t+1) = Lambda(L_t, P_t, P_(t+1), T_t, S_t)

Thus the full evolution map is:

F(P_t, T_t, S_t, R_t, L_t) =
(P_(t+1), T_(t+1), S_(t+1), R_(t+1), L_(t+1))

## Nonlinear Coupled Flow

Let:

x_t = (P_t, T_t, S_t, R_t, L_t)

Then:

x_(t+1) = F(x_t)

where F is nonlinear because:

1. T_t depends on R_t and L_t.
2. S_t depends on R_t and contextual pressure.
3. R_(t+1) depends on P_t and L_t.
4. L_(t+1) depends on both transformation and selection.

## Continuous-Time Form

In a continuous-time approximation:

dP/dt = S_t(T_t(P_t)) - P_t

with:

dR/dt = phi(R_t, P_t, L_t)

dL/dt = lambda(L_t, P_t, T_t, S_t)

This expresses population flow, observer flow, and lineage flow as coupled
fields.

## Non-Markovian Character

A Markov process satisfies:

Pr(P_(t+1) | P_t, P_(t-1), ...) = Pr(P_(t+1) | P_t)

SAEE generally violates this condition because:

P_(t+1) = S(G, R_t, E_t) o T(G, R_t, L_t)(P_t)

and R_t and L_t encode historical dependence.

Thus:

Pr(P_(t+1) | P_t, R_t, L_t) != Pr(P_(t+1) | P_t)

in the general case.

## Reflexive Non-Markovian Definition

SAEE is reflexive non-Markovian when:

1. R_t is part of the system state.
2. R_t depends on prior population and lineage states.
3. T_t or S_t depends on R_t.
4. P_(t+1) depends on T_t or S_t.

The observer is therefore not a passive outside variable. It is an internal
state that modifies future evolutionary flow.

