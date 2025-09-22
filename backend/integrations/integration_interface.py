import importlib
from functools import lru_cache


ENABLED_INTEGRATIONS = {
    "airtable": True,
    "notion": True,
    "hubspot": True,
}

@lru_cache()
def integration_interface(integration_name):
    """Dynamically import the integration module if it's enabled"""
    if integration_name not in ENABLED_INTEGRATIONS or not ENABLED_INTEGRATIONS[integration_name]:
        raise ValueError(f"Integration '{integration_name}' is not enabled")
    
    try:
        return importlib.import_module(f"integrations.{integration_name}")
    except ImportError:
        raise ValueError(f"Integration module for '{integration_name}' not found")