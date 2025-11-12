from cdk8s import ApiObject

def create_go_worker(chart, cfg):
    labels = {
        "app.kubernetes.io/name": cfg["name"],
        "app.kubernetes.io/component": "go-worker",
    }

    ApiObject(
        chart,
        f"{cfg['name']}-deployment",
        {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": cfg["name"],
                "labels": labels,
            },
            "spec": {
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
        },
    )

    ApiObject(
        chart,
        f"{cfg['name']}-service",
        {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": cfg["name"],
                "labels": labels,
            },
            "spec": {
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
        },
    )
