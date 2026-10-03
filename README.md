# Containerized Flask Task Manager API - OpenShift Deployment

A production-ready containerized Flask application with PostgreSQL database, deployed on OpenShift using Kubernetes manifests and automated Tekton CI/CD pipeline.

## 🎯 Project Overview

This project demonstrates a complete DevOps workflow:
- **Backend API**: Flask-based Task Manager with REST endpoints
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Containerization**: Docker/Podman with optimized images
- **Orchestration**: Kubernetes manifests for scalable deployment
- **CI/CD**: Tekton pipeline for automated build, test, and deploy
- **Cloud Platform**: OpenShift (OKD - open-source Kubernetes distribution)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│   GitHub Repository                                 │
│   https://github.com/bsteve456/Containerized-...   │
└──────────────────┬──────────────────────────────────┘
                   │
              ┌────▼────┐
              │ Podman   │  Build & Push
              └────┬────┘
                   │
         ┌─────────▼──────────┐
         │  GitHub Container  │  Image Storage
         │  Registry (ghcr.io)│
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────────────────┐
         │  OpenShift OKD Sandbox Cluster │
         │  duma999-dev namespace         │
         │                                │
         │  ├─ Flask Pod (1 replica)      │
         │  │  └─ Gunicorn (1 worker)    │
         │  │     └─ SQLite (in-memory)   │
         │  │                            │
         │  └─ Service (ClusterIP)        │
         │     └─ Port 5000              │
         └────────────────────────────────┘
```

## 🛠️ Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Runtime** | Python | 3.9 |
| **Framework** | Flask | 3.0.0 |
| **ORM** | SQLAlchemy | 2.0.54 |
| **Database** | SQLite (in-memory) | 3.x |
| **Web Server** | Gunicorn | 21.0.0 |
| **Container** | Podman | 5.4.2 |
| **Orchestration** | OpenShift/Kubernetes | 4.14+ |
| **Registry** | GitHub Container Registry | ghcr.io |
Containerized-Flask-API-deployed-on-OpenShift/
├── app/
│   ├── __init__.py              # Flask app factory, database init
│   ├── models.py                # SQLAlchemy Task model
│   ├── routes.py                # API endpoints (4 routes)
│   └── main.py                  # Application entry point
├── tests/
│   └── test_tasks.py            # Unit tests (4 tests, all passing)
├── kubernetes/
│   ├── deployment.yaml          # Flask Deployment (2 replicas)
│   ├── service.yaml             # LoadBalancer Service
│   ├── configmap.yaml           # Configuration settings
│   └── postgres.yaml            # PostgreSQL Deployment + Service
├── pipeline/
│   ├── pipeline.yaml            # Tekton Pipeline definition
│   ├── pipelinerun.yaml         # PipelineRun to execute pipeline
│   └── tasks/                   # Individual Tekton tasks
├── Dockerfile                   # Container image recipe
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🚀 Features

### API Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/health` | Health check | `{"status": "healthy"}` |
| GET | `/tasks` | List all tasks | `[{id, title, description, completed, created_at}]` |
| POST | `/tasks` | Create new task | Created task object |
| DELETE | `/tasks/{id}` | Delete task by ID | 204 No Content |

### Database Model

```python
Task:
  - id (Integer, Primary Key, Auto-increment)
  - title (String, Required)
  - description (String, Optional)
  - completed (Boolean, Default: False)
  - created_at (DateTime, Default: UTC now)
```

### Testing

✅ **4 Comprehensive Unit Tests:**
- `test_health` - Verifies `/health` endpoint
- `test_get_tasks_empty` - Verifies empty task list
- `test_create_task` - Verifies task creation with auto-increment ID
- `test_delete_task` - Verifies task deletion

Run tests locally:
```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest tests/test_tasks.py -v
```

## 📋 Prerequisites

### Local Development
- Python 3.9+
- pip or conda
- Git

### Docker/Container
- Docker or Podman 5.0+

### Kubernetes/OpenShift
- OpenShift cluster (OKD, cloud-hosted, or sandbox)
- `oc` CLI configured with cluster credentials
- Tekton installed on cluster

## 🔧 Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/bsteve456/Containerized-Flask-API-deployed-on-OpenShift.git
cd Containerized-Flask-API-deployed-on-OpenShift
```

### 2. Local Development Environment

```bash
# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 3. Run Locally (Development)

```bash
# Using Flask development server
export FLASK_APP=app/main.py
flask run

# Or using Python directly
python app/main.py
```

Server runs at: `http://localhost:5000`

Test health endpoint:
```bash
curl http://localhost:5000/health
```

## 🧪 Testing

### Run Unit Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests with output
PYTHONPATH=. pytest tests/test_tasks.py -v

# Expected output:
# test_health PASSED           [ 25%]
# test_get_tasks_empty PASSED  [ 50%]
# test_create_task PASSED      [ 75%]
# test_delete_task PASSED      [100%]
```

### Manual API Testing

```bash
# Health check
curl http://localhost:5000/health

