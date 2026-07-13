# Lineage and Measure Formalization

## Lineage Relation

Lineage is defined as:

L subset G x G x R

Each element:

(g_parent, g_child, w) in L

represents a directed relation from parent state to child state with weight w.

The weight w may represent transformation magnitude, selection influence,
temporal distance, or a composite evolutionary influence measure.

## Directed Acyclic Condition

If lineage is time-ordered, then L forms a directed acyclic graph:

L = (V, A, w)

where:

- V subset G is the set of realized genome states.
- A subset V x V is the set of directed descent relations.
- w: A -> R is the edge weighting function.

The acyclic condition is:

there is no sequence g_0, g_1, ..., g_k such that
g_0 = g_k and (g_i, g_(i+1)) in A for all i.

## Weighted Lineage Influence

For edge e = (g_i, g_j), define:

w(e) = alpha m(e) + beta s(e)

where:

- m(e) is transformation influence.
- s(e) is selection influence.
- alpha and beta are theoretical weighting coefficients.

This provides a formal relation between variation and selection in lineage
structure.

## Population Measure over Lineage

The population measure P_t over G induces a measure over lineage vertices:

nu_t(V') = P_t(V')

for V' subset V.

For edges, an induced edge flow may be defined:

eta_t(e) = P_t(g_i) w(e)

for e = (g_i, g_j).

## Lineage Entropy

Let B_t be the set of active lineage branches at time t. Let p_b(t) be the
normalized mass of branch b.

Lineage entropy is:

H_L(t) = - sum_{b in B_t} p_b(t) log p_b(t)

Interpretation:

- Increasing H_L indicates diversification.
- Decreasing H_L indicates convergence or bottlenecking.
- Near-zero H_L indicates lineage collapse into a single dominant branch.

## Branching Density

For finite lineage graph L_t = (V_t, A_t), branching density is:

D_B(t) = |A_t| / max(1, |V_t|)

This measures how strongly the lineage graph expands relative to realized
states.

## Bottleneck Condition

A lineage bottleneck exists at state g when:

in_degree(g) >> mean in_degree

or:

P_t(g) dominates total branch mass.

The bottleneck condition indicates concentration of evolutionary continuity.

## Lineage Continuity

Lineage continuity from g_a to g_b exists when there is a directed path:

g_a -> ... -> g_b

in L.

Identity-stable continuity additionally requires that each edge on the path
satisfies an identity admissibility constraint.

