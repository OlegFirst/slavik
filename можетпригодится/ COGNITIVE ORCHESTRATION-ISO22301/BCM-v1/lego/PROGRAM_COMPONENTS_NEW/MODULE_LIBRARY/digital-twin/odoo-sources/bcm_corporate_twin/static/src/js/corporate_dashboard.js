/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

/**
 * Corporate Digital Twin Dashboard Component
 */
export class CorporateDashboard extends Component {
    static template = "bcm_corporate_twin.CorporateDashboard";

    setup() {
        this.metrics = {
            financialHealth: 85,
            supplyChainResilience: 72,
            complianceScore: 94,
            operationalEfficiency: 78
        };
    }

    /**
     * Refresh dashboard data
     */
    refreshDashboard() {
        // Implementation for refreshing dashboard metrics
        console.log("Refreshing corporate dashboard...");
    }

    /**
     * Navigate to financial modeling
     */
    openFinancialModel() {
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'bcm.corporate.financial.model',
            view_mode: 'list,form',
            target: 'current',
        });
    }

    /**
     * Navigate to supply chain analysis
     */
    openSupplyChain() {
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'bcm.corporate.supply.chain',
            view_mode: 'list,form',
            target: 'current',
        });
    }

    /**
     * Navigate to compliance tracking
     */
    openCompliance() {
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'bcm.corporate.compliance',
            view_mode: 'list,form',
            target: 'current',
        });
    }
}

registry.category("actions").add("corporate_dashboard", CorporateDashboard);