# Get all tasks (empty initially)
curl http://localhost:5000/tasks

# Create a task
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn OpenShift", "description": "Complete DevOps setup"}'

# Delete a task
curl -X DELETE http://localhost:5000/tasks/1
```

## 🐳 Docker/Podman Containerization

### Build Container Image

```bash
# Build with tag 2.0
podman build -t task-manager-api:2.0 .

# Or with Docker
docker build -t task-manager-api:2.0 .
```

### Run Container Locally

```bash
# Run with PostgreSQL environment (requires postgres service)
podman run -d \
  -p 5000:5000 \
  -e DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/task_manager" \
  task-manager-api:2.0

# Or use SQLite (no external DB needed)
podman run -d \
  -p 5000:5000 \
  task-manager-api:2.0
```

### Push to Registry

```bash
# Tag for registry
podman tag task-manager-api:2.0 quay.io/bsteve456/task-manager-api:2.0

# Push to Quay.io (or your registry)
podman push quay.io/bsteve456/task-manager-api:2.0
```

## ☸️ Kubernetes Deployment to OpenShift

### Prerequisites

1. OpenShift cluster access (tested on OKD Sandbox)
2. `oc` CLI configured with cluster credentials
3. Container image pushed to GitHub Container Registry (ghcr.io)
4. GitHub PAT token for registry authentication

### Step 1: Authenticate to OpenShift

```bash
# Get login token from OpenShift console
oc login --token=<your-token> --server=https://api.rm1.0a51.p1.openshiftapps.com:6443

# Verify authentication
oc current-context
```

### Step 2: Create Registry Secret (for private images)

```bash
# Create secret for GitHub Container Registry
oc create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<github-username> \
  --docker-password=<github-pat-token> \
  --docker-email=<your-email> \
  -n duma999-dev

# Link secret to default service account
oc patch serviceaccount default -p '{"imagePullSecrets": [{"name": "ghcr-secret"}]}' -n duma999-dev
```

### Step 3: Deploy to OpenShift

```bash
# Deploy Flask application to duma999-dev namespace
oc apply -f kubernetes/configmap.yaml -n duma999-dev
oc apply -f kubernetes/deployment.yaml -n duma999-dev
oc apply -f kubernetes/service.yaml -n duma999-dev

# Verify pods running
oc get pods -n duma999-dev -w

# Get pod name
oc get pods -n duma999-dev
```

### Step 4: Verify Deployment

```bash
# Check deployment status
oc get deployment task-manager-api -n duma999-dev
oc get pods -n duma999-dev
oc describe pod <pod-name> -n duma999-dev

# View logs from Flask pod
oc logs -f deployment/task-manager-api -n duma999-dev
```

### Step 5: Test API Endpoints

```bash
# Setup port-forward (in one terminal)
oc port-forward svc/task-manager-api-service 5000:5000 -n duma999-dev

# In another terminal, test endpoints:

# Health check
curl http://localhost:5000/health
# Response: {"status":"healthy"}

# Get all tasks (empty initially)
curl http://localhost:5000/tasks
# Response: []

# Create a task
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Deploy to OpenShift","description":"Successfully running on OKD Sandbox!"}'
# Response: {"id":1,"title":"Deploy to OpenShift",...}

# Get all tasks (now with your task)
curl http://localhost:5000/tasks
# Response: [{"id":1,...}]

# Delete a task
curl -X DELETE http://localhost:5000/tasks/1
# Response: 204 No Content
```

## 🔄 CI/CD Pipeline (Tekton)

### Overview

A Tekton pipeline is included for automated build and deployment. Pipeline components:

1. **git-clone**: Clones repository from GitHub
2. **run-tests**: Runs pytest to validate code  
3. **build-image**: Builds container and pushes to ghcr.io

### Deploy Pipeline (Optional)

```bash
# Prerequisites:
# - Tekton installed on cluster
# - GitHub PAT token for accessing repo
# - ghcr.io credentials configured

# Apply pipeline definitions
oc apply -f pipeline/pipeline.yaml -n duma999-dev

# Create PipelineRun
oc apply -f pipeline/pipelinerun.yaml -n duma999-dev

# Monitor execution
oc logs -f $(oc get pipelinerun -o jsonpath='{.items[0].metadata.name}') -n duma999-dev
```

**Note**: Pipeline deployment requires Tekton to be installed and properly configured with registry credentials.

## 📊 Database Setup

### Current Implementation: In-Memory SQLite

The deployment uses **SQLite in-memory database** (`sqlite:///:memory:`) for the OKD Sandbox:

**Why in-memory?**
- OKD Sandbox doesn't support persistent volumes easily
- Container filesystem is read-only
- Single worker Gunicorn avoids data isolation issues
- Suitable for demo/testing purposes

### Database Initialization

Tables are automatically created on Flask app startup via SQLAlchemy in `app/__init__.py`:

