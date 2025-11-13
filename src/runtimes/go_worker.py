from cdk8s import ApiObject, JsonPatch

def create_go_worker(chart, cfg):
    labels = {
        "app.kubernetes.io/name": cfg["name"],
        "app.kubernetes.io/component": "go-worker",
    }

    deployment = ApiObject(
        chart,
        f"{cfg['name']}-deployment",
        api_version="apps/v1",
        kind="Deployment",
        metadata={
            "name": cfg["name"],
            "labels": labels,
        },
    )
    deployment.add_json_patch(
        JsonPatch.add(
            "/spec",
            {
                "replicas": cfg.get("replicas", 1),
                "selector": {"matchLabels": labels},
                "template": {
                    "metadata": {"labels": labels},
                    "spec": {
                        "containers": [
                            {
                                "name": cfg["name"],
                                "image": f"{cfg['image']['repository']}:{cfg['image']['tag']}",
                                "args": cfg.get("args", []),
                                "ports": [
                                    {
                                        "containerPort": cfg.get("containerPort", 5678),
                                        "name": "http",
                                    }
                                ],
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/",
                                        "port": "http",
                                    },
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/",
                                        "port": "http",
                                    },
                                },
                            }
                        ]
                    },
                },
            },
        )
    )

    service = ApiObject(
        chart,
        f"{cfg['name']}-service",
        api_version="v1",
        kind="Service",
        metadata={
            "name": cfg["name"],
            "labels": labels,
        },
    )
    service.add_json_patch(
        JsonPatch.add(
            "/spec",
            {
                "type": cfg.get("service", {}).get("type", "ClusterIP"),
                "selector": labels,
                "ports": [
                    {
                        "name": "http",
                        "port": cfg.get("service", {}).get("port", 80),
                        "targetPort": cfg.get("service", {}).get("targetPort", cfg.get("containerPort", 5678)),
                    }
                ],
            },
        )
    )
