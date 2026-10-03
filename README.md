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
┌─────────────┐
│   GitHub    │  Source code repository
└──────┬──────┘
       │
       ├──→ Tekton Pipeline (CI/CD)
       │    ├─ git-clone: Clone repo
       │    ├─ run-tests: Execute pytest
       │    └─ build-image: Build & push container
       │
       └──→ OpenShift Cluster
            ├─ Flask Pod (x2 replicas)
            │  └─ Gunicorn server (4 workers)
            ├─ PostgreSQL Pod
            │  └─ Persistent storage
            └─ Service (LoadBalancer)
               └─ External access to API
```

## 🛠️ Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Runtime** | Python | 3.9 |
| **Framework** | Flask | 3.0.0 |
| **ORM** | SQLAlchemy | 2.0.54 |
| **Database** | PostgreSQL | 13 |
| **Web Server** | Gunicorn | 21.0.0 |
| **Container** | Docker/Podman | 5.4.2+ |
| **Orchestration** | Kubernetes/OpenShift | 1.27+ |
| **CI/CD** | Tekton | 0.40+ |
| **Testing** | pytest | 7.0.0 |

## 📁 Project Structure

```
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

## ☸️ Kubernetes Deployment

### Prerequisites

1. Connected OpenShift cluster with `oc` CLI configured
2. Container image pushed to accessible registry

### Deploy to OpenShift

```bash
# Create project/namespace
oc new-project task-manager

# Deploy PostgreSQL database
oc apply -f kubernetes/postgres.yaml

# Wait for PostgreSQL pod to be ready
oc wait --for=condition=ready pod -l app=postgres --timeout=300s

# Deploy Flask application
oc apply -f kubernetes/deployment.yaml
oc apply -f kubernetes/service.yaml
oc apply -f kubernetes/configmap.yaml

# Verify pods running
oc get pods -w

# Get service details
oc get svc task-manager-api
```

### Verify Deployment

```bash
# Check deployment status
oc get deployments

# Check running pods
oc get pods

# View logs from Flask pod
oc logs -f deployment/task-manager-api

# Test API through port-forward
oc port-forward svc/task-manager-api 5000:5000

# In another terminal:
curl http://localhost:5000/health
```

### Access Service

If service is LoadBalancer type:
```bash
# Get external IP
oc get svc task-manager-api
# Access via: http://<EXTERNAL-IP>:5000
```

If service is ClusterIP only:
```bash
# Use port-forward
oc port-forward svc/task-manager-api 5000:5000
# Access via: http://localhost:5000
```

## 🔄 Tekton CI/CD Pipeline

### Pipeline Components

The Tekton pipeline consists of 3 tasks:

1. **git-clone**: Clones repository from GitHub
2. **run-tests**: Runs pytest to validate code
3. **build-image**: Builds container image and pushes to registry

### Deploy Pipeline

```bash
# Apply pipeline and tasks
oc apply -f pipeline/pipeline.yaml

# Create PipelineRun to execute
oc apply -f pipeline/pipelinerun.yaml

# Watch pipeline execution
oc logs -f $(oc get pipelinerun -o jsonpath='{.items[0].metadata.name}')

# View PipelineRun status
oc get pipelinerun
oc describe pipelinerun <pipeline-run-name>
```

### Customize Pipeline

Edit `pipeline/pipeline.yaml` to:
- Change registry URL (update `quay.io/bsteve456` to your registry)
- Adjust git branch parameter
- Add additional tasks (e.g., code scanning, security checks)

## 📊 Database Setup

### PostgreSQL Container

The deployment includes PostgreSQL 13 with:
- **Database**: `task_manager`
- **User**: `postgres`
- **Password**: `postgres123`
- **Port**: 5432

Connection string:
```
postgresql://postgres:postgres123@postgres:5432/task_manager
```

### Database Initialization

Tables are automatically created on app startup via SQLAlchemy:
- `task` table with columns: id, title, description, completed, created_at

### Data Persistence

PostgreSQL deployment uses `emptyDir` volume for demo purposes. For production:

```yaml
# Replace in kubernetes/postgres.yaml for persistence:
volumes:
- name: postgres-storage
  persistentVolumeClaim:
    claimName: postgres-pvc
```

## 🌐 OpenShift Integration

### Setup Tekton Webhook (Optional)

Automatically trigger pipeline on GitHub push:

```bash
# Get EventListener route
oc get route el-github-listener

# Add webhook to GitHub repo:
# Settings → Webhooks → Add webhook
# Payload URL: https://<el-route>/
# Events: Push events
```

### Monitor Pipeline in OpenShift Console

1. Login to OpenShift console (URL from cluster)
2. Navigate to Pipelines → Pipelines
3. Select `task-manager-pipeline`
4. View execution history and logs

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
