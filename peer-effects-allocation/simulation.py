"""
Simulation: price of myopia in batched position allocation with peer effects.

Compares:
  - GREEDY: assign each player one at a time to the position that maximizes
            their current marginal utility (ignores future arrivals)
  - BATCH:  receive all players at once, find near-optimal joint allocation
            via brute force (small instances) or random restarts

Welfare model (Threshold-style, as in Qiu et al. Theorem 1):
  Player i of type t gets utility 1 if >= tau same-type neighbors, else 0.
  SW = sum of individual utilities.

Graph: planar grid of size rows x cols.
"""

import itertools
import random
import numpy as np
import networkx as nx
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Player:
    id: int
    type: int   # 0 or 1


def make_grid_graph(rows: int, cols: int) -> nx.Graph:
    return nx.grid_2d_graph(rows, cols)


def utility(player: Player, position, assignment: Dict, G: nx.Graph, tau: int) -> float:
    """Threshold utility: 1 if player has >= tau same-type neighbors."""
    neighbors = list(G.neighbors(position))
    same_type_neighbors = sum(
        1 for nb in neighbors
        if nb in assignment.values()
        and next((p for p, pos in assignment.items() if pos == nb), None) is not None
        and _type_at(nb, assignment) == player.type
    )
    return 1.0 if same_type_neighbors >= tau else 0.0


def _type_at(position, assignment: Dict) -> Optional[int]:
    for player_id, pos in assignment.items():
        if pos == position:
            return player_id  # placeholder — we need player type
    return None


def social_welfare(players: List[Player], assignment: Dict[int, tuple], G: nx.Graph, tau: int) -> float:
    """Sum of utilities over all assigned players."""
    sw = 0.0
    for player in players:
        if player.id not in assignment:
            continue
        pos = assignment[player.id]
        neighbors = list(G.neighbors(pos))
        # count same-type neighbors
        pos_to_player = {v: p for p, v in assignment.items()}
        player_by_id = {p.id: p for p in players}
        same_type = sum(
            1 for nb in neighbors
            if nb in pos_to_player and player_by_id[pos_to_player[nb]].type == player.type
        )
        sw += 1.0 if same_type >= tau else 0.0
    return sw


def greedy_assign(players: List[Player], G: nx.Graph, tau: int,
                  existing: Dict[int, tuple] = None) -> Dict[int, tuple]:
    """
    Assign players one at a time. Each player goes to the available position
    that maximizes their current marginal utility (breaking ties randomly).
    """
    if existing is None:
        existing = {}
    assignment = dict(existing)
    occupied = set(assignment.values())
    available = [v for v in G.nodes() if v not in occupied]
    player_by_id = {p.id: p for p in players}

    # process players in arrival order
    for player in players:
        if not available:
            break
        best_pos = None
        best_util = -1
        random.shuffle(available)
        for pos in available:
            # tentatively assign
            tentative = dict(assignment)
            tentative[player.id] = pos
            u = _single_utility(player, pos, tentative, G, tau, player_by_id)
            if u > best_util:
                best_util = u
                best_pos = pos
        if best_pos is None:
            best_pos = available[0]
        assignment[player.id] = best_pos
        available.remove(best_pos)

    return assignment


def _single_utility(player: Player, pos, assignment: Dict[int, tuple],
                    G: nx.Graph, tau: int, player_by_id: Dict[int, Player]) -> float:
    neighbors = list(G.neighbors(pos))
    pos_to_player = {v: pid for pid, v in assignment.items()}
    same_type = sum(
        1 for nb in neighbors
        if nb in pos_to_player and player_by_id[pos_to_player[nb]].type == player.type
    )
    return 1.0 if same_type >= tau else 0.0


def random_restart_assign(players: List[Player], G: nx.Graph, tau: int,
                           n_restarts: int = 200) -> Dict[int, tuple]:
    """
    Near-optimal batch assignment via random restarts.
    Returns the assignment with the highest social welfare.
    """
    nodes = list(G.nodes())
    player_by_id = {p.id: p for p in players}
    best_sw = -1.0
    best_assignment = {}

    for _ in range(n_restarts):
        sampled_positions = random.sample(nodes, len(players))
        assignment = {p.id: pos for p, pos in zip(players, sampled_positions)}
        sw = social_welfare(players, assignment, G, tau)
        if sw > best_sw:
            best_sw = sw
            best_assignment = dict(assignment)

    return best_assignment


def simulate(rows: int, cols: int, n_players: int, type_split: float,
             tau: int, batch_size: int, n_restarts: int = 300,
             seed: int = 42) -> Dict:
    """
    Run both greedy (batch_size=1) and near-optimal batch assignment.

    Returns dict with welfare values and price of myopia.
    """
    random.seed(seed)
    np.random.seed(seed)

    G = make_grid_graph(rows, cols)
    assert n_players <= len(G.nodes()), "More players than positions"

    # generate players
    n_type0 = int(n_players * type_split)
    players = (
        [Player(id=i, type=0) for i in range(n_type0)] +
        [Player(id=i, type=1) for i in range(n_type0, n_players)]
    )
    random.shuffle(players)

    # greedy (myopic, batch_size=1)
    greedy_assignment = greedy_assign(players, G, tau)
    greedy_sw = social_welfare(players, greedy_assignment, G, tau)

    # batch near-optimal
    batch_assignment = random_restart_assign(players, G, tau, n_restarts=n_restarts)
    batch_sw = social_welfare(players, batch_assignment, G, tau)

    pom = (batch_sw / greedy_sw) if greedy_sw > 0 else float("inf")

    return {
        "rows": rows,
        "cols": cols,
        "n_players": n_players,
        "tau": tau,
        "batch_size": batch_size,
        "greedy_sw": greedy_sw,
        "batch_sw": batch_sw,
        "price_of_myopia": pom,
        "greedy_assignment": greedy_assignment,
        "batch_assignment": batch_assignment,
    }


def run_experiments():
    results = []
    configs = [
        # (rows, cols, n_players, type_split, tau)
        (4, 4, 8,  0.5, 2),
        (4, 4, 12, 0.5, 2),
        (5, 5, 16, 0.5, 2),
        (5, 5, 16, 0.5, 3),
        (5, 5, 20, 0.6, 2),
        (6, 6, 24, 0.5, 2),
    ]
    for rows, cols, n_players, split, tau in configs:
        r = simulate(rows, cols, n_players, split, tau, batch_size=n_players)
        results.append(r)
        print(
            f"Grid {rows}x{cols}, n={n_players}, tau={tau} | "
            f"greedy SW={r['greedy_sw']:.1f}, batch SW={r['batch_sw']:.1f}, "
            f"PoM={r['price_of_myopia']:.2f}x"
        )
    return results


if __name__ == "__main__":
    print("=== Price of Myopia: Greedy vs. Batch Allocation ===\n")
    run_experiments()
