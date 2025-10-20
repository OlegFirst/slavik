# DigitalOcean Kubernetes Terraform Variables
# Reference: https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs

variable "do_token" {
  description = "DigitalOcean API Token"
  type        = string
  sensitive   = true
}

variable "cluster_name" {
  description = "Name of the Kubernetes cluster"
  type        = string
  default     = "bcm-platform-cluster"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.cluster_name))
    error_message = "Cluster name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "region" {
  description = "DigitalOcean region for the cluster"
  type        = string
  default     = "nyc1"

  validation {
    condition     = contains(["nyc1", "nyc3", "sfo2", "sfo3", "ams3", "sgp1", "lon1", "fra1", "tor1", "blr1"], var.region)
    error_message = "Must be a valid DigitalOcean region."
  }
}

variable "k8s_version" {
  description = "Kubernetes version (e.g., 1.28.2-do.0). Get available versions: doctl kubernetes options versions"
  type        = string
  default     = "1.28.2-do.0"
}

variable "vpc_uuid" {
  description = "UUID of existing VPC (leave empty to create new VPC)"
  type        = string
  default     = ""
}

variable "ha_control_plane" {
  description = "Enable highly available control plane"
  type        = bool
  default     = true
}

variable "auto_upgrade" {
  description = "Enable automatic upgrades to latest patch version"
  type        = bool
  default     = false
}

variable "node_pool_name" {
  description = "Name of the default node pool"
  type        = string
  default     = "worker-pool"
}

variable "node_size" {
  description = "Droplet size for worker nodes (e.g., s-2vcpu-4gb, s-4vcpu-8gb)"
  type        = string
  default     = "s-4vcpu-8gb"
}

variable "node_count" {
  description = "Initial number of worker nodes"
  type        = number
  default     = 3

  validation {
    condition     = var.node_count >= 1 && var.node_count <= 100
    error_message = "Node count must be between 1 and 100."
  }
}

variable "min_nodes" {
  description = "Minimum number of nodes for autoscaling"
  type        = number
  default     = 2

  validation {
    condition     = var.min_nodes >= 1
    error_message = "Minimum nodes must be at least 1."
  }
}

variable "max_nodes" {
  description = "Maximum number of nodes for autoscaling"
  type        = number
  default     = 10

  validation {
    condition     = var.max_nodes >= var.min_nodes
    error_message = "Maximum nodes must be greater than or equal to minimum nodes."
  }
}

variable "tags" {
  description = "Tags to apply to the cluster and resources"
  type        = list(string)
  default     = ["bcm-platform", "production", "kubernetes"]
}

variable "one_clicks" {
  description = "1-Click applications to install (ingress-nginx, monitoring, cert-manager)"
  type        = list(string)
  default     = ["ingress-nginx", "monitoring"]
}

variable "maintenance_day" {
  description = "Day of week for maintenance window (monday-sunday)"
  type        = string
  default     = "sunday"

  validation {
    condition     = contains(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], var.maintenance_day)
    error_message = "Must be a valid day of the week (lowercase)."
  }
}

variable "maintenance_hour" {
  description = "Start time for maintenance window (HH:MM format, 24-hour)"
  type        = string
  default     = "04:00"

  validation {
    condition     = can(regex("^([0-1][0-9]|2[0-3]):[0-5][0-9]$", var.maintenance_hour))
    error_message = "Must be a valid time in HH:MM format (24-hour)."
  }
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Must be development, staging, or production."
  }
}

# Container Registry Variables
variable "create_container_registry" {
  description = "Create DigitalOcean Container Registry"
  type        = bool
  default     = true
}

variable "registry_name" {
  description = "Name of the container registry"
  type        = string
  default     = "bcm-platform"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.registry_name))
    error_message = "Registry name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "registry_subscription_tier" {
  description = "Container registry subscription tier (starter, basic, professional)"
  type        = string
  default     = "basic"

  validation {
    condition     = contains(["starter", "basic", "professional"], var.registry_subscription_tier)
    error_message = "Must be starter, basic, or professional."
  }
}

# Spaces (Backup) Variables
variable "create_spaces_bucket" {
  description = "Create DigitalOcean Spaces bucket for backups"
  type        = bool
  default     = true
}

variable "spaces_bucket_name" {
  description = "Name of the Spaces bucket for Velero backups"
  type        = string
  default     = "bcm-velero-backups"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.spaces_bucket_name))
    error_message = "Bucket name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "spaces_region" {
  description = "Region for DigitalOcean Spaces bucket"
  type        = string
  default     = "nyc3"

  validation {
    condition     = contains(["nyc3", "sfo3", "sgp1", "fra1", "ams3"], var.spaces_region)
    error_message = "Must be a valid Spaces region."
  }
}

variable "backup_retention_days" {
  description = "Number of days to retain backups in Spaces"
  type        = number
  default     = 30

  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 365
    error_message = "Backup retention must be between 1 and 365 days."
  }
}

# Additional Variables
variable "domain_name" {
  description = "Domain name for the BCM Platform"
  type        = string
  default     = "bcm.example.com"
}

variable "letsencrypt_email" {
  description = "Email address for Let's Encrypt certificate notifications"
  type        = string
  default     = "admin@example.com"
}
