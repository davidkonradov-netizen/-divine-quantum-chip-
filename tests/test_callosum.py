"""Tests aislados de invariantes del callosum."""
import asyncio, tempfile, random
from pathlib import Path
import pytest

from hemisphere.callosum import CallosumController, CommissuralServer, make_brain
from hemisphere.pki import make_pki
from hemisphere.site_node import Params, ISOLATE


@pytest.mark.asyncio
async def test_never_splits_brain():
    """Con 3 dominios y max_isolated=2, nunca se aísla el último."""
    tmp = Path(tempfile.mkdtemp())
    ids = [f"V{i}" for i in range(1, 13)]
    make_pki(tmp, ids + [f"{i}.L" for i in ids] + [f"{i}.R" for i in ids])
    brain = make_brain()
    p = Params(interval=0.05, timeout=0.4, max_isolated=2)
    server = CommissuralServer("V3", tmp, interval=p.interval)
    ctrl = CallosumController("V3", brain, tmp, params=p)
    await server.start()
    ctrl.start({d: ("127.0.0.1", server.ports[d]) for d in range(3)})
    try:
        # Forzar las 3 rutas degradadas
        for d in range(3):
            server.fault[d] = (0.15, 0.0)
        await asyncio.sleep(2)
        # Solo 2 pueden aislarse
        assert len(ctrl.isolated_domains()) <= 2
        assert ctrl.summary()["bridged"] is True
    finally:
        await ctrl.stop()
        await server.stop()


@pytest.mark.asyncio
async def test_cut_by_domain_not_by_fiber():
    """El corte es por dominio completo, no por fibra suelta."""
    tmp = Path(tempfile.mkdtemp())
    ids = [f"V{i}" for i in range(1, 13)]
    make_pki(tmp, ids + [f"{i}.L" for i in ids] + [f"{i}.R" for i in ids])
    brain = make_brain()
    p = Params(interval=0.05, timeout=0.4)
    server = CommissuralServer("V3", tmp, interval=p.interval)
    ctrl = CallosumController("V3", brain, tmp, params=p)
    await server.start()
    ctrl.start({d: ("127.0.0.1", server.ports[d]) for d in range(3)})
    try:
        server.fault[1] = (0.15, 0.0)
        await asyncio.sleep(3)
        per_dom = [sum(f.domain == d for f in brain.fibers) for d in range(3)]
        assert ctrl.summary()["fibers"] == 169 - per_dom[1]
    finally:
        await ctrl.stop()
        await server.stop()