#!/usr/bin/env bash

################################################################################
# BCM Platform - Kubernetes Context Switcher
#
# Easily switch between different Kubernetes clusters:
# - local (minikube/kind/docker-desktop)
# - gke-prod (Google Kubernetes Engine - Production)
# - gke-staging (Google Kubernetes Engine - Staging)
# - do-prod (DigitalOcean Kubernetes - Production)
# - do-staging (DigitalOcean Kubernetes - Staging)
#
# Usage:
#   ./switch-context.sh                    # Interactive mode
#   ./switch-context.sh <context-name>     # Direct switch
#   ./switch-context.sh --list             # List all contexts
#   ./switch-context.sh --current          # Show current context
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $*"; }
log_success() { echo -e "${GREEN}✅${NC} $*"; }
log_warning() { echo -e "${YELLOW}⚠️${NC}  $*"; }
log_error() { echo -e "${RED}❌${NC} $*"; }

show_banner() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  BCM Platform - Kubernetes Context Switcher"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

get_current_context() {
    kubectl config current-context 2>/dev/null || echo "none"
}

get_all_contexts() {
    kubectl config get-contexts -o name
}

get_bcm_contexts() {
    # Get all contexts and filter for BCM-related ones
    get_all_contexts | grep -E "(bcm|minikube|kind|docker-desktop)" || true
}

