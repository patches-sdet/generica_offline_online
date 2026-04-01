from .factory import make_ability
from .registry import register_ability, get_all_abilities
import pkgutil, importlib, os
from . import definitions, professions, races, advanced

MODULE_GROUPS = [definitions, professions, races, advanced]

definitions_path = os.path.join(os.path.dirname(__file__), "definitions")

loaded = 0

for group in MODULE_GROUPS:
    for _, module_name, _ in pkgutil.iter_modules(group.__path__):
        if module_name.startswith("_"):
            continue
        try:
            print(f"[Ability Loader] Importing {module_name}...")
            module = importlib.import_module(f"{group.__name__}.{module_name}")
            loaded += 1

        except Exception as e:
            print(f"[Ability Loader] FAILED to import {module_name}: {e}")
            
print(f"[Ability Loader] Successfully imported {loaded} modules")

from .registry import _ABILITY_REGISTRY

if not _ABILITY_REGISTRY:
    raise RuntimeError("Ability registry is empty — no abililities were registered.\n"
                       "Check definitions import path and module discovery.")
else:
    print(f"[Ability Loader] Loaded {len(_ABILITY_REGISTRY)} abilities.")

__all__ = [
    "make_ability",
    "register_ability",
    "get_all_abilities",
]