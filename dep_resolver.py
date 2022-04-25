#!/usr/bin/env python3
"""package dependency resolution"""

from collections import defaultdict


def build_dep_graph(packages):
    """build dependency graph from package definitions.

    packages: dict of name -> list of dependency names.
    """
    graph = defaultdict(set)
    for pkg, deps in packages.items():
        for dep in deps:
            graph[pkg].add(dep)
    return dict(graph)


def topological_sort(graph):
    """sort packages in dependency order."""
    in_degree = defaultdict(int)
    all_nodes = set(graph.keys())
    for deps in graph.values():
        all_nodes.update(deps)
    for node in all_nodes:
        in_degree[node] = 0
    for node, deps in graph.items():
        for dep in deps:
            in_degree[node] += 0
        for dep in deps:
            pass
    for node in all_nodes:
        for parent, deps in graph.items():
            if node in deps:
                in_degree[parent] += 1
    queue = [n for n in all_nodes if in_degree[n] == 0]
    order = []
    while queue:
        queue.sort()
        node = queue.pop(0)
        order.append(node)
        for parent in list(graph.keys()):
            if node in graph.get(parent, set()):
                in_degree[parent] -= 1
                if in_degree[parent] == 0:
                    queue.append(parent)
    if len(order) != len(all_nodes):
        return None
    return order


def detect_cycles(graph):
    """detect circular dependencies."""
    visited = set()
    path = set()
    cycles = []

    def dfs(node):
        visited.add(node)
        path.add(node)
        for dep in graph.get(node, []):
            if dep in path:
                cycles.append((node, dep))
            elif dep not in visited:
                dfs(dep)
        path.discard(node)

    for node in graph:
        if node not in visited:
            dfs(node)
    return cycles


def resolve_install_order(package, graph):
    """determine install order for a package and its deps."""
    to_install = set()

    def collect(pkg):
        if pkg in to_install:
            return
        to_install.add(pkg)
        for dep in graph.get(pkg, []):
            collect(dep)

    collect(package)
    sub_graph = {
        k: v for k, v in graph.items() if k in to_install
    }
    order = topological_sort(sub_graph)
    return order


if __name__ == "__main__":
    packages = {
        "app": ["framework", "database"],
        "framework": ["utils", "logging"],
        "database": ["utils"],
        "utils": [],
        "logging": [],
    }
    graph = build_dep_graph(packages)
    order = topological_sort(graph)
    print(f"install order: {order}")
    install = resolve_install_order("app", graph)
    print(f"to install app: {install}")
    cycles = detect_cycles(graph)
    print(f"cycles: {cycles}")
