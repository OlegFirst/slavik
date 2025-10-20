# BCM Platform - GKE Terraform Configuration
# Google Kubernetes Engine with Istio, Autopilot, and monitoring

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }

  # Optional: Configure remote state (uncomment for production)
  # backend "gcs" {
  #   bucket = "bcm-platform-terraform-state"
  #   prefix = "gke/production"
  # }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE Cluster Name"
  type        = string
  default     = "bcm-platform-prod"
}

variable "environment" {
  description = "Environment (production/staging)"
  type        = string
  default     = "production"
}

variable "enable_autopilot" {
  description = "Enable GKE Autopilot mode"
  type        = bool
  default     = true
}

variable "min_nodes" {
  description = "Minimum number of nodes (Standard mode only)"
  type        = number
  default     = 3
}

variable "max_nodes" {
  description = "Maximum number of nodes (Standard mode only)"
  type        = number
  default     = 10
}

variable "machine_type" {
  description = "Machine type for nodes (Standard mode only)"
  type        = string
  default     = "e2-standard-4"
}

variable "enable_istio" {
  description = "Enable Istio service mesh"
  type        = bool
  default     = true
}

variable "enable_monitoring" {
  description = "Enable Cloud Monitoring and Logging"
  type        = bool
  default     = true
}

# Provider Configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "container_api" {
  project = var.project_id
  service = "container.googleapis.com"

  disable_on_destroy = false
}

resource "google_project_service" "compute_api" {
  project = var.project_id
  service = "compute.googleapis.com"

  disable_on_destroy = false
}

resource "google_project_service" "monitoring_api" {
  project = var.project_id
  service = "monitoring.googleapis.com"

  disable_on_destroy = false
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "${var.cluster_name}-vpc"
  auto_create_subnetworks = false

  depends_on = [
    google_project_service.compute_api
  ]
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.cluster_name}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/16"
  }
}

# GKE Autopilot Cluster
resource "google_container_cluster" "autopilot" {
  count = var.enable_autopilot ? 1 : 0

  name     = var.cluster_name
  location = var.region

  # Autopilot mode
  enable_autopilot = true

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  # IP allocation policy
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Release channel
  release_channel {
    channel = "REGULAR"
  }

  # Monitoring
  monitoring_config {
    enable_components = var.enable_monitoring ? ["SYSTEM_COMPONENTS", "WORKLOADS"] : []

    managed_prometheus {
      enabled = var.enable_monitoring
    }
  }

  # Logging
  logging_config {
    enable_components = var.enable_monitoring ? ["SYSTEM_COMPONENTS", "WORKLOADS"] : []
  }

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }

    horizontal_pod_autoscaling {
      disabled = false
    }

    network_policy_config {
      disabled = false
    }

    gcp_filestore_csi_driver_config {
      enabled = true
    }

    gcs_fuse_csi_driver_config {
      enabled = true
    }
  }

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Binary Authorization
  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  # Labels
  resource_labels = {
    environment = var.environment
    managed_by  = "terraform"
    platform    = "bcm"
  }

  depends_on = [
    google_project_service.container_api
  ]
}

# GKE Standard Cluster (alternative to Autopilot)
resource "google_container_cluster" "standard" {
  count = var.enable_autopilot ? 0 : 1

  name     = var.cluster_name
  location = var.region

  # Remove default node pool (we'll create custom one)
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  # IP allocation policy
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Release channel
  release_channel {
    channel = "REGULAR"
  }

  # Monitoring
  monitoring_config {
    enable_components = var.enable_monitoring ? ["SYSTEM_COMPONENTS", "WORKLOADS"] : []

    managed_prometheus {
      enabled = var.enable_monitoring
    }
  }

  # Logging
  logging_config {
    enable_components = var.enable_monitoring ? ["SYSTEM_COMPONENTS", "WORKLOADS"] : []
  }

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }

    horizontal_pod_autoscaling {
      disabled = false
    }

    network_policy_config {
      disabled = false
    }

    gcp_filestore_csi_driver_config {
      enabled = true
    }
  }

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  # Labels
  resource_labels = {
    environment = var.environment
    managed_by  = "terraform"
    platform    = "bcm"
  }

  depends_on = [
    google_project_service.container_api
  ]
}

# Node Pool for Standard Cluster
resource "google_container_node_pool" "primary" {
  count = var.enable_autopilot ? 0 : 1

  name       = "${var.cluster_name}-pool"
  location   = var.region
  cluster    = google_container_cluster.standard[0].name
  node_count = var.min_nodes

  # Autoscaling
  autoscaling {
    min_node_count = var.min_nodes
    max_node_count = var.max_nodes
  }

  # Node configuration
  node_config {
    machine_type = var.machine_type
    disk_size_gb = 50
    disk_type    = "pd-standard"

    # OAuth scopes
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Labels
    labels = {
      environment = var.environment
      pool        = "primary"
    }

    # Tags
    tags = ["bcm-platform", var.environment]

    # Metadata
    metadata = {
      disable-legacy-endpoints = "true"
    }

    # Shielded instance config
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  # Management
  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# Cloud Storage bucket for Velero backups
resource "google_storage_bucket" "velero_backups" {
  name     = "${var.project_id}-bcm-velero-backups"
  location = var.region

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    environment = var.environment
    purpose     = "velero-backups"
  }
}

# Service Account for Velero
resource "google_service_account" "velero" {
  account_id   = "${var.cluster_name}-velero"
  display_name = "Velero Backup Service Account"
}

# IAM binding for Velero
resource "google_storage_bucket_iam_member" "velero" {
  bucket = google_storage_bucket.velero_backups.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.velero.email}"
}

# Service Account key for Velero
resource "google_service_account_key" "velero" {
  service_account_id = google_service_account.velero.name
}

# Outputs
output "cluster_name" {
  description = "GKE Cluster Name"
  value       = var.enable_autopilot ? google_container_cluster.autopilot[0].name : google_container_cluster.standard[0].name
}

output "cluster_endpoint" {
  description = "GKE Cluster Endpoint"
  value       = var.enable_autopilot ? google_container_cluster.autopilot[0].endpoint : google_container_cluster.standard[0].endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "GKE Cluster CA Certificate"
  value       = var.enable_autopilot ? google_container_cluster.autopilot[0].master_auth[0].cluster_ca_certificate : google_container_cluster.standard[0].master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "velero_bucket" {
  description = "Velero backup bucket"
  value       = google_storage_bucket.velero_backups.name
}

output "velero_sa_key" {
  description = "Velero service account key (base64 encoded)"
  value       = google_service_account_key.velero.private_key
  sensitive   = true
}

output "get_credentials_command" {
  description = "Command to get cluster credentials"
  value       = "gcloud container clusters get-credentials ${var.enable_autopilot ? google_container_cluster.autopilot[0].name : google_container_cluster.standard[0].name} --region ${var.region} --project ${var.project_id}"
}
