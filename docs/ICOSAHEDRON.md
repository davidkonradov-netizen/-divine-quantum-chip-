# Icosaedro — 12 sitios, 30 aristas, 6 pares antípodas

## Propiedades

- 12 vértices (V1..V12)
- 30 aristas no dirigidas (60 dirigidas)
- Grado 5 por vértice
- Diámetro 3
- **Cada vértice tiene exactamente 1 antípoda a distancia 3**

## Por qué importa

La antípoda es la única posición que **no está en el vecindario cerrado**
(sitio + 5 vecinos) de un vértice. Esto permite que caigan 6 vértices
consecutivos y **las 6 capacidades sigan vivas** (roles.py, test_static).

## Distribución óptima de 6 capacidades

| Capacidad | Región cerebral | Exige `bridged=True` |
|---|---|---|
| ejecutivo | Prefrontal + Broca + Hipotálamo | No |
| memoria | Hipocampo | No |
| seguridad | Amígdala + Tronco | No |
| sensorio | Tálamo + Visual + Auditiva | No |
| computo_hpc | Cerebelo + Motora | No |
| **morfogénesis** | **Límbico** | **Sí** |

## Referencia

- `icosahedron.build()` — genera el grafo
- `icosahedron.validate()` — valida las propiedades
