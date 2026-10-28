# ShopKart — DevOps Portfolio Simulation

> **SIMULATION — read this first.** This is a **portfolio project (self, Oct 2026 – Present)**.
> It simulates a production e-commerce platform. It is **not company employment**,
> has **no real customers, no real payments, no real production traffic, and no
> real incidents**. Anything in the original project description that sounds like
> a production event is implemented here as a **local demo** and labelled as such.
> The honest mapping is in [What is real vs simulated](#what-is-real-vs-simulated).

## What this is

A small e-commerce API (products, cart, checkout) used as a vehicle to practise
real DevOps tooling end to end: Docker, Kubernetes, GitOps with Argo CD,
blue-green and canary releases with Argo Rollouts, CI/CD with Trivy scanning,
and observability with Prometheus and Grafana. The infrastructure for AWS EKS
is written in Terraform but **not applied** (see below).

## Architecture

```mermaid
flowchart LR
    Dev[Developer] -->|git push| GH[GitHub Actions CI\npytest + Docker build + Trivy]
    GH -->|image| Reg[Container image\n(local / registry)]
    Reg -->|Argo CD syncs k8s/| K8s[Kubernetes\nShopKart API + HPA]
    K8s -->|canary / blue-green| RO[Argo Rollouts]
    K8s -->|/metrics| Prom[Prometheus\nSLO rules + alerts]
    Prom --> Graf[Grafana dashboard\n99.9% SLO target]
    TF[Terraform\nVPC + EKS, 3 AZs] -.->|defined, NOT applied| AWS[AWS — not provisioned]
```

## What each tool does, and why

| Tool | What it does here | Why |
| --- | --- | --- |
| FastAPI + pytest | The demo API + 10 tests | Something real to deploy; tests gate the pipeline |
| Docker / Compose | API image + local Prometheus + Grafana stack | Reproducible local runs |
| Kubernetes (kind locally) | Deployment, Service, HPA, Ingress | The runnable deployment target |
| Terraform | VPC + 3-AZ subnets + EKS cluster definition | Infrastructure as code, reviewable — but **not applied** (paid service) |
| Argo CD | GitOps sync of `k8s/` | Cluster state follows git, no manual kubectl deploys |
| Argo Rollouts | Blue-green + canary strategies | Safe releases: preview first, shift traffic gradually |
| GitHub Actions + Trivy | Test, build, vulnerability scan on every push | Nothing untested or unscanned ships |
| Prometheus + Grafana | `/metrics` scrape, SLO recording/alert rules, dashboard | Checkout health visible against the SLO target |

## Quick start (local, Docker Compose)

```bash
docker compose up --build
curl localhost:8000/products
curl localhost:8000/health
# Prometheus: http://localhost:9090  |  Grafana: http://localhost:3000 (default admin/admin, local demo only)
```

Run the tests:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q   # 10 tests
```

## Local Kubernetes deploy (kind) — step by step

Prerequisites: `docker`, `kind`, `kubectl`, `argo` CLI (Rollouts plugin) installed.

```bash
# 1. Cluster
kind create cluster --name shopkart

# 2. Build + load the image into kind (no registry push in this simulation)
docker build -t shopkart-api:latest .
kind load docker-image shopkart-api:latest --name shopkart

# 3. Deploy the app
kubectl apply -f k8s/
kubectl -n shopkart get pods
kubectl -n shopkart port-forward svc/shopkart-api 8000:80
curl localhost:8000/products

# 4. Argo CD (GitOps) — optional, replaces step 3 for the manifests
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
# Edit argocd/application.yaml: replace REPO_URL with this repo's real URL, then:
kubectl apply -f argocd/application.yaml

# 5. Monitoring on Kubernetes (needs a Prometheus Operator install for
#    ServiceMonitor/PrometheusRule; otherwise use the Compose stack above)
kubectl apply -f monitoring/servicemonitor.yaml -f monitoring/prometheus-rules.yaml
# Grafana dashboard: import monitoring/grafana-dashboard.json
```

## The 5x festival traffic spike — as a local simulation

There is no real festival and no real traffic spike. The demo:

```bash
# With the API reachable on localhost:8000 (Compose or port-forward):
python3 loadtest/spike.py
# Baseline: 10 workers, 100 requests. Spike: 50 workers, 500 requests (5x workers).
kubectl -n shopkart get hpa   # watch replicas rise toward maxReplicas: 10, then fall back
```

What this proves: the HPA reacts to load. What it does **not** prove: production
capacity — a laptop kind cluster is not a production load test.

## The canary rollback — as a local demo

Full steps: [`argocd/rollouts/canary-demo.md`](argocd/rollouts/canary-demo.md).
Short version: deploy a deliberately bad image, let the canary take 10% of your
own test requests at the first paused step, observe the failures, then
`kubectl argo rollouts undo` before it ever reaches 100%. There is no real
payments issue and no real incident — the "payments issue" in the original
description is represented here by a bad checkout build in a demo.

Blue-green works the same way: see `argocd/rollouts/bluegreen.yaml`
(new version runs as preview, promotion is manual).

## What is real vs simulated

| Original description claim | What exists in this repo | Honest status |
| --- | --- | --- |
| E-commerce platform, products/cart/checkout | Working FastAPI API + 10 passing tests | Real code, demo data only |
| AWS EKS across 3 availability zones | Terraform: VPC + 3-AZ subnets + EKS cluster | Defined, **NOT applied** — paid service, no credentials, Free Tier only |
| ArgoCD GitOps, blue-green + canary | Application + both Rollout strategies + demo notes | Real manifests; runnable on local kind, not on EKS |
| GitHub Actions CI/CD with Trivy | `.github/workflows/ci.yml` (test → build → Trivy) | Real workflow; runs when pushed to GitHub |
| Prometheus + Grafana observability | `/metrics` endpoint, ServiceMonitor, SLO rules, dashboard JSON | Real locally; dashboard shows demo data |
| 99.9% checkout SLO | SLO definition + recording/alert rules + dashboard target line | **Target, not a measured production SLO** |
| 5x festival traffic spike | `loadtest/spike.py` against localhost | **Local load simulation**, not a real event |
| Canary rollback containing a payments issue to 10% | Canary Rollout with 10% first step + pause + undo demo | **Local demo**, not a real incident, no real payments |

## What is deliberately NOT done

- No AWS resources provisioned, no AWS credentials anywhere, no registry push.
- No real payment processing (checkout returns `"payment": "simulated"`).
- No production SLO measurement, no incident claims, no client/employer names.
- No secrets in the repo (checked with grep before delivery).

---

## INTERVIEW SECTION — how to explain this project

### 60-second spoken explanation

> "ShopKart is a portfolio simulation I built to practise end-to-end DevOps.
> It is a small e-commerce API — products, cart and checkout — that I
> containerised with Docker and deployed on Kubernetes. GitHub Actions runs
> the tests, builds the image and scans it with Trivy, and Argo CD keeps the
> cluster in sync with git. For releases I used Argo Rollouts: blue-green for
> full previews and canary for gradual traffic shifts, so a bad build can be
> caught at ten percent and rolled back before it reaches everyone.
> Prometheus scrapes the API and Grafana shows checkout health against a
> 99.9 percent SLO target. The infrastructure for EKS across three
> availability zones is written in Terraform, but I have not applied it —
> EKS is a paid service and I work within Free Tier, so the runnable demo is
> a local kind cluster plus Docker Compose. The traffic spike and the
> canary rollback are local demos with synthetic load, not production
> events — and I will say that plainly if an interviewer asks."

### 10 likely interview questions, with honest answers

1. **"Is this a real production system?"**
   No. It is a portfolio simulation with demo data. The code, pipelines and
   manifests are real and runnable locally; there is no production traffic.
2. **"Why EKS in Terraform if you never applied it?"**
   To show I can define production-shaped infrastructure as code — VPC,
   three AZs, cluster — while being honest that provisioning it costs money
   I did not spend. The same manifests run on kind locally.
3. **"How does the canary actually protect users?"**
   The first step sends 10% of traffic to the new version and pauses. If
   error rates rise, you roll back before the 50% and 100% steps. In my demo
   I did that manually; in production I would add automated analysis on
   error rate and latency so rollback triggers itself.
4. **"What does the 99.9% SLO mean here?"**
   It is a target defined in Prometheus rules, with an alert below it — not
   a measured result. With real traffic I would burn-rate alerts over 30
   days and an error budget, not a single threshold.
5. **"How did you handle the 5x spike?"**
   I simulated 5x load locally and watched the HPA scale the Deployment
   from 2 toward 10 replicas. In production I would also pre-scale before a
   known event, load-test staging, and check database and downstream limits
   — CPU autoscaling alone does not save a database.
6. **"What does Trivy catch that tests don't?"**
   Known vulnerabilities in the image's OS packages and libraries. Tests
   prove behaviour; scanning proves the shipped artefact is not carrying
   known CVEs.
7. **"Why GitOps instead of kubectl apply in CI?"**
   Git becomes the source of truth: the cluster converges to what is
   committed, rollbacks are git reverts, and nobody needs direct cluster
   credentials in the pipeline.
8. **"Blue-green vs canary — when would you pick each?"**
   Blue-green when I want an instant, full switchback and can afford double
   capacity; canary when I want real-user signal on a small slice first,
   which is why the risky checkout change went canary in my demo.
9. **"What would you do differently in real production?"**
   Managed database with backups and failover tested, secrets in a vault
   (never in git), image promotion through environments, automated rollout
   analysis, and proper load testing in staging — none of which a local
   demo can honestly claim.
10. **"What broke while you built this, and what did you learn?"**
    The honest answer: keeping the demo truthful. It is tempting to describe
    local demos as production wins; I kept every claim mapped to what
    actually runs, because an interviewer will probe exactly that gap.

## Repository layout

```text
app/                 FastAPI demo API
tests/               pytest suite (10 tests)
Dockerfile           Pinned Python image
docker-compose.yml   Local API + Prometheus + Grafana
k8s/                 Namespace, Deployment, Service, HPA, Ingress
argocd/              Argo CD Application, blue-green + canary Rollouts, canary demo
terraform/           VPC + EKS definition — NOT APPLIED (see header comment)
.github/workflows/   CI: test -> build -> Trivy scan
monitoring/          Prometheus config/rules, ServiceMonitor, Grafana dashboard
loadtest/            5x spike simulation script (local only)
```
