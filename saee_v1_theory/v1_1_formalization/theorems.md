# SAEE v1.1 Core Theorems

## Theorem 1: Reflexive Drift Theorem

### Statement

In a SAEE system, evolution trajectories are generally not invariant under
fixed external fitness assumptions. They are invariant only relative to the
observer-dependent transformation and selection fields.

Formally, if:

P_(t+1) = S(G, R_t, E_t) o T(G, R_t, L_t)(P_t)

and:

partial T_t / partial R_t != 0

or:

partial S_t / partial R_t != 0

then:

partial P_(t+1) / partial R_t != 0

in the general case.

### Interpretation

The population trajectory depends on observer state. Therefore fixed-fitness
analysis is insufficient for reflexively coupled evolution.

### Proof Sketch

Let:

F_R(P_t) = S(G, R_t, E_t) o T(G, R_t, L_t)(P_t)

If T or S varies with R, then F_R varies with R unless the variation lies in a
null direction of P_t. Thus two observer states R_a and R_b can induce:

F_Ra(P_t) != F_Rb(P_t)

Therefore the population derivative or discrete transition depends on R_t.

## Theorem 2: Selection Topology Evolution Theorem

### Statement

In SAEE, the selection operator evolves in an operator space rather than
remaining a fixed scalar fitness map.

Let Omega_S be the space of selection fields. Then:

S_t in Omega_S

and:

S_(t+1) = Psi(S_t, R_t, P_t, L_t, E_t)

for some selection update functional Psi.

If Psi is non-constant, then selection topology evolves.

### Interpretation

Selection is a dynamic field. Its topology can change with observer state,
population distribution, lineage structure, and context.

### Proof Sketch

By definition, S_t depends on R_t and E_t. Since R_t evolves through:

R_(t+1) = Phi(R_t, P_t, L_t)

the input to S changes across time. If S responds non-trivially to that input,
then S_t and S_(t+1) may differ as elements of Omega_S. Therefore selection
is not fixed but evolves in selection-field space.

## Theorem 3: Emergent Attractor Theorem

### Statement

Stable regimes in SAEE emerge as fixed points or recurrent sets of reflexive
coupling:

P* = F(P*, R*, L*)

with:

R* = Phi(R*, P*, L*)

and:

L* = Lambda(L*, P*, P*, T*, S*)

where:

T* = T(G, R*, L*)

S* = S(G, R*, E*)

### Interpretation

An attractor is not merely a fixed genome distribution. It is a coupled fixed
point of population, observer, selection, transformation, and lineage.

### Proof Sketch

Let the coupled flow be:

x_(t+1) = F(x_t)

where:

x_t = (P_t, R_t, L_t, T_t, S_t)

A fixed point x* satisfies:

F(x*) = x*

Expanding x* yields the coupled equations above. Thus any stable regime that
persists under SAEE dynamics must be a fixed point or recurrent set of the
combined reflexive system, not of P alone.

## Corollary 1: Fixed Fitness Insufficiency

If R_t changes T_t or S_t, then no fixed scalar fitness landscape fully
determines the trajectory.

## Corollary 2: Observer Internalization

If R_t is produced by Phi(R_t, P_t, L_t), then the observer is internal to the
state flow rather than exogenous to it.

## Corollary 3: Attractor Multiplicity

Because attractors may arise in the coupled space:

Omega = G x S x T x R x L

multiple attractors may share similar population distributions while differing
in observer state, selection topology, or lineage topology.

