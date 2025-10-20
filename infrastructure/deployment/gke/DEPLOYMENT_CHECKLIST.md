# GKE Deployment Checklist

Complete checklist for production-ready GKE deployment.

## Pre-Deployment

### Google Cloud Setup
- [ ] GCP Project created
- [ ] Billing enabled and verified
- [ ] Project ID documented
- [ ] gcloud CLI installed (`gcloud version`)
- [ ] Authenticated to GCP (`gcloud auth login`)
- [ ] Default project set (`gcloud config set project PROJECT_ID`)
- [ ] Default region set (`gcloud config set compute/region REGION`)

### Required Tools
- [ ] kubectl installed (`kubectl version --client`)
- [ ] gke-gcloud-auth-plugin installed (`gcloud components install gke-gcloud-auth-plugin`)
- [ ] istioctl installed (via `gke-install-addons.sh`)
- [ ] velero CLI installed (`velero version`)

### Configuration
- [ ] `terraform.tfvars` created from example
- [ ] `project_id` configured correctly
- [ ] `cluster_name` set (unique, alphanumeric + hyphens)
- [ ] `region` selected (e.g., us-central1)
- [ ] `release_channel` chosen (rapid/regular/stable)
- [ ] Network settings reviewed

### Permissions & Quotas
- [ ] User has `roles/container.admin` role
- [ ] User has `roles/iam.serviceAccountUser` role
- [ ] Compute Engine quota sufficient (check console)
- [ ] IP address quota available for region

## Deployment Phase

### Step 1: Cluster Creation
- [ ] Run `./gke-create-cluster.sh`
- [ ] Script completes without errors
- [ ] Cluster creation confirmed in GCP Console
- [ ] Required APIs enabled:
  - [ ] container.googleapis.com
  - [ ] compute.googleapis.com
  - [ ] monitoring.googleapis.com
  - [ ] logging.googleapis.com
- [ ] Cluster status: RUNNING
  ```bash
  gcloud container clusters describe CLUSTER_NAME --region=REGION
  ```

### Step 2: kubectl Configuration
- [ ] Run `./gke-configure.sh`
- [ ] kubectl context created
- [ ] Cluster info displays correctly (`kubectl cluster-info`)
- [ ] Nodes visible (`kubectl get nodes`)
- [ ] All nodes in Ready state

### Step 3: Add-ons Installation
- [ ] Run `./gke-install-addons.sh`
- [ ] Istio downloaded (check `istio-*` directory)
- [ ] Istio installed successfully
- [ ] Istio pods running in `istio-system` namespace
  ```bash
  kubectl get pods -n istio-system
  ```
- [ ] Default namespace labeled for injection
  ```bash
  kubectl get namespace default --show-labels
  ```
- [ ] Cloud Operations verified (monitoring/logging)

### Step 4: BCM Platform Deployment
- [ ] Run `./gke-deploy-bcm.sh`
- [ ] BCM namespace created
- [ ] BCM namespace labeled for Istio injection
- [ ] Secrets created
- [ ] ConfigMaps created
- [ ] Deployments created and running
  ```bash
  kubectl get deployments -n bcm-platform
  ```
- [ ] All pods in Running state
  ```bash
  kubectl get pods -n bcm-platform
  ```
- [ ] Services created
  ```bash
  kubectl get services -n bcm-platform
  ```
- [ ] LoadBalancer IP assigned
  ```bash
  kubectl get svc bcm-platform -n bcm-platform -o wide
  ```

### Step 5: Velero Backup Setup
- [ ] Run `./velero-setup.sh`
- [ ] GCS bucket created
  ```bash
  gsutil ls | grep velero
  ```
- [ ] Bucket versioning enabled
  ```bash
  gsutil versioning get gs://BUCKET_NAME
  ```
- [ ] Service account created
  ```bash
  gcloud iam service-accounts list | grep velero
  ```
- [ ] Custom IAM role created
- [ ] Permissions bound correctly
- [ ] Service account key generated
- [ ] Velero installed in cluster
  ```bash
  kubectl get pods -n velero
  ```
- [ ] Backup schedule created
  ```bash
  velero schedule get
  ```

## Post-Deployment Verification

### Cluster Health
- [ ] All nodes Ready
  ```bash
  kubectl get nodes
  ```
- [ ] All system pods running
  ```bash
  kubectl get pods -n kube-system
  ```
- [ ] Resource utilization normal
  ```bash
  kubectl top nodes
  ```

### Application Health
- [ ] All BCM pods Running
  ```bash
  kubectl get pods -n bcm-platform
  ```
- [ ] All deployments Available
  ```bash
  kubectl get deployments -n bcm-platform
  ```
- [ ] Services have endpoints
  ```bash
  kubectl get endpoints -n bcm-platform
  ```
- [ ] Application accessible via LoadBalancer IP
- [ ] Health checks passing
- [ ] No error logs
  ```bash
  kubectl logs -n bcm-platform -l app=bcm-platform --tail=100
  ```

### Istio Verification
- [ ] Istio control plane healthy
  ```bash
  istioctl verify-install
  ```
- [ ] Sidecar injection working
  ```bash
  kubectl get pods -n bcm-platform -o jsonpath='{.items[*].spec.containers[*].name}'
  ```
  (Should see `istio-proxy` alongside app containers)
- [ ] No configuration errors
  ```bash
  istioctl analyze -n bcm-platform
  ```

### Monitoring & Logging
- [ ] Cloud Monitoring dashboard accessible
- [ ] Metrics flowing to Cloud Monitoring
- [ ] Logs visible in Cloud Logging
- [ ] GKE cluster visible in console
- [ ] Custom dashboards created (optional)
- [ ] Alert policies configured (optional)

