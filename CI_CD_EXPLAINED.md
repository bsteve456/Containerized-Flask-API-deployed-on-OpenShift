# CI/CD Pipeline Explained

Comprehensive guide to understanding and managing the Tekton CI/CD pipeline for automated testing, building, and deployment.

## Table of Contents

1. [CI/CD Concepts](#cicd-concepts)
2. [Pipeline Overview](#pipeline-overview)
3. [Pipeline Components](#pipeline-components)
4. [Task Breakdown](#task-breakdown)
5. [Execution Flow](#execution-flow)
6. [Configuration & Customization](#configuration--customization)
7. [Monitoring & Debugging](#monitoring--debugging)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## CI/CD Concepts

### What is CI/CD?

**Continuous Integration (CI):**
- Automatically run tests when code changes
- Catch bugs early in development
- Ensure code quality standards

**Continuous Deployment (CD):**
- Automatically deploy tested code to production
- Eliminate manual deployments
- Enable rapid feature releases

### Benefits of CI/CD Pipeline

```
Traditional Workflow:
Developer → Manual testing → Manual build → Manual deploy
             (1-2 hours)   (error-prone)   (risky)

CI/CD Workflow:
Developer → Automatic test → Automatic build → Automatic deploy
(Git push)  (1 min)         (2 min)           (automated)
            ✅ Consistent    ✅ Reliable       ✅ Safe
```

### Why Tekton?

| Feature | Tekton | Jenkins | GitLab CI |
|---------|--------|---------|-----------|
| **Kubernetes Native** | ✅ Yes | ❌ No | ❌ No |
| **Serverless** | ✅ Yes | ❌ No | ❌ No |
| **Container-based** | ✅ Yes | ⚠️ Plugin | ✅ Yes |
| **Easy Setup** | ✅ Yes | ❌ Complex | ⚠️ SaaS |
| **Cost** | ✅ Free | ✅ Free | ⚠️ Paid |

---

## Pipeline Overview

### Our Pipeline: task-manager-pipeline

```
┌────────────────────────────────────────────────────────────┐
│  Task Manager CI/CD Pipeline (task-manager-pipeline)       │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  GitHub Push Event                                          │
│  └─ webhook/commit trigger                                 │
│                                                              │
│  ┌─ Task 1: git-clone (1 minute)                           │
│  │ └─ Clone repo from GitHub                               │
│  │ └─ Output: source code in workspace                     │
│  │                                                          │
│  └─ Task 2: run-tests (2 minutes)                          │
│     └─ Run 4 unit tests                                    │
│     └─ Validate code quality                              │
│     └─ Fail pipeline if tests fail                        │
│                                                            │
│  └─ Task 3: build-image (3 minutes)                        │
│     └─ Build Docker image from Dockerfile                │
│     └─ Push to Quay.io registry                           │
│     └─ Tag with commit SHA                                │
│                                                            │
│  └─ Auto Redeploy (optional)                              │
│     └─ Update Kubernetes deployment                       │
│     └─ Rollout new pods with new image                   │
│                                                            │
│  Total Runtime: ~6 minutes ⏱️                              │
│  Success Rate Target: 95%+ ✅                              │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Pipeline Triggers

```
Trigger 1: GitHub Push (Webhook)
│
├─ Developer pushes to main branch
├─ GitHub sends webhook to Tekton
└─ PipelineRun automatically created
   └─ No manual action needed ✅

Trigger 2: Manual Execution
│
├─ Admin runs: oc apply -f pipeline/pipelinerun.yaml
├─ Or: tkn pipeline start task-manager-pipeline
└─ PipelineRun starts immediately

Trigger 3: Scheduled (Optional)
│
├─ Cron job at 2 AM daily
├─ Test codebase on schedule
└─ Catch regression issues
```

---

## Pipeline Components

### 1. Pipeline Definition (pipeline.yaml)

```yaml
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: task-manager-pipeline
spec:
  # Input parameters (can be overridden at runtime)
  params:
  - name: git-revision
    type: string
    default: main
  - name: registry
    type: string
    default: quay.io/bsteve456

  # Shared storage between tasks
  workspaces:
  - name: source

  # Tasks to execute
  tasks:
  - name: clone-repo
    taskRef:
      name: git-clone
    params:
    - name: revision
      value: $(params.git-revision)
    workspaces:
    - name: source
      workspace: source

  - name: test-code
    taskRef:
      name: run-tests
    runAfter:
    - clone-repo
    workspaces:
    - name: source
      workspace: source

  - name: build-push-image
    taskRef:
      name: build-image
    runAfter:
    - test-code
    params:
    - name: registry
      value: $(params.registry)
    workspaces:
    - name: source
      workspace: source
```

**Key Concepts:**
- `params` - Input variables (like function arguments)
- `workspaces` - Shared storage between tasks
- `tasks` - List of tasks to execute
- `runAfter` - Task dependencies (what runs first)

### 2. Task Definitions (pipeline/tasks/)

Each Task is a reusable unit of work:

**git-clone Task:**
```yaml
metadata:
  name: git-clone
spec:
  params:
  - name: revision
    type: string
    default: main
  workspaces:
  - name: source
  steps:
  - name: clone
    image: alpine/git:latest
    script: |
      git clone <repo-url> /workspace/source
      cd /workspace/source
      git checkout $(params.revision)
```

**run-tests Task:**
```yaml
metadata:
  name: run-tests
spec:
  workspaces:
  - name: source
  steps:
  - name: test
    image: python:3.9
    script: |
      cd /workspace/source
      pip install -r requirements.txt
      PYTHONPATH=. pytest
```

**build-image Task:**
```yaml
metadata:
  name: build-image
spec:
  params:
  - name: registry
    type: string
  workspaces:
  - name: source
  steps:
  - name: build-and-push
    image: quay.io/buildah/stable
    script: |
      cd /workspace/source
      buildah build -t $(params.registry)/task-manager-api:latest .
      buildah push $(params.registry)/task-manager-api:latest
```

### 3. PipelineRun (pipelinerun.yaml)

```yaml
apiVersion: tekton.dev/v1beta1
kind: PipelineRun
metadata:
  name: task-manager-pipeline-run-1
spec:
  pipelineRef:
    name: task-manager-pipeline
  params:
  - name: git-revision
    value: main
  - name: registry
    value: quay.io/bsteve456
  workspaces:
  - name: source
    emptyDir: {}
```

Creates an instance of the Pipeline with specific parameters.

### 4. EventListener (Optional - for webhooks)

Accepts GitHub webhooks and creates PipelineRuns:

```yaml
apiVersion: triggers.tekton.dev/v1beta1
kind: EventListener
metadata:
  name: github-listener
spec:
  triggers:
  - name: github-push
    bindings:
    - ref: github-binding
    template:
      ref: github-template
```

---

## Task Breakdown

### Task 1: git-clone

**Purpose:** Clone repository from GitHub

**Container Image:** `alpine/git:latest` (lightweight Git container)

**Parameters:**
- `revision` - Branch/commit to checkout (default: main)

**Steps:**
```bash
# Step 1: Clone repository
git clone https://github.com/bsteve456/Containerized-Flask-API-deployed-on-OpenShift.git /workspace/source

# Step 2: Navigate to directory
cd /workspace/source

# Step 3: Checkout specific revision
git checkout main
```

**Output:**
- `/workspace/source/` - Full repository code
  ```
  ├── app/
  ├── tests/
  ├── kubernetes/
  ├── pipeline/
  ├── Dockerfile
  ├── requirements.txt
  └── ...
  ```

**Success Criteria:**
- ✅ Exit code 0
- ✅ Source files readable

**Common Errors:**
```
Error: "Could not resolve host: github.com"
└─ Network connectivity issue
└─ Check cluster egress rules

Error: "fatal: Unexpected end of command stream"
└─ Invalid git URL
└─ Check pipeline.yaml git-clone URL

Error: "fatal: invalid gitfile format"
└─ Repository doesn't exist
└─ Verify GitHub URL
```

---

### Task 2: run-tests

**Purpose:** Execute unit tests to validate code

**Container Image:** `python:3.9` (Python runtime)

**Parameters:** None (uses workspace)

**Steps:**
```bash
# Step 1: Navigate to workspace
cd /workspace/source

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run pytest
PYTHONPATH=. pytest tests/test_tasks.py -v

# Expected output:
# test_health PASSED           [ 25%]
# test_get_tasks_empty PASSED  [ 50%]
# test_create_task PASSED      [ 75%]
# test_delete_task PASSED      [100%]
#
# ====== 4 passed in 0.44s ======
```

**Tests Executed:**
```python
1. test_health()
   └─ Verifies GET /health returns {"status": "healthy"}

2. test_get_tasks_empty()
   └─ Verifies GET /tasks returns []

3. test_create_task()
   └─ Verifies POST /tasks creates task with auto-increment ID

4. test_delete_task()
   └─ Verifies DELETE /tasks/{id} removes task
```

**Success Criteria:**
- ✅ All 4 tests pass
- ✅ Exit code 0
- ✅ No assertion failures

**Failure Behavior:**
```
If any test fails:
└─ Task marked as FAILED
└─ Pipeline stops (build-image doesn't run)
└─ Developer notified via GitHub
└─ No image pushed to registry
```

**Common Errors:**
```
Error: "No module named 'app'"
└─ Solution: PYTHONPATH=. pytest

Error: "FAILED tests/test_tasks.py::test_health"
└─ Solution: Run test locally, debug, push fix

Error: "ConnectionRefusedError: [Errno 111] Connection refused"
└─ Solution: Database not running (tests should use SQLite)
```

---

### Task 3: build-image

**Purpose:** Build Docker image and push to registry

**Container Image:** `quay.io/buildah/stable` (Container image builder)

**Parameters:**
- `registry` - Registry URL (e.g., quay.io/bsteve456)

**Steps:**
```bash
# Step 1: Navigate to workspace (has Dockerfile)
cd /workspace/source

# Step 2: Build image with Buildah
buildah build -t quay.io/bsteve456/task-manager-api:latest .

# Step 3: Push to registry
buildah push quay.io/bsteve456/task-manager-api:latest docker://quay.io/bsteve456/task-manager-api:latest

# Expected output:
# Copying blob 5d20c...
# Copying blob 8d4e...
# Copying config 7f9c...
# Writing manifest to image destination
# Successfully pushed image
```

**What Gets Built:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
ENV FLASK_APP=app/main.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app.main:app"]
```

**Image Details:**
- **Size:** ~400MB
- **Base:** python:3.9-slim
- **Tag:** latest (and commit SHA optional)
- **Registry:** Quay.io or Docker Hub
- **Accessibility:** Public (for this demo)

**Success Criteria:**
- ✅ Image builds without errors
- ✅ All layers cached properly
- ✅ Image pushed to registry
- ✅ Exit code 0

**Common Errors:**
```
Error: "authentication required"
└─ Solution: oc create secret docker-registry quay-credentials...
└─ Solution: oc patch serviceaccount default -p '...'

Error: "COPY failed: stat /path/to/file: no such file or directory"
└─ Solution: Dockerfile paths must match workspace structure

Error: "Dockerfile not found"
└─ Solution: git-clone didn't work, check previous task
```

---

## Execution Flow

### Normal Successful Execution

```
Time: T+0s
├─ User: git push origin main
│
Time: T+1s
├─ GitHub: Sends webhook to Tekton EventListener
│
Time: T+2s
├─ Tekton: Creates PipelineRun
│   └─ task-manager-pipeline-run-123
│
Time: T+5s
├─ Task 1: git-clone starts
│   ├─ Pod created: git-clone-xxxxx
│   └─ Container: alpine/git:latest
│
Time: T+65s (T+60s runtime)
├─ Task 1: git-clone succeeds ✅
│   ├─ Output: /workspace/source/* (full repo)
│   └─ Next task can start
│
Time: T+70s
├─ Task 2: run-tests starts
│   ├─ Pod created: run-tests-xxxxx
│   └─ Container: python:3.9
│
Time: T+190s (T+120s runtime)
├─ Task 2: run-tests succeeds ✅
│   ├─ Output: 4 tests passed
│   └─ Next task can start
│
Time: T+195s
├─ Task 3: build-image starts
│   ├─ Pod created: build-image-xxxxx
│   └─ Container: quay.io/buildah/stable
│
Time: T+375s (T+180s runtime)
├─ Task 3: build-image succeeds ✅
│   ├─ Output: Image pushed to quay.io/bsteve456/task-manager-api:latest
│   └─ PipelineRun status: Succeeded
│
Time: T+380s
├─ Tekton: Notifies GitHub (status: SUCCESS ✅)
│
Time: T+381s (Total: 6 minutes 21 seconds)
└─ Pipeline Complete!
   ├─ Logs: Available via oc logs
   └─ Webhook Deployment: (automatic if configured)
```

### Failed Execution (Test Fails)

```
Time: T+0s
├─ User: git push origin main
│
...
│
Time: T+190s
├─ Task 2: run-tests FAILS ❌
│   ├─ Test assertion fails
│   ├─ Exit code 1 (failure)
│   └─ Task marked as FAILED
│
Time: T+195s
├─ Pipeline Status: FAILED ❌
│   ├─ Remaining tasks cancelled (build-image doesn't run)
│   └─ No image pushed to registry
│
Time: T+196s
├─ Tekton: Notifies GitHub (status: FAILURE ❌)
│   └─ GitHub shows red X on commit
│
Time: T+197s
├─ Developer: Gets notification
│   ├─ Email: "Pipeline failed"
│   ├─ GitHub: Commit marked as failed
│   └─ Action: Fix tests and push again
```

### Partial Task Execution (Custom Parameters)

```
Example: Run only tests (skip git-clone)

Command: tkn pipeline start task-manager-pipeline \
  --param git-revision=dev \
  --workspace name=source,emptyDir=

Uses:
├─ git-revision = dev (checkout dev branch, not main)
├─ workspace = emptyDir (temporary storage)
└─ All tasks execute with custom params
```

---

## Configuration & Customization

### Changing Pipeline Parameters

**Current Default Parameters:**
```yaml
params:
- name: git-revision
  type: string
  default: main
- name: registry
  type: string
  default: quay.io/bsteve456
```

**How to Override:**

Option 1: Edit pipelinerun.yaml
```yaml
params:
- name: git-revision
  value: develop          # Changed from main
- name: registry
  value: docker.io/myuser # Changed from quay.io
```

Option 2: Command-line
```bash
tkn pipeline start task-manager-pipeline \
  --param git-revision=develop \
  --param registry=docker.io/myuser
```

### Adding a New Task to Pipeline

Example: Add linting task

**Step 1: Create linting task**
```yaml
# pipeline/lint-code.yaml
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: lint-code
spec:
  workspaces:
  - name: source
  steps:
  - name: lint
    image: python:3.9
    script: |
      cd /workspace/source
      pip install flake8
      flake8 app/ --max-line-length=100
```

**Step 2: Update pipeline.yaml**
```yaml
tasks:
- name: clone-repo
  ...

- name: lint-code
  taskRef:
    name: lint-code
  runAfter:
  - clone-repo
  workspaces:
  - name: source
    workspace: source

- name: test-code
  ...
  runAfter:
  - lint-code  # Changed: now depends on lint-code, not clone-repo
```

### Adding Security Scanning

Example: Trivy vulnerability scanner

```yaml
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: scan-image
spec:
  params:
  - name: image
    type: string
  steps:
  - name: trivy-scan
    image: aquasec/trivy:latest
    script: |
      trivy image --severity HIGH,CRITICAL $(params.image)
      # Exit code 0 if no critical vulnerabilities
```

Add to pipeline:
```yaml
- name: scan-image
  taskRef:
    name: scan-image
  params:
  - name: image
    value: quay.io/bsteve456/task-manager-api:latest
  runAfter:
  - build-image
```

### Environment Variables

Pass secrets/config to tasks:

```yaml
- name: build-push-image
  taskRef:
    name: build-image
  params:
  - name: registry
    value: $(params.registry)
  env:
  - name: REGISTRY_USERNAME
    valueFrom:
      secretKeyRef:
        name: registry-credentials
        key: username
  - name: REGISTRY_PASSWORD
    valueFrom:
      secretKeyRef:
        name: registry-credentials
        key: password
```

Create secret:
```bash
oc create secret generic registry-credentials \
  --from-literal=username=bsteve456 \
  --from-literal=password=<token>
```

---

## Monitoring & Debugging

### View Pipeline Execution

**List all PipelineRuns:**
```bash
oc get pipelinerun

# Output:
# NAME                             SUCCEEDED   REASON     STARTTIME   COMPLETIONTIME
# task-manager-pipeline-run-1      True        Succeeded  5m ago      2m ago
# task-manager-pipeline-run-2      False       Failed     3m ago      2m ago
```

**View specific PipelineRun:**
```bash
oc describe pipelinerun task-manager-pipeline-run-1

# Output shows:
# Name: task-manager-pipeline-run-1
# Status: Succeeded
# Start Time: ...
# Completion Time: ...
# Tasks:
#   clone-repo: Succeeded
#   test-code: Succeeded
#   build-image: Succeeded
```

**View full PipelineRun YAML:**
```bash
oc get pipelinerun task-manager-pipeline-run-1 -o yaml
```

### View Task Logs

**Get TaskRun names:**
```bash
oc get taskrun

# Lists all task executions
```

**View task logs:**
```bash
# View git-clone task logs
oc logs taskrun/task-manager-pipeline-run-1-clone-repo-xxxxx

# View run-tests task logs
oc logs taskrun/task-manager-pipeline-run-1-test-code-xxxxx

# View build-image task logs with live output
oc logs -f taskrun/task-manager-pipeline-run-1-build-image-xxxxx
```

**Follow pipeline execution in real-time:**
```bash
# Using Tekton CLI
tkn pipelinerun logs -f <pipeline-run-name>

# Shows live output as tasks execute
```

### Pipeline Web UI

**OpenShift Developer Console:**
```
1. Login to OpenShift console
2. Navigate to: Developer → Pipelines
3. Click: task-manager-pipeline
4. View: Execution history, logs, status
```

**Tekton Dashboard (if installed):**
```
1. Access: <tekton-dashboard-url>
2. View: Pipeline, PipelineRuns, TaskRuns
3. Monitor: Real-time execution
```

### Debugging Failed Pipelines

**Problem: Task fails, but logs are unclear**

```bash
# Get detailed event information
oc describe taskrun <taskrun-name>

# Shows:
# - Status
# - Exit code
# - Pod created
# - Container status
# - Events (warnings, errors)
```

**Problem: Pod stuck in Pending**

```bash
# Check pod status
oc get pod -l tekton.dev/pipelineRun=<pipeline-run-name>

# Get pod events
oc describe pod <pod-name>

# Check resource availability
oc describe node

# Common causes:
# - Insufficient CPU
# - Insufficient memory
# - Image not pulling
# - Volume mount issues
```

**Problem: Image push fails**

```bash
# Check image registry credentials
oc get secret docker-registry regcred -o yaml

# Verify registry is accessible
oc exec taskrun/xxx -- curl https://quay.io/api/v1/ping

# Check service account has image pull permissions
oc get serviceaccount default -o yaml
```

---

## Best Practices

### 1. Pipeline Design

✅ **DO:**
- Keep tasks focused on single responsibility
- Use meaningful task names
- Document parameters and outputs
- Run fast tasks before slow ones

❌ **DON'T:**
- Create mega-tasks that do everything
- Skip intermediate validation steps
- Ignore task failure modes
- Hardcode configuration values

### 2. Error Handling

✅ **DO:**
- Exit with code 0 on success, 1 on failure
- Log errors to stdout/stderr
- Make failure messages descriptive
- Use `set -e` to fail on first error

```bash
set -e  # Exit on any error

# Commands here
cd /workspace/source
pytest tests/

# If pytest fails, script stops immediately
```

❌ **DON'T:**
- Ignore test failures (always check exit codes)
- Log sensitive data (passwords, tokens)
- Use `|| true` to suppress legitimate errors

### 3. Performance Optimization

✅ **DO:**
- Cache Docker layers
- Use lightweight base images
- Parallelize independent tasks
- Pin container image versions

```dockerfile
# Good: Lightweight base
FROM python:3.9-slim

# Good: Layer caching
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .  # App code changes frequently, layer on top
```

❌ **DON'T:**
- Use latest tag (always use specific versions)
- Copy large files unnecessarily
- Run unnecessary build steps

### 4. Security

✅ **DO:**
- Use secrets for credentials (not env vars)
- Scan images for vulnerabilities
- Run containers as non-root
- Validate all inputs

```bash
# Good: Pull from secret
docker login -u $(echo $REGISTRY_USER) -p $(echo $REGISTRY_PASS)

# Good: Scan image
trivy image --severity HIGH quay.io/...
```

❌ **DON'T:**
- Store credentials in pipeline definition
- Push images to public registry without scanning
- Run containers as root
- Skip authentication checks

### 5. Testing

✅ **DO:**
- Test before building image
- Use consistent test environment
- Report coverage metrics
- Test failure scenarios

```bash
# Good: Run tests with coverage
pytest --cov=app tests/

# Good: Generate test report
pytest --junit-xml=test-results.xml tests/
```

❌ **DON'T:**
- Skip tests to save time
- Test in different environments (dev vs CI)
- Ignore test coverage

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: "Invalid credential supplied" during image push

**Symptom:**
```
Error: CREDENTIAL_NOT_FOUND
Error: Unauthorized
```

**Root Cause:** Registry credentials not available in pipeline

**Solution:**
```bash
# Create secret with registry credentials
oc create secret docker-registry registry-creds \
  --docker-server=quay.io \
  --docker-username=bsteve456 \
  --docker-password=<token>

# Link secret to service account
oc secrets link default registry-creds --for=pull
oc secrets link default registry-creds --for=mount

# Update TaskRun to use secret (in task definition)
volumes:
- name: docker-config
  secret:
    secretName: registry-creds
```

#### Issue 2: "git clone failed: unknown host"

**Symptom:**
```
error: exec: "git": executable file not found
fatal: Could not read from remote repository
```

**Root Cause:** Network issue or wrong base image

**Solution:**
```yaml
# Ensure git image has git installed
image: alpine/git:latest  # Already has git

# Or install git manually
image: alpine:latest
script: |
  apk add --no-cache git  # Install git first
  git clone ...
```

#### Issue 3: "File not found" in workspace

**Symptom:**
```
No such file or directory: /workspace/source/requirements.txt
```

**Root Cause:** Previous task didn't complete or didn't share workspace

**Solution:**
```yaml
# Ensure correct workspace name
workspaces:
- name: source      # Must match

# Ensure runAfter dependency
tasks:
- name: test-code
  runAfter:
  - clone-repo      # Must wait for clone to finish
```

#### Issue 4: Pipeline stuck in "Running" state

**Symptom:**
```
Status: Unknown (running for 1 hour)
```

**Root Cause:** Pod stuck, resource deadlock, or network issue

**Solution:**
```bash
# Check pod status
oc get pod -l tekton.dev/pipelineRun=xxx

# Delete stuck pod (Kubernetes will recreate)
oc delete pod taskrun-xxx-pod-xxxxx

# If still stuck, delete entire PipelineRun
oc delete pipelinerun xxx

# Restart pipeline
oc apply -f pipeline/pipelinerun.yaml
```

#### Issue 5: "Permission denied" during mount

**Symptom:**
```
Error: permission denied while trying to connect to Docker daemon
```

**Root Cause:** Container running as non-root (buildah requires root)

**Solution:**
```yaml
# Allow privileged execution for buildah
securityContext:
  privileged: true
  runAsUser: 0
  runAsGroup: 0
```

---

## Advanced Topics

### Conditional Task Execution

Run task only if previous succeeded:

```yaml
- name: build-image
  when:
  - input: $(tasks.test-code.status)
    operator: in
    values: ["Succeeded"]
```

### Retry Strategies

Retry task on failure:

```yaml
- name: build-image
  taskRef:
    name: build-image
  retries: 2  # Retry up to 2 times
  timeout: 10m
```

### Parallel Tasks

Run independent tasks concurrently:

```yaml
tasks:
- name: lint
  taskRef: lint-task

- name: test
  taskRef: test-task
  # No runAfter = runs parallel to lint

- name: security-scan
  taskRef: scan-task
  # No runAfter = runs parallel to others

- name: build
  taskRef: build-task
  runAfter:
  - lint
  - test
  - security-scan
  # Waits for all above to complete
```

### Matrix (Tekton 0.42+)

Run task multiple times with different parameters:

```yaml
- name: test-matrix
  taskRef:
    name: test-task
  params:
  - name: python-version
    value:
    - "3.8"
    - "3.9"
    - "3.10"
  # Runs test-task 3 times with different Python versions
```

---

## Performance Tuning

### Optimize Pipeline Runtime

**Current Total Time:** ~6 minutes

```
git-clone:     1 minute  ├─ Can't parallelize (dependency)
run-tests:     2 minutes ├─ Can't parallelize (needs clone)
build-image:   3 minutes └─ Can't parallelize (needs test)
────────────────────────
Total:         6 minutes
```

**Optimization Strategy:**

```
Option 1: Cache dependencies
├─ Cache pip packages
├─ Cache Docker layers
└─ Result: 4 minutes total

Option 2: Faster test framework
├─ Use pytest-xdist for parallel tests
├─ Result: 1.5 minutes (30% faster)

Option 3: Lightweight images
├─ Use python:3.9-alpine instead of python:3.9
├─ Result: 2.5 minutes (smaller downloads)
```

### Resource Requests/Limits

```yaml
resources:
  requests:
    memory: "512Mi"  # Minimum needed
    cpu: "500m"      # 0.5 CPU cores
  limits:
    memory: "1Gi"    # Maximum allowed
    cpu: "1000m"     # 1 CPU core
```

---

## Summary

Tekton Pipeline provides:

✅ **Automation** - Run tests and builds automatically  
✅ **Reliability** - Consistent, repeatable processes  
✅ **Transparency** - View execution and logs  
✅ **Scalability** - Run multiple pipelines in parallel  
✅ **Integration** - GitHub webhooks for automation  

Perfect for modern DevOps workflows! 🚀

For more info: https://tekton.dev/docs/
