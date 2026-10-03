# System Architecture & Design

Comprehensive documentation of the Task Manager API architecture, design decisions, and system components.

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Component Overview](#component-overview)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Deployment Architecture](#deployment-architecture)
6. [Kubernetes Architecture](#kubernetes-architecture)
7. [CI/CD Pipeline Architecture](#cicd-pipeline-architecture)
8. [Database Schema](#database-schema)
9. [API Specification](#api-specification)
10. [Scaling Strategy](#scaling-strategy)

---

## High-Level Architecture

### System Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INTERNET / USERS                              │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   OpenShift LoadBalancer    │
                    │     (External Service)      │
                    └──────────────┬──────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
    ┌───▼────┐               ┌─────▼──────┐           ┌─────▼──────┐
    │ Flask  │               │ Flask      │           │ Gunicorn   │
    │ Pod 1  │───────────────│ Pod 2      │────...────│ Worker 4   │
    │ (2 GB) │   Kubernetes  │ (2 GB)     │           │ (0.5 CPU)  │
    └────────┘   Network     └────────────┘           └────────────┘
                 (Service)           │
                                     ▼
                    ┌──────────────────────────┐
                    │   PostgreSQL Database    │
                    │   (Single Pod)           │
                    │   - Persistent Volume    │
                    │   - User: postgres       │
                    │   - DB: task_manager     │
                    └──────────────────────────┘

│                    OpenShift Cluster                         │
└─────────────────────────────────────────────────────────────┘
```

### GitOps Flow Diagram

```
┌─────────────────┐
│  Developer Push │
│  to GitHub      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  GitHub Webhook → Tekton EventListener
└──────────┬──────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  Tekton PipelineRun Created              │
└──────────┬───────────────────────────────┘
           │
    ┌──────┴────────┬──────────────┬─────────────┐
    │               │              │             │
    ▼               ▼              ▼             ▼
┌─────────┐   ┌──────────┐  ┌───────────┐  ┌──────────────┐
│git-clone│   │run-tests │  │build-image│  │Push to       │
│         │──▶│          │─▶│           │─▶│Quay.io/      │
│Clone    │   │Run pytest│  │Build with │  │Docker Hub    │
│Repo     │   │4 tests   │  │Buildah    │  │              │
└─────────┘   └──────────┘  └───────────┘  └──────┬───────┘
                                                   │
                                    ┌──────────────▼──────────────┐
                                    │ Redeploy with New Image     │
                                    │ (automatic via webhook)     │
                                    └─────────────────────────────┘
```

---

## Component Overview

### 1. Flask Application

**Purpose:** REST API for task management

**Key Files:**
- `app/__init__.py` - Flask app factory, database initialization
- `app/models.py` - SQLAlchemy ORM models
- `app/routes.py` - API endpoint handlers
- `app/main.py` - Application entry point

**Responsibilities:**
- ✅ Handle HTTP requests from clients
- ✅ Validate input data
- ✅ Perform CRUD operations on tasks
- ✅ Interact with PostgreSQL database
- ✅ Return JSON responses

**Dependencies:**
- Flask 3.0.0 - Web framework
- Flask-SQLAlchemy 3.1.1 - ORM integration
- Gunicorn 21.0.0 - Production web server

### 2. PostgreSQL Database

**Purpose:** Persistent data storage

**Configuration:**
- **Version:** PostgreSQL 13
- **Database Name:** task_manager
- **Default User:** postgres
- **Default Password:** postgres123
- **Port:** 5432 (internal)

**Tables:**
```sql
CREATE TABLE task (
    id INTEGER PRIMARY KEY AUTO INCREMENT,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Responsibilities:**
- ✅ Store task data persistently
- ✅ Handle concurrent access from multiple pods
- ✅ Maintain data integrity
- ✅ Provide transaction support

### 3. Gunicorn Web Server

**Purpose:** Production-grade WSGI application server

**Configuration:**
- **Bind Address:** 0.0.0.0:5000
- **Worker Processes:** 4 per pod
- **Worker Class:** sync (default)
- **Timeout:** 30 seconds
- **Keep-Alive:** 2 seconds

**Why Gunicorn instead of Flask dev server:**
- ✅ Multi-worker concurrency (handle multiple requests)
- ✅ Process management and graceful reloads
- ✅ Production-ready error handling
- ✅ Performance and stability

**Responsibilities:**
- ✅ Listen on port 5000
- ✅ Spawn multiple worker processes
- ✅ Forward requests to Flask application
- ✅ Handle errors and timeouts

### 4. Kubernetes Service

**Purpose:** Internal service discovery and external exposure

**Type:** LoadBalancer

**Spec:**
```yaml
Service: task-manager-api
  Port: 5000 (external)
  TargetPort: 5000 (container)
  Selector: app=task-manager-api
  Type: LoadBalancer
```

**Responsibilities:**
- ✅ Expose pods to internal network
- ✅ Load balance requests across pod replicas
- ✅ Provide DNS name (task-manager-api.default.svc.cluster.local)
- ✅ Handle external traffic via LoadBalancer

### 5. Docker Container

**Purpose:** Standardize application deployment

**Base Image:** python:3.9-slim
**Image Size:** ~400MB

**Layers:**
1. Base Python 3.9 runtime
2. Install production dependencies (Flask, SQLAlchemy, psycopg2, gunicorn)
3. Copy application code
4. Set environment variables
5. Expose port 5000
6. Start gunicorn

**Responsibilities:**
- ✅ Package application with all dependencies
- ✅ Ensure consistency across environments
- ✅ Enable container orchestration
- ✅ Reduce deployment time

---

## Data Flow

### Request Flow Diagram

```
1. Client Request
   │
   curl http://localhost:5000/health
   │
   ▼
2. HTTP Request reaches Service
   │
   Service (task-manager-api:5000)
   │
   ▼
3. Load Balancer distributes to Pod
   │
   ├─ Pod 1 (40% chance)
   ├─ Pod 2 (60% chance)
   │
   ▼
4. Gunicorn Worker receives request
   │
   4.1 worker 1 (available)
   4.2 worker 2 (busy)
   4.3 worker 3 (available)
   4.4 worker 4 (busy)
   │
   ▼
5. Flask Application routes request
   │
   if path == '/health':
     → health()
   elif path == '/tasks':
     → get_tasks() OR create_task()
   elif path == '/tasks/<id>':
     → delete_task()
   │
   ▼
6. Handler function executes
   │
   For GET /tasks:
   └─ Task.query.all() → Query database
   │
   ▼
7. Database Query
   │
   PostgreSQL Pod
   SELECT * FROM task;
   │
   ▼
8. Database Response
   │
   Returns: [Task1, Task2, Task3, ...]
   │
   ▼
9. Flask serializes to JSON
   │
   [{"id": 1, "title": "...", ...}, ...]
   │
   ▼
10. HTTP Response (200 OK)
    │
    Content-Type: application/json
    Response Body: [...]
    │
    ▼
11. Client receives data
```

### Database Interaction Flow

```
Flask Pod
├─ SQLAlchemy ORM Layer
│  │
│  ├─ Task.query.all()
│  ├─ Task.query.get(id)
│  ├─ db.session.add(task)
│  └─ db.session.commit()
│
└─ PostgreSQL Driver (psycopg2)
   │
   └─ Network: TCP 5432 → postgres Pod
      │
      PostgreSQL Database
      ├─ SQL Parser
      ├─ Query Optimizer
      ├─ Storage Engine
      └─ Returns result set
```

---

## Technology Stack

### Runtime & Framework

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.9 | Application runtime |
| Framework | Flask | 3.0.0 | Web framework |
| Web Server | Gunicorn | 21.0.0 | Production WSGI server |
| ORM | SQLAlchemy | 2.0.54 | Database abstraction |

### Database

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Database | PostgreSQL | 13 | Persistent storage |
| Driver | psycopg2-binary | 2.9.0 | Python PostgreSQL client |

### Container & Orchestration

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Container Runtime | Docker/Podman | 5.0+ | Container execution |
| Orchestration | Kubernetes/OpenShift | 1.27+ | Cluster management |
| CI/CD | Tekton | 0.40+ | Pipeline automation |

### Development & Testing

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Testing | pytest | 7.0.0 | Unit testing framework |
| SCM | Git | 2.40+ | Version control |
| Env Vars | python-dotenv | 0.21.0 | Configuration management |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Source Control | GitHub | Code repository & webhooks |
| Container Registry | Quay.io/Docker Hub | Image storage |
| Cloud Platform | OpenShift/OKD | Cluster hosting |

---

## Deployment Architecture

### Local Development

```
Developer Machine
├─ Python 3.9 Virtual Environment
├─ Flask dev server (localhost:5000)
├─ SQLite database (in-memory for testing)
└─ pytest test runner
```

### Containerized (Single Container)

```
Container Image (400MB)
├─ Python 3.9-slim base
├─ Dependencies (Flask, SQLAlchemy, gunicorn)
├─ Application code
└─ Configuration

Container Runtime
├─ Port: 5000
├─ Database: External PostgreSQL
└─ Volumes: (optional) Persistent storage
```

### Containerized (Docker Compose - Optional)

```
docker-compose.yml
├─ flask service (task-manager-api:2.0)
│  └─ Port: 5000
├─ postgres service
│  └─ Port: 5432
└─ Network: internal communication
```

### Kubernetes/OpenShift

```
OpenShift Cluster
│
├─ Namespace: task-manager
│
├─ Deployment: task-manager-api
│  ├─ Replicas: 2
│  ├─ Pod Template
│  │  ├─ Container: task-manager-api:2.0
│  │  ├─ Port: 5000
│  │  ├─ Resources
│  │  │  ├─ Request: 128Mi/100m
│  │  │  └─ Limit: 256Mi/500m
│  │  ├─ Environment
│  │  │  ├─ FLASK_APP=app/main.py
│  │  │  ├─ DATABASE_URL=postgresql://...
│  │  │  └─ PYTHONUNBUFFERED=1
│  │  └─ Liveness Probe: /health
│  │
│  ├─ Pod 1 (Running)
│  │  └─ Gunicorn (4 workers)
│  └─ Pod 2 (Running)
│     └─ Gunicorn (4 workers)
│
├─ Service: task-manager-api
│  ├─ Type: LoadBalancer
│  ├─ Port: 5000
│  └─ Selector: app=task-manager-api
│
├─ Deployment: postgres
│  ├─ Replicas: 1
│  └─ Pod: PostgreSQL 13
│     ├─ Port: 5432
│     └─ Volume: Storage (emptyDir or PVC)
│
├─ Secret: postgres-secret
│  ├─ POSTGRES_USER: postgres
│  ├─ POSTGRES_PASSWORD: postgres123
│  └─ POSTGRES_DB: task_manager
│
├─ ConfigMap: task-manager-config
│  ├─ FLASK_ENV: production
│  └─ LOG_LEVEL: INFO
│
└─ Tekton Pipeline
   ├─ Pipeline: task-manager-pipeline
   ├─ Task: git-clone
   ├─ Task: run-tests
   ├─ Task: build-image
   └─ PipelineRun: task-manager-pipeline-run-1
```

---

## Kubernetes Architecture

### Pod Architecture

```
Pod: task-manager-api-abc123-def456
│
├─ Container: task-manager-api
│  │
│  ├─ Image: task-manager-api:2.0
│  │
│  ├─ Process Tree
│  │  └─ gunicorn (PID 1)
│  │     ├─ worker 1
│  │     ├─ worker 2
│  │     ├─ worker 3
│  │     └─ worker 4
│  │
│  ├─ Port: 5000
│  │
│  ├─ Environment Variables
│  │  ├─ FLASK_APP=app/main.py
│  │  ├─ DATABASE_URL=postgresql://...
│  │  └─ PYTHONUNBUFFERED=1
│  │
│  ├─ Volume Mounts
│  │  └─ /app (read-only filesystem)
│  │
│  ├─ Resource Limits
│  │  ├─ Requests: 128Mi RAM, 100m CPU
│  │  └─ Limits: 256Mi RAM, 500m CPU
│  │
│  └─ Probes
│     ├─ Liveness (HTTP GET /health)
│     └─ Readiness (HTTP GET /health)
│
└─ Metadata
   ├─ Name: task-manager-api-abc123-def456
   ├─ Namespace: task-manager
   ├─ Labels: app=task-manager-api
   ├─ Annotations: ...
   └─ IP: 10.128.0.42 (cluster-internal)
```

### Replica Set Management

```
Deployment: task-manager-api
│ replicas: 2
│
└─ ReplicaSet: task-manager-api-abc123
   │
   ├─ Pod 1: task-manager-api-abc123-def456
   │  └─ Status: Running
   │
   └─ Pod 2: task-manager-api-abc123-ghi789
      └─ Status: Running

When update triggered (new image):
  Deployment creates new ReplicaSet
  ├─ ReplicaSet v2: task-manager-api-xyz789 (0 replicas)
  │
  ├─ Scale up new: Pod 1 (Running)
  ├─ Scale down old: Pod 1 (Terminating)
  │
  ├─ Scale up new: Pod 2 (Running)
  ├─ Scale down old: Pod 2 (Terminating)
  │
  └─ Old ReplicaSet: 0 replicas (kept for rollback)
```

### Service Discovery

```
Client wants to reach: task-manager-api:5000

DNS Resolution
└─ task-manager-api.task-manager.svc.cluster.local
   │
   └─ Resolves to: Cluster IP (10.96.x.x)
      │
      Service (task-manager-api)
      │
      Endpoints:
      ├─ 10.128.0.42:5000 (Pod 1)
      └─ 10.128.0.43:5000 (Pod 2)
      │
      Load Balancer (kube-proxy)
      │
      └─ Routes to available pod
         (round-robin or least connections)
```

---

## CI/CD Pipeline Architecture

### Tekton Pipeline Flow

```
GitHub Event (webhook)
│
└─ Tekton EventListener (gateway)
   │
   └─ Creates PipelineRun
      │
      ├─ Task 1: git-clone
      │  │
      │  ├─ Container: alpine/git
      │  │
      │  └─ Steps:
      │     └─ git clone https://github.com/bsteve456/...
      │        └─ git checkout $(params.revision)
      │        └─ Output: /workspace/source/*
      │
      ├─ Task 2: run-tests (runs after git-clone)
      │  │
      │  ├─ Container: python:3.9
      │  │
      │  └─ Steps:
      │     ├─ cd /workspace/source
      │     ├─ pip install -r requirements.txt
      │     ├─ PYTHONPATH=. pytest
      │     └─ Exit code 0 = success
      │
      ├─ Task 3: build-image (runs after run-tests)
      │  │
      │  ├─ Container: quay.io/buildah/stable
      │  │
      │  └─ Steps:
      │     ├─ cd /workspace/source
      │     ├─ buildah build -t $(params.registry)/task-manager-api:latest .
      │     └─ buildah push --> quay.io
      │
      └─ PipelineRun Status: Success ✅
         │
         └─ Kubernetes admission controller
            │
            └─ Auto-redeploy with new image
               (if webhook configured)
```

### Pipeline Task Dependencies

```
┌─────────────────────────────────┐
│  git-clone                      │
│  (Clone from GitHub)            │
│  Status: Depends on nothing     │
└────────────────┬────────────────┘
                 │
                 │ Output: /workspace/source/
                 ▼
┌─────────────────────────────────┐
│  run-tests                      │
│  (Run pytest)                   │
│  Status: Depends on git-clone   │
└────────────────┬────────────────┘
                 │
                 │ All tests PASS?
                 ├─ YES → continue
                 └─ NO  → FAIL pipeline
                 │
                 ▼
┌─────────────────────────────────┐
│  build-image                    │
│  (Build & push container)       │
│  Status: Depends on run-tests   │
└────────────────┬────────────────┘
                 │
                 │ Image pushed?
                 ├─ YES → SUCCESS ✅
                 └─ NO  → FAIL ❌
```

### Workspace Sharing

```
Tekton Workspaces (Shared Storage)
│
└─ source (emptyDir)
   │
   ├─ git-clone writes
   │  └─ /workspace/source/*
   │
   ├─ run-tests reads
   │  └─ /workspace/source/requirements.txt
   │  └─ /workspace/source/tests/
   │
   └─ build-image reads
      └─ /workspace/source/Dockerfile
      └─ /workspace/source/app/
```

---

## Database Schema

### Task Table

```sql
CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Entity Relationship Diagram

```
┌──────────────────────────────┐
│         task                 │
├──────────────────────────────┤
│ id (PK)          INTEGER     │ ← Auto-increment
├──────────────────────────────┤
│ title            VARCHAR(255)│ ← Required, max 255 chars
│ description      VARCHAR(500)│ ← Optional, max 500 chars
│ completed        BOOLEAN     │ ← Default: false
│ created_at       TIMESTAMP   │ ← Default: now()
└──────────────────────────────┘

Indexes:
├─ PRIMARY KEY (id)
└─ UNIQUE (None in current schema)
```

### Sample Data

```json
[
  {
    "id": 1,
    "title": "Learn OpenShift",
    "description": "Deploy containerized app to OpenShift cluster",
    "completed": false,
    "created_at": "2024-10-03T10:30:00"
  },
  {
    "id": 2,
    "title": "Setup Tekton CI/CD",
    "description": "Create automated pipeline for git→test→build→deploy",
    "completed": true,
    "created_at": "2024-10-02T14:15:00"
  }
]
```

---

## API Specification

### Endpoint: GET /health

**Purpose:** Health check endpoint

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:5000
```

**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

### Endpoint: GET /tasks

**Purpose:** Retrieve all tasks

**Request:**
```http
GET /tasks HTTP/1.1
Host: localhost:5000
Accept: application/json
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Learn Kubernetes",
    "description": "Study K8s concepts",
    "completed": false,
    "created_at": "2024-10-03T10:30:00"
  }
]
```

**Response (200 OK - Empty):**
```json
[]
```

### Endpoint: POST /tasks

**Purpose:** Create a new task

**Request:**
```http
POST /tasks HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "title": "Learn Flask",
  "description": "Build web applications",
  "completed": false
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Learn Flask",
  "description": "Build web applications",
  "completed": false,
  "created_at": "2024-10-03T10:30:00"
}
```

**Response (400 Bad Request - Missing title):**
```json
{
  "error": "Title is required"
}
```

### Endpoint: DELETE /tasks/{id}

**Purpose:** Delete a task by ID

**Request:**
```http
DELETE /tasks/1 HTTP/1.1
Host: localhost:5000
```

**Response (204 No Content):**
```
(empty body)
```

**Response (404 Not Found):**
```json
{
  "error": "Task not found"
}
```

### Error Responses

| Status | Message | Cause |
|--------|---------|-------|
| 400 | "Title is required" | POST /tasks without title |
| 404 | "Task not found" | DELETE with non-existent ID |
| 500 | Internal Server Error | Database connection failure |

---

## Scaling Strategy

### Horizontal Scaling (Replicas)

```
Current: 2 replicas
Current Load: ~10 requests/second
Current Response Time: 50ms avg

Scaling Decision Tree:
│
├─ CPU Usage > 80%?
│  └─ YES → Increase replicas
│
├─ Memory Usage > 85%?
│  └─ YES → Increase memory limits
│
└─ Request Queue > 100?
   └─ YES → Increase replicas
```

**Kubernetes HPA (Horizontal Pod Autoscaler)**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: task-manager-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: task-manager-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Vertical Scaling (Resources)

**Current Resources:**
```yaml
requests:
  memory: "128Mi"
  cpu: "100m"
limits:
  memory: "256Mi"
  cpu: "500m"
```

**For High Throughput:**
```yaml
requests:
  memory: "256Mi"
  cpu: "500m"
limits:
  memory: "512Mi"
  cpu: "1000m"
```

### Load Testing Scenarios

```
Scenario 1: Normal Load
└─ 100 requests/second
   └─ 2 replicas sufficient
   └─ Response time: 50-100ms

Scenario 2: Peak Load
└─ 500 requests/second
   └─ 5 replicas recommended
   └─ Response time: 100-200ms

Scenario 3: Max Load
└─ 1000+ requests/second
   └─ 10 replicas + database optimization needed
   └─ Consider caching strategy
   └─ Response time: 200-500ms
```

### Database Scaling

```
Current: Single PostgreSQL pod
├─ Write: ~10/sec
├─ Read: ~50/sec
└─ Max connections: 100

For Production:
├─ PostgreSQL Master (writes)
├─ PostgreSQL Replica (reads)
└─ Connection pooling (PgBouncer)
```

---

## High Availability

### Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: task-manager-api
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: task-manager-api
```

Ensures at least 1 pod always available during maintenance.

### Anti-Affinity Rules

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - task-manager-api
        topologyKey: kubernetes.io/hostname
```

Spreads pods across different nodes.

### Health Checks

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 1
```

---

## Security Considerations

### Pod Security

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
```

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: task-manager-api
spec:
  podSelector:
    matchLabels:
      app: task-manager-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: task-manager-frontend
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
```

### Secrets Management

Use Kubernetes Secrets instead of hardcoded credentials:

```bash
oc create secret generic postgres-credentials \
  --from-literal=password=<secure-password>
```

---

## Monitoring & Observability

### Metrics to Monitor

```
Application Metrics:
├─ Request Rate (requests/sec)
├─ Response Time (p50, p95, p99)
├─ Error Rate (4xx, 5xx errors)
└─ Database Query Time

Infrastructure Metrics:
├─ CPU Usage (pods, nodes)
├─ Memory Usage (pods, nodes)
├─ Network I/O (bytes in/out)
└─ Disk Usage (PersistentVolumes)

Health Checks:
├─ Pod restarts (should be 0)
├─ Pod memory errors
└─ Database connectivity
```

### Example Prometheus Queries

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Pod CPU usage
rate(container_cpu_usage_seconds_total[5m])

# Pod memory usage
container_memory_working_set_bytes
```

---

## Disaster Recovery

### Backup Strategy

```
PostgreSQL Backups:
├─ Daily full backups (retention: 30 days)
├─ Hourly incremental backups
└─ Backup location: S3 or external storage

Recovery Time Objective (RTO): 1 hour
Recovery Point Objective (RPO): 1 hour
```

### Rollback Strategy

```
Failed Deployment?
│
└─ oc rollout undo deployment/task-manager-api
   │
   ├─ Reverts to previous ReplicaSet
   ├─ Terminates bad pods
   └─ Scales up old pods
```

---

## Summary

This architecture provides:

✅ **Scalability** - Horizontal scaling via replicas  
✅ **Reliability** - Multiple replicas, health checks  
✅ **Maintainability** - Clear separation of concerns  
✅ **Observability** - Metrics and logging  
✅ **Security** - Network policies, secrets management  
✅ **Automation** - CI/CD pipeline with Tekton  

Perfect for production containerized applications! 🚀
