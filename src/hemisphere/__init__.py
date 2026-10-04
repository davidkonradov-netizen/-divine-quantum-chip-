"""
Capa de hemisferios — sitios icosaédricos con par de hemisferios T^4.

Exporta los primitivos que el resto del Kernel de Dios consume:
  - CallosumController, CommissuralServer, make_brain
  - Brain, Spec, Hemisphere, Fiber
  - RoleScheduler, FasciclePool, Placement, assign_roles, site_roles
  - SiteNode, Link, Params
  - build_topology (icosahedron), make_pki
"""

from .callosum import CallosumController, CommissuralServer, make_brain
from .cytosk8s_topology import Brain, Spec, Hemisphere, Fiber
from .roles import (
    RoleScheduler, FasciclePool, Placement, CapacityExceeded,
    ROLES, NEEDS_BRIDGED, assign_roles, site_roles, antipodal_pairs,
)
from .site_node import SiteNode, Link, Params, STABLE, RECAL, ISOLATE
from .icosahedron import build as build_topology, validate as validate_topology

__all__ = [
    "CallosumController", "CommissuralServer", "make_brain",
    "Brain", "Spec", "Hemisphere", "Fiber",
    "RoleScheduler", "FasciclePool", "Placement", "CapacityExceeded",
    "ROLES", "NEEDS_BRIDGED", "assign_roles", "site_roles", "antipodal_pairs",
    "SiteNode", "Link", "Params", "STABLE", "RECAL", "ISOLATE",
    "build_topology", "validate_topology",
]