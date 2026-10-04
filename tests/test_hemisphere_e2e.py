"""Test de integración: hemisphere ↔ allocator ↔ hyper-torus."""
import asyncio, pytest
from hemisphere.icosahedron import build, validate
from hemisphere.roles import assign_roles, NEEDS_BRIDGED


def test_icosahedron_valid():
    topo = build()
    assert validate(topo) == []


def test_roles_assignment():
    topo = build()
    assign = assign_roles(topo)
    assert len(assign) == 6
    assert all(len(v) == 2 for v in assign.values())
    # 'morfogenesis' exige cerebro unido
    assert NEEDS_BRIDGED["morfogenesis"] is True
    assert NEEDS_BRIDGED["ejecutivo"] is False


def test_no_pair_of_neighbors_kills_role():
    """Un sitio + sus 5 vecinos no puede apagar ninguna capacidad."""
    from hemisphere.roles import antipodal_pairs, site_roles
    topo = build()
    assign = assign_roles(topo)
    adj = {u: set(d["neighbors"]) for u, d in topo["nodes"].items()}
    for v in topo["nodes"]:
        dead = {v} | adj[v]
        for role, hosts in assign.items():
            assert any(h not in dead for h in hosts), \
                f"rol {role} muere con {v} y sus vecinos"


if __name__ == "__main__":
    import pytest as p
    p.main([__file__, "-v"])