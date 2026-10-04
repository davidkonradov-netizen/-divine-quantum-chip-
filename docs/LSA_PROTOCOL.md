
### `docs/LSA_PROTOCOL.md`

```markdown
# Protocolo LSA — Link State Advertisement firmado (ECDSA P-256)

## Por qué firmado

Sin firma, un vecino comprometido podría anunciar estado falso de terceros
(envenenamiento de tabla de rutas). El protocolo es **origen-firmado**: cada
anuncio va firmado por la clave privada del sitio que lo origina, verificada
contra el certificado público obtenido de la CA.

## Formato del anuncio

```json
{
  "seq":     <int, 0 ≤ seq < 2^62, monótono>,
  "ts":      <int, wall-clock ms>,
  "usable":  [<site_id>, ...],  // subconjunto de la adyacencia real
  "bridged": <bool>,             // callosum.summary()["bridged"]
  "sig":     "<base64 ECDSA-SHA256 sobre lsa_bytes()>"
}

lsa_bytes() serializa {site, seq, ts, usable (sorted), bridged} con
sort_keys=True, separators=(",", ":") — canónico y determinista.

Reglas de aceptación (merge_lsa)

Un anuncio se rechaza si:

1. seq, ts no son int en [0, 2^62) (rechaza bool, str, negativos, gigantes).
2. bridged no es bool.
3. usable no es lista, o tiene duplicados, o contiene IDs no-adyacentes al origen.
4. sig no es str ≤ 200 chars.
5. ts <= cur["ts"] (no es más nuevo).
6. ts > now + lsa_skew (del futuro).
7. now - ts > lsa_ttl + lsa_skew (demasiado viejo).
8. Firma inválida con la clave pública del origen del anuncio.

Defensas contra ataques

Ataque Defensa
Alterar usable Firma cubre el payload canónico
Alterar bridged Idem
Firma de otro sitio La clave pública es la del origen, no la del emisor
Replay de anuncio viejo bien firmado ts <= cur["ts"] → descartado
Timestamp del futuro ts > now + skew → rechazado
seq enorme sin firma válida Validación de rango + firma
Anuncio sobre el propio sitio Ignorado silenciosamente
Payload tipo incorrecto Validación estricta de tipos
Flood de payload len(raw) <= len(topo_adj)

Referencia

· SiteNode.refresh_lsa() — el sitio se anuncia a sí mismo
· SiteNode.merge_lsa() — fusión con validación estricta
· SiteNode._sign/_verify() — ECDSA P-256 sobre payload canónico
· SiteNode.fresh(site) — now - lsdb[site].rx <= ttl

```