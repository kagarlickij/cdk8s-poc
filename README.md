# cdk8s POC: Go & Java workers (Python)

This proof of concept uses [cdk8s](https://cdk8s.io/) with Python constructs to render the same two microservices as the Helm POC. Source YAML is checked in so Argo CD can sync it immediately, but the `cdk8s synth` step can be rerun to regenerate manifests after editing the Python code or data files.

## Layout
```
cdk8s-poc/
  cdk8s.yaml                # tells cdk8s to run src/main.py and emit to dist/
  requirements.txt          # python dependencies
  src/
    main.py                 # reads data/, builds charts, writes dist/<env>/<service>/manifest.yaml
    runtimes/
      go_worker.py          # low-level Deployment/Service rendering for Go pods
      java_worker.py        # same but tuned for Java pods
  data/
    apps.yaml               # base definition of the two services
    envs/
      dev.yaml
      prod.yaml             # per-cluster overrides (tags, replicas, namespaces)
  dist/<env>/<service>/manifest.yaml  # example synthesized output committed for Argo consumption
  argocd/
    applicationset.yaml     # Argo CD matrix over services × envs pointing at dist/... folders
```

## Running synth
```
cd cdk8s-poc
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cdk8s synth
```
This rewrites everything under `dist/`. Commit the updated YAML so Argo CD can pick it up or wire up an ApplicationSet plugin to run `cdk8s synth` automatically.

## Images
- **hello-go** → `hashicorp/http-echo` (`0.2.3` in dev, `0.2.2` in prod)
- **hello-java** → `tomcat` (`10.1.29-jdk17-temurin` in dev, `10.1.28-jdk17-temurin` in prod)

## Argo CD
`argocd/applicationset.yaml` creates one Application per service per environment. Update the `repoURL`, destination cluster names, and namespaces before applying. If you prefer Argo to execute `cdk8s synth`, swap the source block to use a Config Management Plugin instead of the pre-rendered `dist/` folders.
