# Comprehensive Deployment Guide

Complete step-by-step instructions for deploying the Task Manager API to OpenShift.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Container Registry Setup](#container-registry-setup)
4. [OpenShift Cluster Setup](#openshift-cluster-setup)
5. [Application Deployment](#application-deployment)
6. [Database Deployment](#database-deployment)
7. [Pipeline Deployment](#pipeline-deployment)
8. [Verification & Testing](#verification--testing)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

| Tool | Minimum Version | Purpose |
|------|-----------------|---------|
| Git | 2.40+ | Source code management |
| Python | 3.9+ | Runtime for Flask app |
| Docker/Podman | 5.0+ | Container runtime |
| oc CLI | 4.20+ | OpenShift command-line |
| kubectl | 1.27+ | Kubernetes operations |

### Required Accounts

- **GitHub**: Source code repository (free account OK)
- **Quay.io** or **Docker Hub**: Container registry (free tier available)
- **OpenShift Sandbox** or **OKD Cluster**: For deployment

### System Requirements

- **Disk Space**: 20GB minimum
- **RAM**: 4GB minimum
- **Internet**: Required for pulling images and pushing to registry

---

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/bsteve456/Containerized-Flask-API-deployed-on-OpenShift.git
cd Containerized-Flask-API-deployed-on-OpenShift
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify activation (should show (venv) prompt)
which python
```

### Step 3: Install Dependencies

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Verify Flask installed
python -c "import flask; print(f'Flask {flask.__version__}')"
```

### Step 4: Run Application Locally

```bash
# Method 1: Flask development server (debug mode)
export FLASK_APP=app/main.py
flask run --reload

# Method 2: Direct Python execution
python app/main.py

# Server should start at: http://localhost:5000
```

### Step 5: Run Tests

```bash
# Run all unit tests
PYTHONPATH=. pytest tests/test_tasks.py -v

# Expected output:
# test_health PASSED           [ 25%]
# test_get_tasks_empty PASSED  [ 50%]
# test_create_task PASSED      [ 75%]
# test_delete_task PASSED      [100%]
```

### Step 6: Test API Endpoints

```bash
# In another terminal, test the API:

# Health check
curl http://localhost:5000/health
# Response: {"status":"healthy"}

# Get tasks (empty initially)
curl http://localhost:5000/tasks
# Response: []

# Create a task
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn OpenShift", "description": "Deploy containerized app"}'
# Response: {"id": 1, "title": "Learn OpenShift", ...}

# Get tasks (should have 1 task)
curl http://localhost:5000/tasks

# Delete task
curl -X DELETE http://localhost:5000/tasks/1
# Response: 204 No Content
```

---

## Container Registry Setup

### Choose Your Registry

| Registry | Free Tier | Public/Private | Recommendation |
|----------|-----------|----------------|-----------------|
| Quay.io | ✅ 2 private repos | Both | **Recommended** |
| Docker Hub | ✅ 1 private repo | Both | Popular |
| GitHub Container Registry | ✅ Public free | Both | Good |

### Setup Quay.io (Recommended)

1. Go to: https://quay.io/signin/
2. Sign up with GitHub (faster) or email
3. Create new organization (optional)
4. Create repository:
   - Name: `task-manager-api`
   - Visibility: Public (for this demo)
   - Click "Create Public Repository"

### Create Docker Credentials

```bash
# Login to registry
podman login quay.io
# Enter username and password when prompted

# Verify login worked
podman images  # Should show login was successful
```

---

## Container Image Build & Push

### Step 1: Build Container Image

```bash
# Navigate to project root
cd Containerized-Flask-API-deployed-on-OpenShift

# Build image with version tag
podman build -t task-manager-api:2.0 .

# Verify image built
podman images | grep task-manager-api
# Should show: localhost/task-manager-api  2.0
```

### Step 2: Tag for Registry

```bash
# Tag image for Quay.io
# Format: podman tag <local-image> <registry>/<username>/<repo>:<tag>

podman tag task-manager-api:2.0 quay.io/bsteve456/task-manager-api:2.0

# Verify tag
podman images | grep quay
```

### Step 3: Push to Registry

```bash
# Push to Quay.io
podman push quay.io/bsteve456/task-manager-api:2.0

# Expected output:
# Copying blob ...
# Copying config ...
# Writing manifest ...
# Successfully pushed image
```

### Step 4: Verify in Registry

Visit: https://quay.io/bsteve456/task-manager-api

Should see:
- Image size
- Tags (v2.0)
- Visibility (public)
- Push/pull commands

---

## OpenShift Cluster Setup

### Option 1: Free OpenShift Sandbox (Recommended)

**Sign Up for Free Sandbox:**

1. Visit: https://try.openshift.com
2. Click: "Start your sandbox for free"
3. Sign in with:
   - GitHub account (easiest), OR
   - Red Hat account
4. Accept terms
5. Wait 2-3 minutes for cluster provisioning
6. Once ready, click: "Open Console"

**Get Login Command:**

1. In OpenShift console, top-right corner
2. Click your username
3. Click "Copy login command"
4. You get:
   ```bash
   oc login --token=sha256:XXXXX --server=https://api.sandbox-m3.xxx.openshiftapps.com:6443
   ```

### Option 2: Local OKD Cluster

```bash
# If you have CRC properly configured:
crc start

# Wait for cluster startup (5-10 minutes)
crc status

# Get login info
crc console --credentials

# Login
oc login -u kubeadmin -p <password> https://api.crc.testing:6443
```

### Option 3: Cloud-Hosted OpenShift

- **AWS OpenShift Service (ROSA)**
- **Microsoft Azure Red Hat OpenShift**
- **Google Cloud Red Hat OpenShift**

Check cloud provider documentation for setup.

---

## Application Deployment

### Step 1: Create Project (Namespace)

```bash
# Ensure you're logged into OpenShift
oc whoami
# Should return: system:serviceaccount:...

# Create new project for the application
oc new-project task-manager

# Switch to project
oc project task-manager

# Verify current project
oc project
# Should show: Using project "task-manager"
```

### Step 2: Update Kubernetes Manifests

Edit `kubernetes/deployment.yaml`:

```yaml
# Find this line:
image: task-manager-api:2.0

# Replace with your registry URL:
image: quay.io/bsteve456/task-manager-api:2.0
```

**Important:** Update `bsteve456` to your Quay.io username!

### Step 3: Deploy ConfigMap

```bash
# ConfigMap stores non-sensitive configuration
oc apply -f kubernetes/configmap.yaml

# Verify
oc get configmap
# Should show: task-manager-config
```

### Step 4: Deploy Application

```bash
# Deploy Flask application
oc apply -f kubernetes/deployment.yaml

# Verify deployment created
oc get deployment
# Should show: task-manager-api

# Watch pod creation (Ctrl+C to stop)
oc get pods -w

# Expected output after ~1 minute:
# NAME                              READY   STATUS    RESTARTS
# task-manager-api-abc123-def456   1/1     Running   0
# task-manager-api-xyz789-lmn012   1/1     Running   0
```

### Step 5: Create Service

```bash
# Expose application via Service
oc apply -f kubernetes/service.yaml

# Verify service created
oc get svc
# Should show: task-manager-api

# Get service details
oc describe svc task-manager-api
```

---

## Database Deployment

### Step 1: Deploy PostgreSQL Secret

```bash
# Secret stores sensitive credentials
oc apply -f kubernetes/postgres.yaml

# Verify secret created
oc get secret postgres-secret
```

### Step 2: Wait for Database to Start

```bash
# Watch PostgreSQL pod startup
oc get pods -l app=postgres -w

# Wait until status is "Running" (2-3 minutes)
# Ctrl+C when ready

# Alternative: Wait with timeout
oc wait --for=condition=ready pod -l app=postgres --timeout=300s
# Output: pod/postgres-abc123-def456 condition met
```

### Step 3: Verify Database Connection

```bash
# Check PostgreSQL pod logs
oc logs -l app=postgres

# Should see:
# "database system is ready to accept connections"
```

### Step 4: Test Database from Flask Pod

```bash
# Get name of Flask pod
POD_NAME=$(oc get pod -l app=task-manager-api -o jsonpath='{.items[0].metadata.name}')

# Execute test in Flask pod
oc exec -it $POD_NAME -- python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database connected and tables created!')
"
```

---

## Pipeline Deployment

### Step 1: Check Tekton Installation

```bash
# Verify Tekton is installed on cluster
oc get crd | grep tekton

# Should show multiple tekton resources
# If empty, ask cluster admin to install Tekton
```

### Step 2: Create Pipeline

```bash
# Deploy Tekton pipeline and tasks
oc apply -f pipeline/pipeline.yaml

# Verify pipeline created
oc get pipeline
# Should show: task-manager-pipeline

# Check tasks
oc get task
# Should show: git-clone, run-tests, build-image
```

### Step 3: Update PipelineRun Configuration

Edit `pipeline/pipelinerun.yaml`:

```yaml
# Update registry parameter to your Quay username
- name: registry
  value: quay.io/bsteve456  # Change to your username
```

### Step 4: Create GitHub Token (Optional - for webhook)

```bash
# Generate token at: https://github.com/settings/tokens
# Scopes needed: repo, admin:repo_hook

# Create secret with token
oc create secret generic github-token \
  --from-literal=token=<your-github-token>
```

### Step 5: Execute Pipeline

```bash
# Create and run PipelineRun
oc apply -f pipeline/pipelinerun.yaml

# Verify PipelineRun started
oc get pipelinerun

# Watch pipeline execution
oc logs -f $(oc get pipelinerun -o jsonpath='{.items[0].metadata.name}')

# Detailed status
oc describe pipelinerun <pipeline-run-name>
```

---

## Verification & Testing

### Step 1: Verify All Pods Running

```bash
# List all pods in task-manager project
oc get pods

# Expected output:
# NAME                              READY   STATUS    RESTARTS   AGE
# task-manager-api-abc123-xxx       1/1     Running   0          5m
# task-manager-api-xyz789-yyy       1/1     Running   0          5m
# postgres-def456-zzz               1/1     Running   0          5m
```

### Step 2: Check Pod Logs

```bash
# Flask pod logs
oc logs -l app=task-manager-api

# PostgreSQL logs
oc logs -l app=postgres

# Check for errors (should see gunicorn startup messages)
```

### Step 3: Access Application

**Option A: Port Forward (Local Testing)**

```bash
# Forward local port to service
oc port-forward svc/task-manager-api 5000:5000

# In another terminal, test API:
curl http://localhost:5000/health
# Response: {"status":"healthy"}
```

**Option B: Get LoadBalancer IP (If available)**

```bash
# Get external IP
oc get svc task-manager-api

# If EXTERNAL-IP is assigned (not pending), use:
curl http://<EXTERNAL-IP>:5000/health
```

**Option C: Create Route (OpenShift-specific)**

```bash
# Create HTTP route
oc create route edge task-manager-api \
  --service=task-manager-api \
  --port=5000

# Get route URL
oc get route task-manager-api
# Copy the URL from HOST/PORT column

# Test via route
curl https://<route-url>/health
```

### Step 4: Test All Endpoints

```bash
# Using port-forward or route URL
BASE_URL="http://localhost:5000"  # or your route URL

# Health check
curl $BASE_URL/health

# Get empty task list
curl $BASE_URL/tasks

# Create task
curl -X POST $BASE_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Deployed to OpenShift!", "description": "Full DevOps pipeline working"}'

# Get tasks (should have 1)
curl $BASE_URL/tasks

# Delete task
curl -X DELETE $BASE_URL/tasks/1

# Verify empty again
curl $BASE_URL/tasks
```

### Step 5: Monitor Resource Usage

```bash
# Pod resource usage
oc top pod

# Node resources
oc top node

# Describe pod for detailed info
oc describe pod <pod-name>
```

---

## Troubleshooting

### Image Pull Errors

**Error:** `ImagePullBackOff` or `Failed to pull image`

**Solution:**
```bash
# Verify image exists in registry
oc get pod <pod-name> -o yaml | grep image:

# Check if image path is correct in deployment.yaml
oc describe pod <pod-name> | grep "Image:"

# If private registry, create image pull secret:
oc create secret docker-registry regcred \
  --docker-server=quay.io \
  --docker-username=<username> \
  --docker-password=<password>

# Update deployment to use secret:
oc patch deployment task-manager-api \
  -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"regcred"}]}}}}'
```

### Database Connection Fails

**Error:** `Connection refused: postgresql://postgres:...`

**Solution:**
```bash
# Verify PostgreSQL pod is running
oc get pod -l app=postgres

# Check PostgreSQL logs
oc logs -l app=postgres

# Test connectivity from Flask pod
POD=$(oc get pod -l app=task-manager-api -o jsonpath='{.items[0].metadata.name}')
oc exec -it $POD -- nc -zv postgres 5432

# If connection fails, restart PostgreSQL:
oc delete pod -l app=postgres
# Kubernetes will recreate it automatically
```

### Pods Not Starting

**Error:** `CrashLoopBackOff` or `Error`

**Solution:**
```bash
# Check pod events
oc describe pod <pod-name>

# View full logs
oc logs <pod-name> --all-containers=true

# Check environment variables
oc env pod/<pod-name>

# For common issues:
# - Wrong image: Update deployment
# - Wrong DB URL: Check DATABASE_URL in deployment
# - Permission denied: Check RBAC roles

# Redeploy if needed:
oc rollout restart deployment/task-manager-api
```

### Service Not Accessible

**Error:** `Connection refused` when accessing service

**Solution:**
```bash
# Verify service exists
oc get svc task-manager-api

# Check service endpoints
oc get endpoints task-manager-api
# Should show pod IPs

# Verify service selector
oc get svc task-manager-api -o yaml | grep -A 5 selector:

# Test connectivity within cluster
POD=$(oc get pod -l app=task-manager-api -o jsonpath='{.items[0].metadata.name}')
oc exec -it $POD -- curl http://task-manager-api:5000/health
```

### Pipeline Execution Fails

**Error:** `Failed`, `Error`, or stuck in `Pending`

**Solution:**
```bash
# View PipelineRun logs
PIPELINE_RUN=$(oc get pipelinerun -o jsonpath='{.items[0].metadata.name}')
oc logs $PIPELINE_RUN -f

# Describe PipelineRun
oc describe pipelinerun $PIPELINE_RUN

# Check individual task status
oc get taskrun

# View task logs
oc logs taskrun/<taskrun-name> -f

# Common issues:
# - Git URL wrong: Check pipeline.yaml git-clone step
# - Tests fail: Run locally with pytest first
# - Image push fails: Check registry credentials
```

### Memory or CPU Issues

**Error:** `OOMKilled` or `CpuThrottled`

**Solution:**
```bash
# Check resource usage
oc top pod

# Increase resource limits in deployment.yaml:
resources:
  requests:
    memory: "256Mi"      # Increase from 128Mi
    cpu: "200m"          # Increase from 100m
  limits:
    memory: "512Mi"      # Increase from 256Mi
    cpu: "1000m"         # Increase from 500m

# Apply updated deployment
oc apply -f kubernetes/deployment.yaml

# Rollout new version
oc rollout status deployment/task-manager-api
```

---

## Cleanup

### Delete Application

```bash
# Delete all resources in project
oc delete all --all

# Delete entire project
oc delete project task-manager
```

### Delete Container Images

```bash
# Local image
podman rmi localhost/task-manager-api:2.0

# Registry image (manual via Quay.io web UI)
```

---

## Next Steps

1. **Automate with Webhooks**: Set up GitHub webhook for automatic deployments
2. **Add Monitoring**: Deploy Prometheus/Grafana for metrics
3. **Setup Logging**: Configure ELK stack or OpenShift logging
4. **Implement Security**: Add network policies, RBAC, pod security standards
5. **Create Frontend**: Build React/Vue UI to consume API
6. **Add Authentication**: Implement OAuth2 with Keycloak

---

## Quick Reference

### Essential Commands

```bash
# Login to OpenShift
oc login --token=<token> --server=<server-url>

# View resources
oc get pods                    # List pods
oc get svc                     # List services
oc get deployment              # List deployments

# Inspect resources
oc describe pod <pod-name>
oc logs <pod-name>
oc exec -it <pod-name> -- bash

# Apply manifests
oc apply -f <file.yaml>        # Create/update resource
oc delete -f <file.yaml>       # Delete resource

# Port forward
oc port-forward svc/<svc> <local>:<remote>

# Scale deployment
oc scale deployment <name> --replicas=3

# Rollout operations
oc rollout status deployment/<name>
oc rollout restart deployment/<name>
oc rollout undo deployment/<name>
```

---

**Deployment complete! 🎉**

For additional help, refer to the main [README.md](README.md) or check [ARCHITECTURE.md](ARCHITECTURE.md) for system design details.
