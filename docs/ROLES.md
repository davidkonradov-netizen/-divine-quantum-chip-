# Roles — 6 capacidades en pares antípodas

## Asignación (función pura de la topología)

```python
assign = assign_roles(topo)
# {rol: [sitioA_antípoda_de_B, sitioB_antípoda_de_A]}

No requiere consenso. Todos los sitios llegan a la misma asignación desde 
icosahedron.validate().

Tolerancia a fallos

Escenario Supervivencia
1 sitio cae 6/6 capacidades vivas (la antípoda sostiene el rol)
1 sitio + 5 vecinos caen 6/6 capacidades vivas (antípoda fuera del vecindario)
2 sitios caen 60/66 pares sobreviven; solo los 6 pares antípodas apagan un rol

RoleScheduler

```python
pl = sched.place("morfogenesis")  # → Placement(role, site, path)
```

· BFS ponderado por frescura de LSA
· Excluye sitios no frescos (fresh(h) == False)
· Excluye sitios con bridged=False para roles que lo exigen (NEEDS_BRIDGED)
· Desempate determinista por nombre (_key)

FasciclePool

Reutilización de canales (origen, destino) con contadores exactos:

· acquire() → POLYMERIZING → ACTIVE
· release() idempotente → ACTIVE → IDLE cuando refs == 0
· gc() despolimeriza canales ociosos tras idle_ttl
· CapacityExceeded si refs >= cap
