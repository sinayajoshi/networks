# Dynamic Batched Allocation with Peer Effects and Endogenous Capacity

## What the base paper does (Qiu et al. 2025)

**Static position allocation**: Assign n players to vertices of a graph G. Each player i has utility u_i(S(i), C_i^S) depending on (a) their own vertex and (b) the type-composition of their graph neighborhood. Maximize sum of utilities.

**Main results**:
- General case: cannot approximate within 1/n^{1−ε} unless P=NP (Theorem 1)
- Even on subgrid graphs: NP-hard (Theorem 2)
- PTAS on graphs with bounded local treewidth, when same-type players share a utility function — UNIFORM class (Theorem 4)

**Critical assumption the paper does NOT relax**:
- Allocation is a one-shot, simultaneous decision
- Capacities are fixed and exogenous
- No dynamics; welfare is evaluated once

---

## The gap this project fills

Three interacting features are absent from the literature:

1. **Batching**: players arrive in waves; the planner can delay assignment to coordinate across a batch
2. **Dynamics**: today's composition becomes the state that shapes tomorrow's peer effects
3. **Endogenous capacity**: communities (schools, neighborhoods, sponsors) participate more or less in future periods based on outcomes they experienced

Each feature alone has been studied in other contexts. Their combination — especially for spatially-structured networks — has not.

---

## Proposed extensions (ordered by difficulty)

---

### Extension A — Batched Allocation (static, single period)

**Setting**: n players arrive simultaneously. The planner does not assign greedily one-by-one; instead it designs the full allocation treating all n players as a joint problem. This is already what Qiu et al. study. The NEW question is:

> What is the cost of batching RESTRICTIONS — e.g., when the planner must partition players into sub-batches of size at most k before assigning?

**Motivation**: In practice, refugee caseworkers process cases in weekly cohorts. School matching runs once per year. The batch size k is a policy parameter.

**Formal model**:
- Same framework as Qiu et al.
- Add: players arrive in B = ⌈n/k⌉ sequential batches of size k
- Within each batch, the planner solves the joint assignment for that batch given the current graph state
- Between batches, the graph state updates (positions fill, compositions change)

**Key questions**:
1. How does welfare degrade as k decreases (smaller batches → more myopic)?
2. Is there a threshold k*(ε, G) such that batches of size ≥ k* achieve (1−ε)-optimal?
3. For which graph classes does small k suffice?

**Conjecture**: On graphs with bounded local treewidth, there exists k* = O(poly(1/ε)) independent of n such that batches of size k* achieve a (1−ε)-PTAS. This would explain why annual school-choice cycles work nearly as well as fully coordinated assignment.

---

### Extension B — Dynamic Position Allocation (multi-period, fixed capacity)

**Setting**: T time periods. In each period t:
- A batch B_t of new players arrives (e.g., new refugees, new students)
- Some players may vacate positions (turnover rate δ per period)
- The planner assigns B_t to available vertices
- State S_t = current composition of all positions

**Welfare**: Σ_t γ^t · SW(S_t), where γ is a discount factor.

**Key insight**: Greedy myopic assignment (maximize SW(S_t) ignoring future) can be arbitrarily bad.

Example: Suppose peer effects are superadditive — a community of 10 Syrians has more than 10× the welfare of 10 singletons placed separately. A greedy planner who fills each empty slot one by one can never build the cluster. A batching planner can.

**Formal contribution**:
- Define "price of myopia" PoM = OPT / GREEDY (supremum over instances)
- Show PoM = Ω(n) for general graphs and utility functions (i.e., greedy can be n× worse)
- Show PoM = O(1) for UNIFORM utility functions on bounded-local-treewidth graphs (positive result)

This mirrors the Price of Anarchy literature (Roughgarden 2010) but for a planner's sequential decisions rather than strategic agents.

---

### Extension C — Dynamic Allocation with Endogenous Capacity

**Setting**: Extend Extension B. Now each location j has capacity c_j^t that evolves:

  c_j^{t+1} = f(welfare_j^t, c_j^t)

where f is non-decreasing in welfare (good outcomes attract more sponsors/capacity).

**Motivation** (refugee context): A city that successfully integrates a cohort receives more federal support and community sponsorships next year. A school district that experiences peer-effect failures shrinks its magnet program.

**State space**: (S_t, c^t) where S_t is composition, c^t = (c_1^t, ..., c_m^t) is capacity vector.