show_current_context() {
    local current=$(get_current_context)

    echo -e "${CYAN}Current Context:${NC}"
    echo ""

    if [[ "$current" == "none" ]]; then
        log_warning "No active context"
        return
    fi

    # Get cluster info
    local cluster=$(kubectl config view -o jsonpath="{.contexts[?(@.name=='$current')].context.cluster}")
    local user=$(kubectl config view -o jsonpath="{.contexts[?(@.name=='$current')].context.user}")
    local namespace=$(kubectl config view -o jsonpath="{.contexts[?(@.name=='$current')].context.namespace}")

    echo -e "  ${GREEN}✓${NC} Name:      $current"
    echo -e "  ${BLUE}•${NC} Cluster:   $cluster"
    echo -e "  ${BLUE}•${NC} User:      $user"
    echo -e "  ${BLUE}•${NC} Namespace: ${namespace:-default}"

    # Try to get cluster info
    if kubectl cluster-info &> /dev/null; then
        echo ""
        echo -e "${CYAN}Cluster Status:${NC}"
        local api_server=$(kubectl cluster-info | grep "Kubernetes control plane" | awk '{print $NF}')
        echo -e "  ${GREEN}✓${NC} API Server: $api_server"

        # Get node count
        local node_count=$(kubectl get nodes --no-headers 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  ${GREEN}✓${NC} Nodes:      $node_count"

        # Get version
        local version=$(kubectl version --short 2>/dev/null | grep "Server Version" | awk '{print $3}' || echo "unknown")
        echo -e "  ${GREEN}✓${NC} Version:    $version"
    else
        echo ""
        log_warning "Cluster not reachable"
    fi

    echo ""
}

list_all_contexts() {
    echo -e "${CYAN}Available Contexts:${NC}"
    echo ""

    local current=$(get_current_context)
    local contexts=$(get_all_contexts)

    if [[ -z "$contexts" ]]; then
        log_warning "No contexts configured"
        echo ""
        log_info "Set up a context:"
        echo "  • Local: ./infrastructure/kubernetes/scripts/local-setup.sh"
        echo "  • GKE:   gcloud container clusters get-credentials <cluster-name> --region <region>"
        echo "  • DO:    doctl kubernetes cluster kubeconfig save <cluster-name>"
        return
    fi

    # Group contexts by platform
    local -a local_contexts=()
    local -a gke_contexts=()
    local -a do_contexts=()
    local -a other_contexts=()

    while IFS= read -r ctx; do
        if [[ "$ctx" =~ (minikube|kind|docker-desktop) ]]; then
            local_contexts+=("$ctx")
        elif [[ "$ctx" =~ gke ]]; then
            gke_contexts+=("$ctx")
        elif [[ "$ctx" =~ do- ]]; then
            do_contexts+=("$ctx")
        else
            other_contexts+=("$ctx")
        fi
    done <<< "$contexts"

    # Print local contexts
    if [[ ${#local_contexts[@]} -gt 0 ]]; then
        echo -e "${MAGENTA}Local Clusters:${NC}"
        for ctx in "${local_contexts[@]}"; do
            if [[ "$ctx" == "$current" ]]; then
                echo -e "  ${GREEN}▶${NC} $ctx ${GREEN}(active)${NC}"
            else
                echo -e "  ${BLUE}•${NC} $ctx"
            fi
        done
        echo ""
    fi

    # Print GKE contexts
    if [[ ${#gke_contexts[@]} -gt 0 ]]; then
        echo -e "${MAGENTA}Google Kubernetes Engine (GKE):${NC}"
        for ctx in "${gke_contexts[@]}"; do
            if [[ "$ctx" == "$current" ]]; then
                echo -e "  ${GREEN}▶${NC} $ctx ${GREEN}(active)${NC}"
            else
                echo -e "  ${BLUE}•${NC} $ctx"
            fi
        done
        echo ""
    fi

    # Print DigitalOcean contexts
    if [[ ${#do_contexts[@]} -gt 0 ]]; then
        echo -e "${MAGENTA}DigitalOcean Kubernetes (DOKS):${NC}"
        for ctx in "${do_contexts[@]}"; do
            if [[ "$ctx" == "$current" ]]; then
                echo -e "  ${GREEN}▶${NC} $ctx ${GREEN}(active)${NC}"
            else
                echo -e "  ${BLUE}•${NC} $ctx"
            fi
        done
        echo ""
    fi

    # Print other contexts
    if [[ ${#other_contexts[@]} -gt 0 ]]; then
        echo -e "${MAGENTA}Other Clusters:${NC}"
        for ctx in "${other_contexts[@]}"; do
            if [[ "$ctx" == "$current" ]]; then
                echo -e "  ${GREEN}▶${NC} $ctx ${GREEN}(active)${NC}"
            else
                echo -e "  ${BLUE}•${NC} $ctx"
            fi
        done
        echo ""
    fi
}

switch_context() {
    local target_context="$1"

    # Check if context exists
    if ! kubectl config get-contexts -o name | grep -q "^${target_context}$"; then
        log_error "Context '$target_context' not found"
        echo ""
        log_info "Available contexts:"
        get_all_contexts | sed 's/^/  • /'
        return 1
    fi

    local current=$(get_current_context)

    if [[ "$target_context" == "$current" ]]; then
        log_warning "Already using context: $target_context"
        return 0
    fi

    # Switch context
    log_info "Switching from '$current' to '$target_context'..."
    kubectl config use-context "$target_context"

    # Verify switch
    if kubectl cluster-info &> /dev/null; then
        log_success "Context switched successfully!"
        echo ""
        show_current_context
    else
        log_warning "Context switched but cluster is not reachable"
        log_info "The cluster might be stopped or you may need to authenticate"
    fi
}

interactive_mode() {
    show_banner
    list_all_contexts

    local contexts=$(get_all_contexts)
    if [[ -z "$contexts" ]]; then
        return 1
    fi

    echo -e "${CYAN}Select a context to switch to:${NC}"
    echo ""

    # Create numbered list
    local -a context_array=()
    local i=1
    while IFS= read -r ctx; do
        context_array+=("$ctx")
        echo "  $i) $ctx"
        ((i++))
    done <<< "$contexts"

    echo ""
    echo "  0) Cancel"
    echo ""

    # Get user selection
    read -p "Enter number: " selection

    if [[ "$selection" == "0" ]]; then
        log_info "Cancelled"
        return 0
    fi

    # Validate selection
    if ! [[ "$selection" =~ ^[0-9]+$ ]] || [[ "$selection" -lt 1 ]] || [[ "$selection" -gt ${#context_array[@]} ]]; then
        log_error "Invalid selection: $selection"
        return 1
    fi

    # Switch to selected context
    local selected_context="${context_array[$((selection-1))]}"
    echo ""
    switch_context "$selected_context"
}

create_context_aliases() {
    local shell_rc=""

    # Detect shell
    if [[ -n "${BASH_VERSION:-}" ]]; then
        shell_rc="$HOME/.bashrc"
    elif [[ -n "${ZSH_VERSION:-}" ]]; then
        shell_rc="$HOME/.zshrc"
    else
        log_warning "Unknown shell, cannot create aliases"
        return 1
    fi

    echo ""
    log_info "Creating context switch aliases..."

    local aliases_file="$HOME/.bcm-k8s-aliases"

    cat > "$aliases_file" <<'EOF'
# BCM Platform - Kubernetes Context Aliases
# Source: infrastructure/kubernetes/scripts/switch-context.sh

# Quick context switching
alias k8s-local='kubectl config use-context minikube || kubectl config use-context kind-bcm-platform || kubectl config use-context docker-desktop'
alias k8s-gke='kubectl config use-context $(kubectl config get-contexts -o name | grep gke | head -n1)'
alias k8s-do='kubectl config use-context $(kubectl config get-contexts -o name | grep do- | head -n1)'

# Context info
alias k8s-current='kubectl config current-context'
alias k8s-contexts='kubectl config get-contexts'
alias k8s-info='kubectl cluster-info && kubectl get nodes'

# BCM Platform namespace shortcuts
alias k-bcm='kubectl -n bcm-platform'
alias k-bcm-logs='kubectl -n bcm-platform logs'
alias k-bcm-get='kubectl -n bcm-platform get'
alias k-bcm-describe='kubectl -n bcm-platform describe'

# Quick status checks
alias bcm-status='kubectl -n bcm-platform get pods'
alias bcm-health='kubectl -n bcm-platform exec deployment/orchestration-service -- curl -sf http://localhost:8002/health'
alias bcm-logs='kubectl -n bcm-platform logs deployment/orchestration-service -f'
EOF

    # Add source line to shell rc if not already present
    if ! grep -q "source $aliases_file" "$shell_rc"; then
        echo "" >> "$shell_rc"
        echo "# BCM Platform Kubernetes aliases" >> "$shell_rc"
        echo "[ -f $aliases_file ] && source $aliases_file" >> "$shell_rc"
        log_success "Aliases added to $shell_rc"
    else
        log_info "Aliases already configured in $shell_rc"
    fi

    echo ""
    log_info "Reload your shell or run: source $shell_rc"
    echo ""
    log_info "Available aliases:"
    echo "  • k8s-local      - Switch to local cluster"
    echo "  • k8s-gke        - Switch to GKE cluster"
    echo "  • k8s-do         - Switch to DigitalOcean cluster"
    echo "  • k8s-current    - Show current context"
    echo "  • k8s-contexts   - List all contexts"
    echo "  • k-bcm          - kubectl -n bcm-platform"
    echo "  • bcm-status     - Show BCM Platform pods"
    echo "  • bcm-health     - Check orchestration health"
    echo "  • bcm-logs       - Follow orchestration logs"
}

show_help() {
    cat <<EOF
BCM Platform - Kubernetes Context Switcher

USAGE:
    ./switch-context.sh [options] [context-name]

OPTIONS:
    -h, --help          Show this help message
    -l, --list          List all available contexts
    -c, --current       Show current context info
    -a, --aliases       Create shell aliases for quick switching
    -i, --interactive   Interactive mode (default if no args)

ARGUMENTS:
    context-name        Name of context to switch to

EXAMPLES:
    # Interactive mode
    ./switch-context.sh

    # Direct switch
    ./switch-context.sh minikube
    ./switch-context.sh gke_my-project_us-central1_bcm-platform-prod

    # List contexts
    ./switch-context.sh --list

    # Show current
    ./switch-context.sh --current

    # Create aliases
    ./switch-context.sh --aliases

SHELL ALIASES:
    After running --aliases, you can use:
    • k8s-local      - Quick switch to local cluster
    • k8s-gke        - Quick switch to GKE
    • k8s-do         - Quick switch to DigitalOcean
    • k-bcm          - kubectl -n bcm-platform shortcut
    • bcm-status     - Check BCM Platform status
    • bcm-health     - Check orchestration health

EOF
}

main() {
    local mode="interactive"
    local target_context=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -l|--list)
                mode="list"
                shift
                ;;
            -c|--current)
                mode="current"
                shift
                ;;
            -a|--aliases)
                mode="aliases"
                shift
                ;;
            -i|--interactive)
                mode="interactive"
                shift
                ;;
            *)
                mode="switch"
                target_context="$1"
                shift
                ;;
        esac
    done

    # Execute based on mode
    case "$mode" in
        list)
            show_banner
            list_all_contexts
            ;;
        current)
            show_banner
            show_current_context
            ;;
        aliases)
            show_banner
            create_context_aliases
            ;;
        switch)
            show_banner
            switch_context "$target_context"
            ;;
        interactive)
            interactive_mode
            ;;
    esac
}

main "$@"
