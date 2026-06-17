import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

np.random.seed(42)

# -----------------------------
# 1. Generate network
# -----------------------------
def generate_network(n=100, p=0.05):
    G = nx.erdos_renyi_graph(n, p)
    G = nx.convert_node_labels_to_integers(G)
    return G

# -----------------------------
# 2. Assign heterogeneous influence
# -----------------------------
def assign_influence(G):
    # Lognormal heterogeneity (heavy-tailed influence)
    alpha = {i: np.random.lognormal(mean=0, sigma=1) for i in G.nodes()}
    return alpha

# -----------------------------
# 3. Diffusion simulation
# -----------------------------
def simulate_diffusion(G, seeds, alpha, q=0.1, T=5):
    informed = set(seeds)
    newly_informed = set(seeds)

    for t in range(T):
        next_new = set()

        for j in newly_informed:
            for i in G.neighbors(j):
                if i not in informed:
                    prob = q * alpha[j]
                    if np.random.rand() < prob:
                        next_new.add(i)

        informed.update(next_new)
        newly_informed = next_new

    return len(informed) / G.number_of_nodes()


# -----------------------------
# 4. Centrality measures
# -----------------------------
def compute_centralities(G):
    degree = dict(G.degree())
    eigen = nx.eigenvector_centrality_numpy(G)

    # Diffusion centrality approximation
    A = nx.to_numpy_array(G)
    q = 1 / max(np.linalg.eigvals(A).real)
    T = 5

    DC = np.zeros(len(G))
    M = q * A
    current = np.eye(len(G))

    for t in range(1, T + 1):
        current = current @ M
        DC += current.sum(axis=1)

    diffusion = {i: DC[i] for i in range(len(G))}

    return degree, eigen, diffusion


# -----------------------------
# 5. Run experiment
# -----------------------------
def run_experiment(n_runs=50):
    results = []

    for _ in range(n_runs):
        G = generate_network()
        alpha = assign_influence(G)

        degree, eigen, diffusion = compute_centralities(G)

        for node in G.nodes():
            adoption = simulate_diffusion(G, seeds=[node], alpha=alpha)

            results.append({
                "degree": degree[node],
                "eigen": eigen[node],
                "diffusion": diffusion[node],
                "adoption": adoption
            })

    return results


# -----------------------------
# 6. Plotting
# -----------------------------
def plot_results(results):
    degree = [r["degree"] for r in results]
    eigen = [r["eigen"] for r in results]
    diffusion = [r["diffusion"] for r in results]
    adoption = [r["adoption"] for r in results]

    plt.figure()
    plt.scatter(degree, adoption)
    plt.xlabel("Degree")
    plt.ylabel("Final Adoption")
    plt.title("Adoption vs Degree")

    plt.figure()
    plt.scatter(eigen, adoption)
    plt.xlabel("Eigenvector Centrality")
    plt.ylabel("Final Adoption")
    plt.title("Adoption vs Eigenvector Centrality")

    plt.figure()
    plt.scatter(diffusion, adoption)
    plt.xlabel("Diffusion Centrality")
    plt.ylabel("Final Adoption")
    plt.title("Adoption vs Diffusion Centrality")

    plt.show()


# -----------------------------
# 7. Run everything
# -----------------------------
if __name__ == "__main__":
    results = run_experiment(n_runs=50)
    plot_results(results)