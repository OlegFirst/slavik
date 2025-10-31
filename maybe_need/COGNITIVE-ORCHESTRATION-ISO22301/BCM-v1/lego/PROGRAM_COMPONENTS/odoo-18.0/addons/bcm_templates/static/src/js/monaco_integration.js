/** @odoo-module */

import { Component, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";

// Monaco Editor integration for BCM Templates
export class MonacoBPMNEditor extends Component {
    setup() {
        this.editorRef = useRef("monaco-container");
        this.editor = null;

        onMounted(() => {
            this.initMonacoEditor();
        });
    }

    async initMonacoEditor() {
        // Load Monaco Editor dynamically
        const monaco = await import('monaco-editor');

        // BPMN XML specific configuration
        const editorOptions = {
            value: this.props.value || '',
            language: 'xml',
            theme: 'vs-dark',
            automaticLayout: true,
            minimap: { enabled: true },
            formatOnPaste: true,
            formatOnType: true,
            autoIndent: 'full',
            wordWrap: 'on',
            lineNumbers: 'on',
            fontSize: 14
        };

        // Create editor
        this.editor = monaco.editor.create(this.editorRef.el, editorOptions);

        // BPMN-specific features
        this.setupBPMNFeatures(monaco);

        // Event listeners
        this.editor.onDidChangeModelContent(() => {
            const value = this.editor.getValue();
            this.props.onValueChange(value);
        });
    }

    setupBPMNFeatures(monaco) {
        // Add BPMN XML validation
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyB, () => {
            this.validateBPMN();
        });

        // Add BPMN formatting
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyF, () => {
            this.editor.getAction('editor.action.formatDocument').run();
        });

        // BPMN snippets
        this.addBPMNSnippets(monaco);
    }

    addBPMNSnippets(monaco) {
        // Register BPMN snippets
        monaco.languages.registerCompletionItemProvider('xml', {
            provideCompletionItems: (model, position) => {
                const suggestions = [
                    {
                        label: 'bpmn-process',
                        kind: monaco.languages.CompletionItemKind.Snippet,
                        insertText: `<process id="\${1:process_id}" name="\${2:Process Name}" isExecutable="true">
    <startEvent id="\${3:start}" name="Start"/>
    <userTask id="\${4:task}" name="\${5:Task Name}"/>
    <endEvent id="\${6:end}" name="End"/>
</process>`,
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                        documentation: 'Basic BPMN process template'
                    },
                    {
                        label: 'bpmn-usertask',
                        kind: monaco.languages.CompletionItemKind.Snippet,
                        insertText: `<userTask id="\${1:task_id}" name="\${2:Task Name}">
    <documentation>\${3:Task description}</documentation>
</userTask>`,
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                        documentation: 'BPMN User Task'
                    }
                ];
                return { suggestions };
            }
        });
    }

    validateBPMN() {
        const xml = this.editor.getValue();

        try {
            const parser = new DOMParser();
            const doc = parser.parseFromString(xml, 'application/xml');

            const errors = doc.getElementsByTagName('parsererror');
            if (errors.length > 0) {
                this.showValidationError('Invalid BPMN XML format');
                return false;
            }

            // BPMN-specific validation
            const processes = doc.getElementsByTagName('process');
            if (processes.length === 0) {
                this.showValidationError('No BPMN process found');
                return false;
            }

            this.showValidationSuccess('Valid BPMN XML');
            return true;

        } catch (error) {
            this.showValidationError(`BPMN validation failed: ${error.message}`);
            return false;
        }
    }

    showValidationError(message) {
        // Show error notification
        this.env.services.notification.add(message, { type: 'danger' });
    }

    showValidationSuccess(message) {
        // Show success notification
        this.env.services.notification.add(message, { type: 'success' });
    }

    get value() {
        return this.editor ? this.editor.getValue() : '';
    }

    setValue(value) {
        if (this.editor) {
            this.editor.setValue(value);
        }
    }
}

MonacoBPMNEditor.template = `
    <div class="monaco-bpmn-editor">
        <div class="editor-toolbar">
            <button class="btn btn-sm btn-primary" t-on-click="validateBPMN">
                <i class="fa fa-check"/> Validate BPMN
            </button>
            <button class="btn btn-sm btn-secondary" t-on-click="() => this.editor.getAction('editor.action.formatDocument').run()">
                <i class="fa fa-indent"/> Format
            </button>
        </div>
        <div t-ref="monaco-container" class="monaco-container" style="height: 400px; border: 1px solid #ccc;"/>
    </div>
`;

// Register Monaco BPMN Editor widget
registry.category("fields").add("monaco_bpmn", {
    component: MonacoBPMNEditor,
});