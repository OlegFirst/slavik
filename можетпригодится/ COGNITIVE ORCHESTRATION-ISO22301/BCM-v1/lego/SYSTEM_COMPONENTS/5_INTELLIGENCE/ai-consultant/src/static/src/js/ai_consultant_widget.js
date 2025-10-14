/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";

export class AIConsultantWidget extends Component {
    static template = "bcm_ai_consultant.AIConsultantWidget";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            isConnected: false,
            messages: [],
            currentMessage: ''
        });
    }

    async sendMessage() {
        if (!this.state.currentMessage.trim()) return;

        // Add user message
        this.state.messages.push({
            type: 'user',
            content: this.state.currentMessage,
            timestamp: new Date()
        });

        const userMessage = this.state.currentMessage;
        this.state.currentMessage = '';

        try {
            // Send to AI Consultant
            const response = await this.rpc('/web/dataset/call_kw', {
                model: 'bcm.ai.consultant',
                method: 'get_ai_response',
                args: [[], userMessage],
                kwargs: {}
            });

            // Add AI response
            this.state.messages.push({
                type: 'ai',
                content: response.response || 'No response received',
                timestamp: new Date(),
                confidence: response.confidence || 0
            });

        } catch (error) {
            console.error('AI Consultant Error:', error);
            this.state.messages.push({
                type: 'error',
                content: 'Error connecting to AI Consultant',
                timestamp: new Date()
            });
        }
    }

    onInputChange(ev) {
        this.state.currentMessage = ev.target.value;
    }

    onKeyPress(ev) {
        if (ev.key === 'Enter') {
            this.sendMessage();
        }
    }
}

// Register the widget
registry.category("fields").add("ai_consultant_widget", {
    component: AIConsultantWidget,
});