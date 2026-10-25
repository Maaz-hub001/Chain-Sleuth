"""
Graph algorithms for blockchain transaction network analysis.
"""
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque


class GraphAlgorithms:
    @staticmethod
    def find_connected_components(nodes: List[str], edges: List[Tuple[str, str]]) -> List[List[str]]:
        adj = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        visited = set()
        components = []

        for node in nodes:
            if node not in visited:
                comp = []
                queue = deque([node])
                visited.add(node)
                while queue:
                    curr = queue.popleft()
                    comp.append(curr)
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(comp)
        return components

    @staticmethod
    def detect_cycles(edges: List[Tuple[str, str]]) -> List[List[str]]:
        """
        Detects directed cycles using DFS back-edge detection.
        Returns list of cycle paths.
        """
        adj = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)

        visited = {}  # 0: unvisited, 1: visiting, 2: visited
        cycles = []
        path = []

        def dfs(node):
            visited[node] = 1
            path.append(node)

            for neighbor in adj[node]:
                if visited.get(neighbor) == 1:
                    # Cycle found! Extract cycle from path
                    try:
                        idx = path.index(neighbor)
                        cycle = path[idx:] + [neighbor]
                        if cycle not in cycles and len(cycle) <= 6:
                            cycles.append(cycle)
                    except ValueError:
                        pass
                elif visited.get(neighbor) != 2:
                    dfs(neighbor)

            path.pop()
            visited[node] = 2

        all_nodes = list(adj.keys())
        for n in all_nodes:
            if visited.get(n) != 2:
                dfs(n)

        return cycles

    @staticmethod
    def find_shortest_path(start: str, end: str, edges: List[Tuple[str, str]]) -> Optional[List[str]]:
        """BFS for shortest directed path from start to end."""
        adj = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)

        queue = deque([[start]])
        visited = {start}

        while queue:
            curr_path = queue.popleft()
            node = curr_path[-1]

            if node == end:
                return curr_path

            for neighbor in adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(curr_path + [neighbor])
        return None

    @staticmethod
    def identify_hubs(
        in_degrees: Dict[str, int],
        out_degrees: Dict[str, int],
        fan_threshold: int = 3
    ) -> Tuple[List[str], List[str]]:
        """
        Identifies fan-out hubs (high out-degree, disbursement)
        and fan-in hubs (high in-degree, consolidation).
        """
        fan_out = [addr for addr, out_deg in out_degrees.items() if out_deg >= fan_threshold]
        fan_in = [addr for addr, in_deg in in_degrees.items() if in_deg >= fan_threshold]
        return fan_out, fan_in
