from pathlib import Path


def get_weights_path(base_path, kind, version="1.0.0"):
    return str(Path(base_path) / f"weights_{kind}_v{version}.pb")
