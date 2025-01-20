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
- using [helm chart](https://artifacthub.io/packages/helm/prometheus-community/kube-prometheus-stack)
- tutorial: [Medium](https://blog.amis.com/kubernetes-operators-prometheus-3584edd72275)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

# get secret
kubectl get secret kube-prometheus-stack-grafana -n monitoring -o jsonpath="{.data.admin-user}" | base64 --decode
echo
kubectl get secret kube-prometheus-stack-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode
echo
```
- host: `kube-prometheus-stack-grafana.monitoring.svc.cluster.local`
- server port: `80`


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

# upgrade
helm upgrade --namespace spector -f k8s/postgres-values.yaml \
  my-release oci://registry-1.docker.io/bitnamicharts/postgresql
```
Connection Info:
- Host: `my-release-postgresql.spector.svc.cluster.local:5432`
- User: postgres
- Password: spector3702
- [Grafana Dashboard](https://grafana.com/grafana/dashboards/9628-postgresql-database/)

### Server
```bash
kubectl apply -f k8s/deplyment.yaml -n spector
```