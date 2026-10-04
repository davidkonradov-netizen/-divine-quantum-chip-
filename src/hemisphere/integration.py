#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
integration.py — costura entre la capa de hemisferios y el resto del Kernel.

Conecta:
  - CallosumController     (gobierno de las 169 fibras)
  - SiteNode               (mTLS + LSA firmado + histéresis de enlaces)
  - RoleScheduler          (colocación de las 6 capacidades en antípodas)
  - Allocator              (fascículos THIN/THICK persistentes, WAL)
  - HyperTorus / FractalRouter  (enrutamiento N-D)

Reglas de la costura:
  1. Cuando el CallosumController cambia su corte, el Allocator
     reconcilia sus fascículos contra las fibras cortadas.
  2. Cuando el SiteNode marca un vecino con bridged=False en su LSA,
     el RoleScheduler lo excluye de compute_peers() para roles que exigen
     el cerebro unido (morfogenesis).
  3. Cuando el Allocator libera huérfanos, se refleja en el LSA.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from allocator.allocator import Allocator, Conflict, Saturated, NoScaffold, NoQuorum
from snn_core.lif_neuron import LIFPopulation
from topology.hyper_torus import HyperTorus

from hemisphere.callosum import CallosumController, make_brain
from hemisphere.site_node import SiteNode
from hemisphere.roles import RoleScheduler, ROLES, NEEDS_BRIDGED, assign_roles


logger = logging.getLogger("hemisphere.integration")


@dataclass
class SiteContext:
    """Estado integrado de un sitio."""
    site_id: str
    site_node: SiteNode
    callosum: CallosumController
    scheduler: RoleScheduler
    allocator: Allocator
    torus: HyperTorus
    snn_population: LIFPopulation


class HemisphereOrchestrator:
    """
    Orquestador de una capa hemisphere completa: 12 sitios + allocator global.

    Uso típico:
        orch = HemisphereOrchestrator(topo, pki_dir, params)
        await orch.bootstrap()
        await orch.run_forever()
    """

    def __init__(self, topo, pki_dir, params, allocator=None, torus_dims=7):
        self.topo = topo
        self.pki_dir = pki_dir
        self.params = params
        self.sites: dict[str, SiteContext] = {}
        self.assign = assign_roles(topo)
        self.allocator = allocator or Allocator(
            caps={f"nivel-{i}": 3 ** i * 100 for i in range(torus_dims)},
            node_id="hemisphere-alloc",
        )
        self.torus = HyperTorus(dimensions=torus_dims, nodes_per_dim=3)
        self._last_cut_per_site: dict[str, frozenset] = {}

    async def bootstrap(self):
        """Arranca los 12 sitios, cada uno con su callosum y scheduler."""
        brain = make_brain()
        for site_id in self.topo["nodes"]:
            ctrl = CallosumController(site_id, brain, self.pki_dir, params=self.params)
            node = SiteNode(site_id, self.topo, self.pki_dir, params=self.params,
                            callosum=ctrl)
            sched = RoleScheduler(node, self.assign)
            snn = LIFPopulation(n_neurons=100, dimensions=3, seed=hash(site_id) & 0xFFFF)
            await node.start_server()
            self.sites[site_id] = SiteContext(
                site_id=site_id, site_node=node, callosum=ctrl,
                scheduler=sched, allocator=self.allocator,
                torus=self.torus, snn_population=snn,
            )
        eps = {s: ("127.0.0.1", ctx.site_node.port)
               for s, ctx in self.sites.items()}
        for sid, ctx in self.sites.items():
            ctx.site_node.start_probes(eps)
            ctx.callosum.start({
                d: ("127.0.0.1", ctx.site_node.port + 1 + d) for d in range(3)
            })

    # --- costura 1: callosum -> allocator ---------------------------------
    async def on_cut_change(self, site_id: str):
        """
        Cuando el callosum de un sitio cambia su corte, reconciliamos el
        allocator: los fascículos sobre fibras cortadas se liberan.
        """
        ctx = self.sites[site_id]
        cut = frozenset(f.fid for f in ctx.callosum.brain.fibers
                        if ctx.callosum.links[f.domain].state == "ISOLATE_EDGE")
        if cut == self._last_cut_per_site.get(site_id, frozenset()):
            return
        self._last_cut_per_site[site_id] = cut
        dead_l = ctx.callosum.dead_l
        dead_r = ctx.callosum.dead_r

        # Pasar al allocator como estado de hojas
        leaf_states = {}
        for i, f in enumerate(ctx.callosum.brain.fibers):
            if f.fid in cut:
                continue  # cortada → NO la reportamos como viva
            leaf_states[f"fiber-{site_id}-{f.fid}"] = {
                "source": f"hemi-L-{site_id}",
                "target": f"hemi-R-{site_id}",
                "slots": 1,
                "domain": f.domain,
                "left": f.left,
                "right": f.right,
                "left_dead": f.left in dead_l,
                "right_dead": f.right in dead_r,
            }
        released, orphans = self.allocator.reconcile(leaf_states)
        logger.info(
            "callosum→allocator[%s]: cut=%d liberados=%d huérfanos=%d",
            site_id, len(cut), len(released), len(orphans),
        )

    # --- costura 2: LSA bridged -> scheduler ------------------------------
    def scheduler_view(self, site_id: str):
        """
        Devuelve la vista del scheduler en un sitio: qué vecinos pueden recibir
        trabajo para cada rol, respetando NEEDS_BRIDGED.
        """
        ctx = self.sites[site_id]
        view = {}
        for role in ROLES:
            name = role[0]
            needs = NEEDS_BRIDGED[name]
            placement = ctx.scheduler.place(name)
            view[name] = {
                "site": placement.site if placement else None,
                "path": placement.path if placement else [],
                "needs_bridged": needs,
            }
        return view

    # --- costura 3: allocator -> LSA --------------------------------------
    async def publish_orphans(self):
        """
        Cuando el allocator libera huérfanos, se refleja inmediatamente en el
        LSA firmado del sitio afectado, para que sus vecinos lo sepan en el
        siguiente heartbeat.
        """
        for sid, ctx in self.sites.items():
            # Marca un cambio → fuerza refresh_lsa() en el próximo ciclo
            ctx.site_node.refresh_lsa()

    async def run_forever(self, poll_interval: float = 0.5):
        """Bucle de reconciliación entre capas."""
        import asyncio
        try:
            while True:
                for sid in self.sites:
                    await self.on_cut_change(sid)
                await self.publish_orphans()
                await asyncio.sleep(poll_interval)
        except asyncio.CancelledError:
            pass

    async def shutdown(self):
        for ctx in self.sites.values():
            await ctx.callosum.stop()
            await ctx.site_node.stop()