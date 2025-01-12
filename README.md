# Spector
Basically, my personal assistance

## Features
- League of Legend teacher
- Love Adivisor
- (To Be Continued...)

## Structure


## Quick Start

### K8s
using [orbstack local k8s](https://docs.orbstack.dev/kubernetes/)

```bash
kubectl config use-context orbstack
kubectl create namespace spector
```

### PostgresSQL
using [helm chart](https://artifacthub.io/packages/helm/bitnami/postgresql)
```bash
helm install my-release \
  oci://registry-1.docker.io/bitnamicharts/postgresql \
  --namespace spector \
  -f k8s/values.yaml
```
Connection Info:
- Host: `my-release-postgresql.spector.svc.cluster.local:5432`
- User: postgres
- Password: spector3702

### Server
```bash
export OPENAI_API_KEY='{YOUR_OPENAI_API_KEY}'
export TAVILY_API_KEY='YOUR_TAVILY_API_KEY'
python main.py

# or
kubectl apply -f k8s/deplyment.yaml -n spector
```