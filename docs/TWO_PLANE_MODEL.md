

```markdown
# Modelo de dos planos — Red vs Cómputo

## Plano de red (transporte entre sitios)

- **Qué transporta**: heartbeats mTLS, LSA firmados, ACKs.
- **Estados**: `STABLE`, `RECALIBRATING`, `ISOLATE_EDGE` (por enlace, con histéresis).
- **Uso**: `SiteNode.usable_links()` → vecinos con enlace mTLS vivo y no aislado.

## Plano de cómputo (trabajo transversal)

- **Qué transporta**: trabajo que cruza los hemisferios del sitio destino.
- **Regla**: un sitio con `bridged=False` (callosum partido) **recibe trabajo interno**
  pero **no** trabajo transversal, porque su cómputo no puede cruzar hemisferios.
- **Uso**: `SiteNode.compute_peers()` → `usable_links()` filtrado por `peer_cal[.bridged]`.

## Por qué separados

Un sitio puede tener la red perfectamente sana (los 5 enlaces mTLS STABLE)
y a la vez tener el cerebro partido (0 fibras utilizables). Aislarlo de la
red sería un error operativo: **solo debe sacarse del plano de cómputo**.

Esta separación se verifica en `test_brain_sites.py`:

```python
for n in v5_nbs:
    assert "V5" in sites[n].usable_links()       # red sana
    assert "V5" not in sites[n].compute_peers()  # fuera de cómputo transversal


Referencia 

• SiteNode.usable_links() — plano de red

• SiteNode.compute_peers() — plano de cómputo 

• test_brain_sites.py bloque "cerebro partido"