```python
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"[WARNING] Could not initialize database: {e}")
```

Task table schema:
```sql
CREATE TABLE task (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title VARCHAR(255) NOT NULL,
  description VARCHAR(500),
  completed BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Production Database

For production deployments, use PostgreSQL:

```bash
# Deploy PostgreSQL
oc apply -f kubernetes/postgres.yaml -n duma999-dev

# Set DATABASE_URL environment variable
oc set env deployment/task-manager-api \
  DATABASE_URL="postgresql://postgres:postgres123@postgres:5432/task_manager" \
  -n duma999-dev

# Restart deployment
oc rollout restart deployment/task-manager-api -n duma999-dev
```

## 🌐 OpenShift Sandbox Details

### Cluster Information

- **Cluster**: OKD Sandbox (Red Hat Developer Sandbox)
- **API Server**: https://api.rm1.0a51.p1.openshiftapps.com:6443
- **Namespace**: `duma999-dev`
- **Status**: ✅ Active and tested

### Deployment Configuration

- **Replicas**: 1 (in-memory SQLite requires single instance)
- **Gunicorn Workers**: 1 (multiple workers cause data isolation)
- **Service Type**: ClusterIP (LoadBalancer quota exceeded in sandbox)
- **Image Registry**: GitHub Container Registry (ghcr.io)
- **Image Pull Secret**: `ghcr-secret` (required for private registry)

### Useful Commands

```bash
# View all resources
oc get all -n duma999-dev

# Watch pod status
oc get pods -n duma999-dev -w

# Stream logs
oc logs -f deployment/task-manager-api -n duma999-dev

# Exec into pod
oc exec -it <pod-name> -n duma999-dev -- /bin/bash

# Port-forward for local testing
oc port-forward svc/task-manager-api-service 5000:5000 -n duma999-dev

# Scale replicas (for PostgreSQL deployments)
oc scale deployment task-manager-api --replicas=3 -n duma999-dev
```

## 🐛 Troubleshooting

### Pod fails to start

```bash
# Check pod events
oc describe pod <pod-name>

# View logs
oc logs <pod-name>

# Common issues:
# - Image not found: Verify image name and registry
# - DATABASE_URL error: Check postgres pod is running
# - Permission denied: Check RBAC roles
```

### Database connection fails

```bash
# Verify postgres pod is running
oc get pod -l app=postgres

# Check postgres logs
oc logs -l app=postgres

# Test connectivity
oc exec -it deployment/task-manager-api -- \
  python -c "import psycopg2; print('Connection OK')"
```

### Tekton pipeline fails

```bash
# Check task logs
tkn pipelinerun logs <pipeline-run-name> -f

# View detailed PipelineRun status
oc get pipelinerun -o yaml <pipeline-run-name>

# Common issues:
# - Git clone: Check GitHub URL and credentials
# - Tests fail: Run locally first with `pytest`
# - Build fails: Verify Dockerfile and image registry access
```

## 📈 Performance & Scalability

### Current Configuration

- **Flask Replicas**: 2 (for high availability)
- **Gunicorn Workers**: 4 per pod
- **Max Requests**: ~8 concurrent (2 pods × 4 workers)
- **Resource Limits**: 256Mi memory, 500m CPU per pod

### Scale Deployment

```bash
# Increase replicas
oc scale deployment task-manager-api --replicas=5

# Or edit deployment
oc edit deployment task-manager-api
# Change: replicas: 5
```

### Monitor Resources

```bash
# Watch pod resource usage
oc top pods -l app=task-manager-api

# View metrics
oc adm top nodes
```

## 🔐 Security Considerations

For production deployment:

1. **Database Credentials**: Use OpenShift Secrets instead of hardcoded values
   ```bash
   oc create secret generic postgres-credentials \
     --from-literal=user=postgres \
     --from-literal=password=<secure-password>
   ```

2. **Image Registry**: Use private registry with authentication
   ```bash
   oc create secret docker-registry quay-credentials \
     --docker-server=quay.io \
     --docker-username=<username> \
     --docker-password=<password>
   ```

3. **Network Policies**: Restrict pod-to-pod traffic
4. **Pod Security**: Use non-root user in Dockerfile
5. **RBAC**: Apply principle of least privilege

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [OpenShift Documentation](https://docs.openshift.com/)
- [Tekton CI/CD](https://tekton.dev/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/)

## 🚀 Future Enhancements

- [ ] Add authentication & authorization (OAuth2)
- [ ] Implement task filtering and search
- [ ] Add task priority and categories
- [ ] Implement task reminders/notifications
- [ ] Create frontend UI (React/Vue)
- [ ] Add monitoring (Prometheus + Grafana)
- [ ] Setup log aggregation (ELK stack)
- [ ] Add helm charts for simplified deployment
- [ ] Implement backup/disaster recovery

## 👤 Author

**Steve B** - DevOps Engineer

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Happy Deploying! 🎉**

For questions or issues, open a GitHub issue on the repository.
