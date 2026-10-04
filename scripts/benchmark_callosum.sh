#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../src/hemisphere"

python - <<'PY'
import asyncio, tempfile, time
from pathlib import Path
from callosum import CallosumController, CommissuralServer, make_brain
from pki import make_pki
from site_node import Params

async def main():
    tmp = Path(tempfile.mkdtemp())
    ids = [f"V{i}" for i in range(1, 13)]
    make_pki(tmp, ids + [f"{i}.L" for i in ids] + [f"{i}.R" for i in ids])
    brain = make_brain()
    server = CommissuralServer("V1", tmp)
    ctrl = CallosumController("V1", brain, tmp, params=Params(interval=0.02, timeout=0.2))
    await server.start()
    ctrl.start({d: ("127.0.0.1", server.ports[d]) for d in range(3)})
    print("Fase 1: 5s sin fallas")
    await asyncio.sleep(5)
    print("  RTTs:", {d: round(l.rtt*1e3, 2) if l.rtt else None
                      for d, l in ctrl.links.items()})
    print("Fase 2: 5s con +150ms en dominio 1")
    server.fault[1] = (0.15, 0.0)
    await asyncio.sleep(5)
    print("  Estados:", {d: l.state for d, l in ctrl.links.items()})
    print("  Fibras:", ctrl.summary())
    await ctrl.stop()
    await server.stop()

asyncio.run(main())
PY