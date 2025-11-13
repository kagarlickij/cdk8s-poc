import copy
import shutil
from pathlib import Path

import yaml
from cdk8s import App, Chart

from runtimes.go_worker import create_go_worker
from runtimes.java_worker import create_java_worker

ROOT = Path(__file__).resolve().parent.parent


def load_yaml(path):
    return yaml.safe_load(path.read_text())


def deep_merge(base, override):
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def main():
    services = load_yaml(ROOT / "data" / "apps.yaml")
    env_dir = ROOT / "data" / "envs"
    envs = {path.stem: load_yaml(path) for path in env_dir.glob("*.yaml")}

    app = App()
    chart_layout = []
    env_names = set()

    for env_name, env_cfg in envs.items():
        overrides = env_cfg.get("services", {})
        env_names.add(env_name)
        for service in services["services"]:
            merged = deep_merge(service, overrides.get(service["name"], {}))
            merged.setdefault("replicas", 1)
            merged.setdefault("service", {})
            merged.setdefault("env", [])
            chart_id = f"{env_name}-{service['name']}"
            chart = Chart(app, chart_id)
            if service["runtime"] == "go-worker":
                create_go_worker(chart, merged)
            elif service["runtime"] == "java-worker":
                create_java_worker(chart, merged)
            else:
                raise ValueError(f"Unsupported runtime: {service['runtime']}")
            chart_layout.append(
                {
                    "chart_id": chart_id,
                    "env": env_name,
                    "service": service["name"],
                }
            )

    app.synth()
    reorganize_outputs(Path(app.outdir), chart_layout, env_names)


def reorganize_outputs(outdir, layout, env_names):
    outdir = outdir.resolve()
    for env_name in env_names:
        shutil.rmtree(outdir / env_name, ignore_errors=True)

    for entry in layout:
        chart_file = outdir / f"{entry['chart_id']}.k8s.yaml"
        if not chart_file.exists():
            raise FileNotFoundError(f"Expected synth output missing: {chart_file}")
        dest_dir = outdir / entry["env"] / entry["service"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "manifest.yaml"
        dest.write_text(chart_file.read_text())
        chart_file.unlink()


if __name__ == "__main__":
    main()