### Backup Verification
- [ ] Velero pods running
  ```bash
  kubectl get pods -n velero
  ```
- [ ] Backup location configured
  ```bash
  velero backup-location get
  ```
- [ ] Snapshot location configured
  ```bash
  velero snapshot-location get
  ```
- [ ] Schedule active
  ```bash
  velero schedule get
  ```
- [ ] Test backup created successfully
  ```bash
  velero backup create test-backup --include-namespaces bcm-platform --wait
  ```
- [ ] Backup in GCS bucket
  ```bash
  gsutil ls gs://BUCKET_NAME/backups/
  ```

## Security Hardening

### Network Security
- [ ] Private nodes enabled
- [ ] Private endpoint configured
- [ ] Master authorized networks set
- [ ] Network policies defined (if needed)
- [ ] Firewall rules reviewed

### Identity & Access
- [ ] Workload Identity enabled (recommended)
  ```bash
  gcloud container clusters update CLUSTER_NAME \
    --region=REGION \
    --workload-pool=PROJECT_ID.svc.id.goog
  ```
- [ ] RBAC roles configured
- [ ] Service accounts follow least privilege
- [ ] Pod Security Policies reviewed (if using)

### Secrets Management
- [ ] No hardcoded secrets in configs
- [ ] Kubernetes secrets encrypted at rest
- [ ] Consider Google Secret Manager integration
- [ ] Rotate service account keys regularly

### Container Security
- [ ] Images from trusted registries only
- [ ] Container vulnerability scanning enabled
- [ ] Binary Authorization configured (optional)
- [ ] Image signatures verified (optional)

### Cluster Security
- [ ] Auto-upgrade enabled (Autopilot default)
- [ ] Auto-repair enabled (Autopilot default)
- [ ] Security patches applied
- [ ] GKE security bulletins reviewed

## Production Readiness

### High Availability
- [ ] Multi-zone/regional cluster (Autopilot default)
- [ ] Sufficient replicas (minimum 3 for HA)
- [ ] Pod disruption budgets configured
- [ ] Anti-affinity rules for critical workloads

### Performance
- [ ] Resource requests/limits appropriate
  ```bash
  kubectl describe pods -n bcm-platform | grep -A 5 "Limits"
  ```
- [ ] Horizontal Pod Autoscaling configured (if needed)
- [ ] Load testing completed
- [ ] Performance baseline established

### Monitoring & Alerting
- [ ] Cloud Monitoring workspace configured
- [ ] Essential metrics dashboards created
- [ ] Alert policies configured:
  - [ ] Node availability
  - [ ] Pod crashes
  - [ ] High CPU/memory usage
  - [ ] Failed backups
  - [ ] Service unavailability
- [ ] Notification channels configured
- [ ] On-call rotation defined

### Disaster Recovery
- [ ] Backup schedule validated
- [ ] Backup retention policy set
- [ ] Test restore completed successfully
  ```bash
  velero restore create --from-backup test-backup
  ```
- [ ] RTO/RPO documented
- [ ] Disaster recovery runbook created
- [ ] DR testing scheduled

### Documentation
- [ ] Architecture diagram created
- [ ] Deployment procedures documented
- [ ] Runbooks for common operations
- [ ] Troubleshooting guide available
- [ ] Contact information documented
- [ ] Change management process defined

### Cost Management
- [ ] Resource right-sizing completed
- [ ] Committed Use Discounts evaluated
- [ ] Budget alerts configured
  ```bash
  # Set in Cloud Console: Billing > Budgets & alerts
  ```
- [ ] Cost allocation labels applied
- [ ] Unused resources identified and removed
- [ ] Storage lifecycle policies configured

## Ongoing Operations

### Daily
- [ ] Check cluster health
- [ ] Review error logs
- [ ] Monitor resource utilization
- [ ] Verify backups completed

### Weekly
- [ ] Review Cloud Monitoring metrics
- [ ] Check for security updates
- [ ] Review and optimize costs
- [ ] Update documentation as needed

### Monthly
- [ ] Test disaster recovery
- [ ] Review and rotate credentials
- [ ] Capacity planning review
- [ ] Security audit
- [ ] Update dependencies

### Quarterly
- [ ] Full DR exercise
- [ ] Security assessment
- [ ] Cost optimization review
- [ ] Architecture review

## Sign-off

### Deployment Team
- [ ] Technical Lead: _________________ Date: _______
- [ ] DevOps Engineer: _______________ Date: _______
- [ ] Security Review: _______________ Date: _______

### Stakeholders
- [ ] Product Owner: _________________ Date: _______
- [ ] Operations Manager: ____________ Date: _______

## Rollback Plan

If deployment fails:

1. **Identify Issue**
   ```bash
   kubectl get events -n bcm-platform --sort-by='.lastTimestamp'
   kubectl logs -n bcm-platform -l app=bcm-platform --tail=200
   ```

2. **Rollback Deployment**
   ```bash
   kubectl rollout undo deployment/bcm-platform -n bcm-platform
   ```

3. **Restore from Backup** (if needed)
   ```bash
   velero restore create --from-backup LAST_GOOD_BACKUP
   ```

4. **Delete Cluster** (nuclear option)
   ```bash
   gcloud container clusters delete CLUSTER_NAME --region=REGION
   ```

## Support Contacts

- **GKE Support**: https://cloud.google.com/kubernetes-engine/docs/support
- **Emergency Contact**: _______________________
- **Team Slack/Chat**: _________________________
- **Escalation Path**: _________________________

---

**Notes:**
- Review this checklist before each deployment
- Update checklist based on lessons learned
- Keep a copy of completed checklists for audit purposes
- Automate as many checks as possible