**The planner's tradeoff**:
- Send refugees to already-successful communities → reinforces those communities but leaves others to collapse
- Distribute evenly → avoids collapse but may not reach the critical mass needed for any community to succeed

This is a genuine tension not in the base paper.

**Formal questions**:
1. Characterize steady states: which capacity distributions (c_1*, ..., c_m*) are stable under optimal allocation?
2. When does the system converge to a "rich-get-richer" monopoly (one large community)?
3. What planner objective (welfare vs. diversity vs. stability) leads to the most efficient long-run state?

**Connection to existing theory**:
- Analogous to stochastic stability in Schelling games (Kreisel et al. 2024, Ref. 55)
- But here capacity is the dynamic variable, not the positions themselves
- The "tipping" dynamics of Schelling segregation now operate at the capacity level

---

### Extension D — Mechanism Design under Peer Effects (hardest, most novel)

**Setting**: Players are strategic and have private types. They report types to the planner to receive better positions.

**The twist**: With peer effects, a player may want to misreport not only their own preferences but also those of others they want placed nearby.

**Formal question**: Is there an incentive-compatible mechanism that achieves the PTAS of Theorem 4?

**Conjecture**: No deterministic IC mechanism achieves better than 1/2 approximation. Randomized mechanisms may do better.

This connects to the work on truthful mechanisms for combinatorial auctions and to the literature on strategyproofness in school choice (Abdulkadiroglu-Sonmez 2003).

---

## The Refugee Resettlement Application

This is the motivating application that unifies all four extensions.

**Stylized facts**:
- U.S. resettlement: Office of Refugee Resettlement assigns refugees to nine national voluntary agencies (VOLAGs), who then place refugees in local communities
- Batching: Cases are processed in weekly cohorts by each VOLAG
- Peer effects: Co-ethnic communities improve employment outcomes by 15-30% (Edin et al. 2003; Beaman 2012)
- Capacity: VOLAGs expand or contract their programs based on federal funding and local capacity — itself partially determined by community outcomes
- Matching: Annie E. Casey and the Annie DACA algorithms (Bansak et al. 2018) already predict employment outcomes, but ignore peer effects

**Data sources**:
- ORR Annual Reports (Office of Refugee Resettlement)
- WRAPS (Worldwide Refugee Admissions Processing System) — individual-level placement data
- ACS (American Community Survey) — community composition data

**Empirical contribution (if desired)**:
- Estimate the magnitude of peer effects in the refugee context
- Simulate the gain from batch vs. sequential assignment
- Estimate the capacity elasticity f(welfare, c) for VOLAGs

---

## Relationship to Feeding America analogy

The Feeding America insight (implicit in the framing): welfare is generated at the system level, not by summing independent individual assignments.

| Feeding America | Refugee/Position Allocation |
|---|---|
| Food banks are heterogeneous in what they value | Communities are heterogeneous in what refugees bring them |
| Allocation must account for complementarities across goods | Allocation must account for complementarities across co-placed refugees |
| Today's allocation affects participation (food banks exit if they always get bad allocations) | Today's allocation affects capacity (communities exit if integration outcomes are poor) |
| Batching allows coordination across complementary goods | Batching allows coordination across complementary co-placements |

The analogy is structural, not merely superficial. The key mechanism in both cases is:

> The planner internalizes system-level externalities that sequential/myopic allocation leaves on the table.

---

## Open questions (to prioritize)

1. **Tight bound on PoM (price of myopia)**: Is it polynomial in n or exponential? The answer determines whether myopic policies are recoverable.

2. **Critical batch size**: What k*(ε, G) is needed? Is it a function of the graph's local treewidth?

3. **Capacity dynamics and stability**: Under what conditions does the endogenous-capacity system have a unique stable equilibrium vs. multiple equilibria (path dependence)?

4. **Mechanism design**: What is the approximation ratio of the best IC mechanism under peer effects?

---

## Immediate next steps

- [ ] Formalize Extension A (batching restrictions) precisely — write up the model and state a clean conjecture
- [ ] Run simulations: compare myopic vs. batch assignment on synthetic planar graphs with superadditive peer effects
- [ ] Read Beaman (2012) "Social Networks and the Dynamics of Labour Market Outcomes" for empirical estimates of refugee peer effects
- [ ] Check whether Baker's approach (used in Theorem 4) extends naturally to the multi-period setting
