# Topología T⁴ — Hemisferio = Z² / ⟨(13,0), (-s,L)⟩ × Z_bx × Z_by

## Parámetros

| Símbolo | Significado | Default |
|---|---|---|
| `RING` | Protofilamentos por microtúbulo | 13 |
| `L` | Longitud axial | 8 |
| `bx, by` | Sección del haz (enlaces MAP) | 4×4 |
| `twist` | Torsión helicoidal 13_s | 3 |
| `chords` | Cuerdas de largo alcance | `(("a",2),("a",4),("c",3))` en R |

Total: `13 × 8 × 4 × 4 = 1664` nodos/hemisferio.

## Carriles (lanes)

- `ring` — vecino circunferencial (c ± 1)
- `plus` — axial a+1 (kinesina, feed-forward)
- `minus` — axial a−1 (dineína, recurrencia)
- `bundle` — vecino de la sección (x ± 1, y ± 1)
- `chord` — cuerda de largo alcance (small-world, tipo MAP)

## Fórmula de distancia

axial = min_{k ∈ [-2,2]} ( ring_dist(dc - k·twist, 13) + |da + k·L| )
dist  = axial + ring_dist(dx, bx) + ring_dist(dy, by)

## Referencia

- `Hemisphere.dist(u, v)` — fórmula cerrada
- `Hemisphere.bfs(u)` — verificación contra BFS
- `Hemisphere.replica(u)` — vecino en otro dominio de falla
