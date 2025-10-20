# DigitalOcean Kubernetes Cluster - Terraform Configuration
# Based on official DigitalOcean Terraform Provider documentation
# Reference: https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs

terraform {
  required_version = ">= 1.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.34.0"
    }
  }
}

# Configure the DigitalOcean Provider
provider "digitalocean" {
  token = var.do_token
}

# Create a VPC for the cluster (optional but recommended)
resource "digitalocean_vpc" "bcm_vpc" {
  count       = var.vpc_uuid == "" ? 1 : 0
  name        = "${var.cluster_name}-vpc"
  region      = var.region
  description = "VPC for BCM Platform Kubernetes cluster"
}

# Create DigitalOcean Kubernetes Cluster
# Reference: https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs/resources/kubernetes_cluster
resource "digitalocean_kubernetes_cluster" "bcm_cluster" {
  name    = var.cluster_name
  region  = var.region
  version = var.k8s_version

  # Use provided VPC or create new one
  vpc_uuid = var.vpc_uuid != "" ? var.vpc_uuid : digitalocean_vpc.bcm_vpc[0].id

  # Enable HA control plane for production
  ha = var.ha_control_plane

  # Auto-upgrade to latest patch version
  auto_upgrade = var.auto_upgrade

  # Surge upgrade (zero-downtime upgrades)
  surge_upgrade = true

  # Maintenance window
  maintenance_policy {
    day        = var.maintenance_day
    start_time = var.maintenance_hour
  }

  # Default node pool
  node_pool {
    name       = var.node_pool_name
    size       = var.node_size
    node_count = var.node_count

    # Enable autoscaling
    auto_scale = true
    min_nodes  = var.min_nodes
    max_nodes  = var.max_nodes

    # Labels for node selection
    labels = {
      workload = "general"
      env      = var.environment
    }

    # Taints for specialized workloads (optional)
    # taint {
    #   key    = "workloadType"
    #   value  = "general"
    #   effect = "NoSchedule"
    # }
  }

  # Tags for resource organization
  tags = var.tags
}

# Install 1-Click Applications (NGINX Ingress Controller)
# Reference: https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs/resources/kubernetes_1_click
resource "digitalocean_kubernetes_1_click" "ingress_nginx" {
  count      = contains(var.one_clicks, "ingress-nginx") ? 1 : 0
  cluster_id = digitalocean_kubernetes_cluster.bcm_cluster.id
  addon_slug = "ingress-nginx"

  depends_on = [
    digitalocean_kubernetes_cluster.bcm_cluster
  ]
}

# Install Monitoring Stack (Prometheus + Grafana)
resource "digitalocean_kubernetes_1_click" "monitoring" {
  count      = contains(var.one_clicks, "monitoring") ? 1 : 0
  cluster_id = digitalocean_kubernetes_cluster.bcm_cluster.id
  addon_slug = "monitoring"

  depends_on = [
    digitalocean_kubernetes_cluster.bcm_cluster
  ]
}

# Create DigitalOcean Container Registry (optional)
# Reference: https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs/resources/container_registry
resource "digitalocean_container_registry" "bcm_registry" {
  count                  = var.create_container_registry ? 1 : 0
  name                   = var.registry_name
  subscription_tier_slug = var.registry_subscription_tier
  region                 = var.region
}

# Connect Container Registry to Kubernetes Cluster
resource "digitalocean_container_registry_docker_credentials" "bcm_registry_credentials" {
  count          = var.create_container_registry ? 1 : 0
  registry_name  = digitalocean_container_registry.bcm_registry[0].name
  write          = true
  expiry_seconds = 0 # No expiration

  depends_on = [
    digitalocean_container_registry.bcm_registry
  ]
}

# Create DigitalOcean Space for Velero Backups
# Reference: https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs/resources/spaces_bucket
resource "digitalocean_spaces_bucket" "velero_backups" {
  count  = var.create_spaces_bucket ? 1 : 0
  name   = var.spaces_bucket_name
  region = var.spaces_region

  # Enable versioning for backup safety
  versioning {
    enabled = true
  }

  # Lifecycle rules for backup retention
  lifecycle_rule {
    enabled = true
    id      = "delete-old-backups"

    expiration {
      days = var.backup_retention_days
    }
  }

  # Make bucket private
  acl = "private"
}

# Local file for kubeconfig (auto-generated)
resource "local_file" "kubeconfig" {
  content  = digitalocean_kubernetes_cluster.bcm_cluster.kube_config[0].raw_config
  filename = "${path.module}/kubeconfig-${var.cluster_name}.yaml"

  file_permission = "0600"
}

# Outputs
output "cluster_id" {
  description = "The ID of the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.bcm_cluster.id
}

output "cluster_name" {
  description = "The name of the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.bcm_cluster.name
}

output "cluster_endpoint" {
  description = "The base URL of the API server on the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.bcm_cluster.endpoint
}

output "cluster_status" {
  description = "The status of the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.bcm_cluster.status
}

output "cluster_region" {
  description = "The region where the cluster is deployed"
  value       = digitalocean_kubernetes_cluster.bcm_cluster.region
}

output "cluster_version" {
  description = "The Kubernetes version"
  value       = digitalocean_kubernetes_cluster.bcm_cluster.version
}

output "vpc_uuid" {
  description = "The VPC UUID"
  value       = var.vpc_uuid != "" ? var.vpc_uuid : digitalocean_vpc.bcm_vpc[0].id
}

output "node_pool_id" {
  description = "The ID of the default node pool"
  value       = digitalocean_kubernetes_cluster.bcm_cluster.node_pool[0].id
}

output "kubeconfig_path" {
  description = "Path to the generated kubeconfig file"
  value       = local_file.kubeconfig.filename
}

output "container_registry_endpoint" {
  description = "Container registry endpoint"
  value       = var.create_container_registry ? digitalocean_container_registry.bcm_registry[0].endpoint : null
}

output "spaces_bucket_name" {
  description = "DigitalOcean Spaces bucket for backups"
  value       = var.create_spaces_bucket ? digitalocean_spaces_bucket.velero_backups[0].name : null
}

output "spaces_bucket_region" {
  description = "DigitalOcean Spaces bucket region"
  value       = var.create_spaces_bucket ? digitalocean_spaces_bucket.velero_backups[0].region : null
}

output "connection_command" {
  description = "Command to connect to the cluster using doctl"
  value       = "doctl kubernetes cluster kubeconfig save ${digitalocean_kubernetes_cluster.bcm_cluster.name}"
}

output "kubectl_config_command" {
  description = "Command to use the generated kubeconfig with kubectl"
  value       = "export KUBECONFIG=${local_file.kubeconfig.filename}"
}
