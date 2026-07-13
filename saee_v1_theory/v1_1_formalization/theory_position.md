# SAEE v1.1 Theory Position

## Core Claim

SAEE v1.1 is a reflexive non-Markovian nonlinear measure dynamical system.

The essential object is:

SAEE = (Omega, G, T, S, L, R, mu)

with:

P_t in mu(G)

and:

P_(t+1) = S_t o T_t(P_t)

## Distinction from Evolutionary Computation

In many evolutionary computation formalisms, the selection function is fixed
or externally specified.

In SAEE:

S_t = S(G, R_t, E_t)

Selection is a reflexive field and may evolve as part of the phase state.

## Distinction from Artificial Life

In many artificial life frameworks, observation is external to the evolving
system.

In SAEE:

R_t in Omega

and:

R_(t+1) = Phi(R_t, P_t, L_t)

The observer state is internal to the formal dynamics.

## Distinction from General Complex Systems

Complex systems theory often studies nonlinear coupled flows, but it does not
necessarily include genotype operator space as a primitive.

In SAEE:

T_t in T

and transformation space is part of the phase state.

## Distinction from Fixed Fitness Landscapes

SAEE does not assume a fixed fitness landscape. It defines:

Omega = G x S x T x R x L

Thus the landscape, operators, observer, and lineage can co-vary.

## Minimal Novelty Statement

SAEE formalizes evolution as a coupled flow of:

1. population measure;
2. transformation operator;
3. selection field;
4. lineage topology;
5. reflexive observer state.

The observer is not external. Selection is not fixed. Transformation is not
independent of observation. Lineage is not merely historical metadata. These
objects form one coupled dynamical system.

## Academic Risk Boundary

The v1.1 formal system is a theoretical candidate. It does not by itself
establish empirical validity, universality, or superiority over existing
models. Those require separate empirical alignment and mathematical proof.

