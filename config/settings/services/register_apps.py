import importlib
import os

from fastapi import APIRouter


def register_apps(app, app_directory="apps"):
    """
    Register routers from all subdirectories with automatic versioning support.

    Discovers routers from:
    - {app_name}.api.v1.routers (as v1_router)
    - {app_name}.api.v2.routers (as v2_router)

    Raises:
        RuntimeError: If a version module exists but doesn't export the required router
    """
    for app_name in os.listdir(app_directory):
        app_path = os.path.join(app_directory, app_name)
        if os.path.isdir(app_path) and not app_name.startswith("__"):
            # Try to import versioned routers
            for version in ["v1", "v2", "v3"]:  # Add versions as needed
                try:
                    module = importlib.import_module(
                        f"{app_name}.api.{version}.routers"
                    )

                    # Look for versioned router (e.g., v1_router)
                    version_router_name = f"{version}_router"
                    if hasattr(module, version_router_name):
                        router = getattr(module, version_router_name)
                        if isinstance(router, APIRouter):
                            app.include_router(router)
                            print(f"✓ Registered {app_name}.{version}")
                        else:
                            raise RuntimeError(
                                f"✗ {app_name}.api.{version}.routers.{version_router_name} "
                                f"exists but is not an APIRouter instance"
                            )
                    else:
                        raise RuntimeError(
                            f"✗ {app_name}.api.{version}.routers must export '{version_router_name}'. "
                            f"Add this to {app_name}/api/{version}/routers/__init__.py:\n"
                            f"  {version_router_name} = APIRouter(prefix='/{version}/...')\n"
                            f"  __all__ = ['{version_router_name}']"
                        )

                except ModuleNotFoundError:
                    # Version doesn't exist, skip silently
                    continue
                except RuntimeError:
                    # Re-raise our custom errors
                    raise
                except Exception as e:
                    raise RuntimeError(
                        f"✗ Error loading {app_name}.{version}: {e}"
                    ) from e
