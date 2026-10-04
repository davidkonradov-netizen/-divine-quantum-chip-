# Integración — 4 flujos cruzados

## Flujo 1: callosum → allocator

Cuando `CallosumController._probe` cambia el corte, `HemisphereOrchestrator.on_cut_change`
reconcilia el allocator:

```python
leaf_states = {f"fiber-{site}-{f.fid}": {...} for f in brain.fibers if f.fid not in cut}
released, orphans = allocator.reconcile(leaf_states)

Los slots sobre fibras cortadas se liberan. Los que las hojas reportan y el
control plane no conoce quedan como huérfanos (siguen ocupando capacidad
hasta confirmación de la hoja).

Flujo 2: LSA bridged → scheduler

RoleScheduler.place(role) filtra sitios con bridged=False cuando el rol
exige el cerebro unido (NEEDS_BRIDGED[role] == True).

Ejemplo: morfogénesis sobre V3 cuando V3 tiene bridged=False se coloca en
la antípoda V8, incluso aunque V3 esté a 1 salto.

Flujo 3: allocator → LSA

Cuando el allocator libera huérfanos, HemisphereOrchestrator.publish_orphans
fuerza refresh_lsa() en el sitio afectado. El siguiente heartbeat lleva el
LSA actualizado, y los vecinos lo propagan.

Flujo 4: hyper-torus ↔ mesh fractal

El HyperTorus (7D, 2187 nodos) da rutas teóricas entre sitios del icosaedro.
El mesh fractal (2,187 nodos de la red global) se mapea a los sitios del
icosaedro, y cada sitio actúa como agregador de su subárbol fractal.

Referencia

· hemisphere.integration.HemisphereOrchestrator

```

---

## 🚀 Scripts

### `scripts/run_brain_sites.sh`

```bash
#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../src/hemisphere"

echo "== Generando PKI de desarrollo =="
python -c "from pki import make_pki; \
    make_pki('./pki', [f'V{i}' for i in range(1,13)] + \
    [f'V{i}.L' for i in range(1,13)] + [f'V{i}.R' for i in range(1,13)], rogue=True)"

echo "== Ejecutando test_brain_sites.py =="
python test_brain_sites.py
```

