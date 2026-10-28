# Canary rollback demo (SIMULATION — local kind cluster only)

Goal: show, honestly, what "contained a bad release to 10% of traffic"
means in practice. There is no real incident here and no real payment
traffic — the "bad version" is a deliberately broken image tag you build
yourself, and the "traffic" is your own curl/load-test requests.

## Steps

1. Install Argo Rollouts in the kind cluster:
   `kubectl create namespace argo-rollouts`
   `kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/download/v1.8.0/install.yaml`
2. Apply the canary Rollout: `kubectl apply -f argocd/rollouts/canary.yaml`
3. Build a "bad" image (e.g. an API that returns 500 on /checkout) and
   tag it `shopkart-api:bad`, load it into kind:
   `kind load docker-image shopkart-api:bad`
4. Update the Rollout image to `shopkart-api:bad`. The Rollout sends 10%
   of traffic to the canary and PAUSES (see `steps` in canary.yaml).
5. Watch: `kubectl argo rollouts get rollout shopkart-canary -n shopkart`
   and send test requests — roughly 1 in 10 fails, the rest succeed.
6. Roll back before promotion: `kubectl argo rollouts undo shopkart-canary -n shopkart`
   (or `abort`). Traffic returns to 100% stable. Nothing reaches 100% bad.

## What to say in an interview

"I demonstrated a canary with a 10% first step and a manual pause, so a
bad build would only affect a tenth of requests and could be rolled back
before full promotion. In this repo it is a local demo with synthetic
requests, not a production incident — in production I would add
automated analysis (error-rate thresholds) so the rollback triggers
itself instead of waiting for a human."
