## Layout
```
cdk8s-poc/
  cdk8s.yaml                # tells cdk8s to run src/main.py and emit to dist/
  requirements.txt          # python dependencies
  src/
    main.py                 # reads data/, builds charts, writes dist/<env>/<service>/manifest.yaml
    runtimes/               # 12 "common charts" to be added here
      go_worker.py            # low-level Deployment/Service rendering for Go pods
      java_worker.py          # same but tuned for Java pods
  data/
    apps.yaml               # base definition of the two services, all 96 apps to be added here
    envs/                   # all 9 envs to be added here
      dev.yaml
      prod.yaml             # per-cluster overrides (tags, replicas)
  dist/<env>/<service>/manifest.yaml        # synthesized output committed for ArgoCD consumption
  argocd/                   # all 9 clusters to be added here
    applicationset-dev.yaml     # Argo CD ApplicationSet for dev cluster
    applicationset-prod.yaml    # Argo CD ApplicationSet for prod cluster
```

## Running synth
```
pip install -r requirements.txt
cdk8s synth
```
This rewrites everything under `dist/`  
Committed YAML picked up by Argo CD  
Alternative is to use ApplicationSet plugin to run `cdk8s synth` automatically  
