

```markdown
# Dos capas de fascículos (no confundir)

| Capa | Módulo | Alcance | Propósito |
|---|---|---|---|
| **Pool de sockets** | `roles.FasciclePool` | 1 proceso, memoria | Reutilizar conexiones (origen, destino) |
| **Allocator distribuido** | `allocator.Allocator` | Clúster completo, WAL | Asignar recursos persistentes con TTL |

## FasciclePool

- **Objeto**: conexión lógica entre 2 sitios.
- **Ciclo**: `POLYMERIZING → ACTIVE ↔ IDLE → (gc)`.
- **Garantías**: contadores exactos por clave, tope de capacidad, GC por idle.
- **No persistente**: si el proceso muere, el pool se pierde.

## Allocator

- **Objeto**: slots de un `deployment_id` sobre un `source` hacia un `target`.
- **Ciclo**: THIN (TTL corto, renovable por `touch`) / THICK (TTL largo, renovable por `health`).
- **Garantías**: idempotencia por `(id, spec)`, cuórum sobre réplicas, WAL con fsync,
  fencing por término de líder, reconciliación con hojas.
- **Persistente**: sobrevive reinicios, huérfanos ocupan capacidad hasta confirmación.

## Cuándo usar cada uno

- **FasciclePool** cuando la conexión es efímera y su coste es la latencia de setup.
- **Allocator** cuando la asignación es un recurso compartido y su duplicación es
  catastrófica (dos pods pensando que tienen el mismo slot).

## Referencia

- `roles.FasciclePool.acquire/release/gc`
- `allocator.Allocator.allocate/release/touch/health/reconcile`