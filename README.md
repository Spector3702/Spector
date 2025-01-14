# Spector
Basically, my personal assistance

## Features
- League of Legend teacher
- Love Adivisor
- (To Be Continued...)

## Structure


## Quick Start
```bash
export OPENAI_API_KEY='{YOUR_OPENAI_API_KEY}'
export TAVILY_API_KEY='YOUR_TAVILY_API_KEY'
pip install .
run-server
```

## Production

### K8s
using [orbstack local k8s](https://docs.orbstack.dev/kubernetes/)

```bash
kubectl config use-context orbstack
kubectl create namespace spector
```

### Prometheus
using [helm chart](https://artifacthub.io/packages/helm/prometheus-community/prometheus)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/prometheus --namespace spector
```
- host: `prometheus-server.spector.svc.cluster.local`
- server port: `80`
- alertmanager port: `9093`
- PushGateway port: `9091`


### PostgresSQL
using [helm chart](https://artifacthub.io/packages/helm/bitnami/postgresql)
```bash
# get values.yaml
helm show values \ 
  oci://registry-1.docker.io/bitnamicharts/postgresql \
  --version 16.3.5 \   
  > k8s/postgres-values.yaml

# install
helm install my-release \
  oci://registry-1.docker.io/bitnamicharts/postgresql \
  --namespace spector \
  -f k8s/postgres-values.yaml
```
Connection Info:
- Host: `my-release-postgresql.spector.svc.cluster.local:5432`
- User: postgres
- Password: spector3702

### Server
```bash
kubectl apply -f k8s/deplyment.yaml -n spector
```