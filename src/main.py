import copy
import yaml
from pathlib import Path
from cdk8s import App, Chart, ChartProps
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

    for env_name, env_cfg in envs.items():
        namespace = env_cfg.get("namespace", "default")
        overrides = env_cfg.get("services", {})
        for service in services["services"]:
            merged = deep_merge(service, overrides.get(service["name"], {}))
            merged.setdefault("replicas", 1)
            merged.setdefault("service", {})
            merged.setdefault("env", [])
            chart = Chart(
                app,
                f"{env_name}-{service['name']}",
                ChartProps(
                    namespace=namespace,
                    output_file=f"{env_name}/{service['name']}/manifest.yaml",
                ),
            )
            if service["runtime"] == "go-worker":
                create_go_worker(chart, merged)
            elif service["runtime"] == "java-worker":
                create_java_worker(chart, merged)
            else:
                raise ValueError(f"Unsupported runtime: {service['runtime']}")

    app.synth()


if __name__ == "__main__":
    main()
