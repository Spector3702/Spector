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
kubectl apply -f docker/deplyment.yaml -n spector
```

### Server
```bash
export OPENAI_API_KEY='{YOUR_OPENAI_API_KEY}'
export TAVILY_API_KEY='YOUR_TAVILY_API_KEY'
python main.py
```