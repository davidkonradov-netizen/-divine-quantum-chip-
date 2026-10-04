# Cuerpo Calloso — 169 fibras, 3 dominios de falla

## Arquitectura

Cada sitio `Vn` tiene 2 hemisferios (`Vn.L` analítico, `Vn.R` asociativo) corriendo
en hosts distintos. La comunicación cruzada usa **169 fibras comisurales**, pero a
efectos de gobierno se agrupan en **3 dominios de falla** independientes:
`{domain: 0,1,2}` → 56/57/56 fibras cada uno.

## Invariantes

| Invariante | Garantía |
|---|---|
| Nunca parte el cerebro | `max_isolated = 2 de 3` |
| Corte por dominio | `_cut` es frozenset de `fid` de todas las fibras del dominio aislado |
| ACK triple | `type=ACK` ∧ `from=server_id` ∧ `seq` ∧ `dom` |
| Rechazo de CN | Certificado de otro sitio → cerrado + `rejected++` |
| Cómputo fuera del loop | `brain.components()` vía `run_in_executor` |
| Coherencia temporal | `interval` fijo: `sleep(max(0, interval - elapsed))` |

## Máquina de estados (heredada de `site_node.Link`)


STABLE ──(stress ≥ warn, up_count)──▶ RECALIBRATING
   ▲                                        │
   │                                        │ (stress ≥ isolate, up_count,
   │                                        │  can_isolate=True)
   │                                        ▼
   └──(stress < clear_warn, down_count)── ISOLATE_EDGE
                    ◀──(stress < clear_isolate, down_count)──┘



## Referencia

- `CallosumController._probe()` — sondeo asyncio por dominio
- `CallosumController.usable_fibers()` — fibras vivas
- `CallosumController.route(left_idx)` — fibra más cercana por distancia de retícula