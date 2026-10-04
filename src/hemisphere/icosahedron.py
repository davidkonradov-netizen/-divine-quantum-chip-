#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
icosahedron.py — grafo del icosaedro regular con 12 vértices y 30 aristas.

Propiedades que valida:
  - 12 nodos, 30 aristas no dirigidas (60 dirigidas), grado 5 por vértice.
  - Cada vértice tiene exactamente UNA antípoda a distancia 3.
  - Diámetro = 3. Aristas = 30 = 12·5/2.

Los 12 vértices se corresponden con los 12 sitios V1..V12. Las aristas son los
5 vecinos geodésicos de cada vértice en el icosaedro.
"""
from __future__ import annotations

import itertools
import math
from collections import deque

RING = 13  # coherencia con cytosk8s_topology


def build() -> dict:
    """Construye el grafo del icosaedro etiquetado V1..V12."""
    phi = (1 + math.sqrt(5)) / 2
    verts = [
        (0, 1, phi), (0, 1, -phi), (0, -1, phi), (0, -1, -phi),
        (1, phi, 0), (1, -phi, 0), (-1, phi, 0), (-1, -phi, 0),
        (phi, 0, 1), (phi, 0, -1), (-phi, 0, 1), (-phi, 0, -1),
    ]
    ids = [f"V{i+1}" for i in range(12)]

    # Encontrar la arista de longitud mínima
    d2 = lambda a, b: sum((a[k] - b[k]) ** 2 for k in range(3))
    min_d2 = min(d2(verts[i], verts[j])
                 for i, j in itertools.combinations(range(12), 2))

    neighbors = {ids[i]: [] for i in range(12)}
    for i, j in itertools.combinations(range(12), 2):
        if abs(d2(verts[i], verts[j]) - min_d2) < 1e-9:
            neighbors[ids[i]].append(ids[j])
            neighbors[ids[j]].append(ids[i])

    def _key(v):
        return int(v[1:])

    for k in neighbors:
        neighbors[k] = sorted(neighbors[k], key=_key)

    return {
        "nodes": {
            ids[i]: {
                "neighbors": list(neighbors[ids[i]]),
                "coord": list(verts[i]),
            }
            for i in range(12)
        },
        "edges": [(a, b) for i in range(12) for a, b in
                  ((ids[i], nb) for nb in neighbors[ids[i]]) if a < b],
    }


def _bfs(adj, src):
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def validate(topo: dict) -> list:
    """Devuelve la lista de errores. [] = topología válida."""
    errs = []
    ids = list(topo.get("nodes", {}).keys())

    if len(ids) != 12:
        errs.append(f"se esperaban 12 nodos, hay {len(ids)}")
        return errs

    adj = {u: list(d["neighbors"]) for u, d in topo["nodes"].items()}

    # Grado 5
    for u in ids:
        if len(adj[u]) != 5:
            errs.append(f"{u}: grado {len(adj[u])}, esperado 5")

    # Simetría
    for u in ids:
        for v in adj[u]:
            if v not in ids:
                errs.append(f"{u}->{v}: vecino desconocido")
            elif u not in adj[v]:
                errs.append(f"{u}->{v}: sin arco reverso")

    # Sin duplicados en la lista de vecinos
    for u in ids:
        if len(set(adj[u])) != len(adj[u]):
            errs.append(f"{u}: vecinos duplicados")

    # Aristas = 30
    edges = set()
    for u in ids:
        for v in adj[u]:
            edges.add(tuple(sorted((u, v), key=lambda x: int(x[1:]))))
    if len(edges) != 30:
        errs.append(f"{len(edges)} aristas, esperadas 30")

    # Diámetro 3 y antípoda única
    for u in ids:
        d = _bfs(adj, u)
        if len(d) != 12:
            errs.append(f"{u}: grafo no conexo desde aquí")
            continue
        if max(d.values()) != 3:
            errs.append(f"{u}: diámetro {max(d.values())}, esperado 3")
        antípodas = [v for v, k in d.items() if k == 3]
        if len(antípodas) != 1:
            errs.append(f"{u}: {len(antípodas)} antípodas, esperada 1")

    return errs


if __name__ == "__main__":
    topo = build()
    errs = validate(topo)
    if errs:
        print("ERRORES:")
        for e in errs:
            print(f"  - {e}")
    else:
        print("icosaedro OK: 12 nodos, 30 aristas, grado 5, diámetro 3, "
              "1 antípoda por vértice")