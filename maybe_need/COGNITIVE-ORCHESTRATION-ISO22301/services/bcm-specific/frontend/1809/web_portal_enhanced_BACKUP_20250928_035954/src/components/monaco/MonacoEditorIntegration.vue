<template>
  <div class="monaco-editor-container">
    <div ref="monacoEditor" class="monaco-editor"></div>
  </div>
</template>

<script>
import * as monaco from 'monaco-editor';

export default {
  name: 'MonacoEditorIntegration',
  props: {
    value: {
      type: String,
      default: ''
    },
    language: {
      type: String,
      default: 'javascript'
    },
    theme: {
      type: String,
      default: 'vs-dark'
    },
    options: {
      type: Object,
      default: () => ({})
    },
    height: {
      type: String,
      default: '400px'
    }
  },
  data() {
    return {
      editor: null
    }
  },
  mounted() {
    this.initMonaco();
  },
  beforeUnmount() {
    if (this.editor) {
      this.editor.dispose();
    }
  },
  watch: {
    value(newValue) {
      if (this.editor && newValue !== this.editor.getValue()) {
        this.editor.setValue(newValue);
      }
    },
    language(newLanguage) {
      if (this.editor) {
        monaco.editor.setModelLanguage(this.editor.getModel(), newLanguage);
      }
    }
  },
  methods: {
    initMonaco() {
      // Configure Monaco Editor for BCM Platform
      const defaultOptions = {
        value: this.value,
        language: this.language,
        theme: this.theme,
        automaticLayout: true,
        minimap: { enabled: true },
        scrollBeyondLastLine: false,
        fontSize: 14,
        lineNumbers: 'on',
        wordWrap: 'on',
        folding: true,
        lineDecorationsWidth: 10,
        lineNumbersMinChars: 3,
        glyphMargin: false,
        ...this.options
      };

      // Special configurations for BCM use cases
      if (this.language === 'xml') {
        // BPMN XML specific settings
        defaultOptions.formatOnPaste = true;
        defaultOptions.formatOnType = true;
        defaultOptions.autoIndent = 'full';
      } else if (this.language === 'json') {
        // JSON schema specific settings
        defaultOptions.validate = true;
        defaultOptions.allowComments = false;
        defaultOptions.trailingCommas = 'error';
      } else if (this.language === 'markdown') {
        // AI prompt specific settings
        defaultOptions.wordWrap = 'on';
        defaultOptions.lineNumbers = 'off';
        defaultOptions.minimap = { enabled: false };
      }

      // Set container height
      this.$refs.monacoEditor.style.height = this.height;

      // Create editor
      this.editor = monaco.editor.create(this.$refs.monacoEditor, defaultOptions);

      // Setup event listeners
      this.editor.onDidChangeModelContent(() => {
        const value = this.editor.getValue();
        this.$emit('change', value);
        this.$emit('update:value', value);
      });

      // Custom commands for BCM Platform
      this.setupBCMCommands();
    },

    setupBCMCommands() {
      // Add BCM-specific Monaco commands

      // BPMN XML validation command
      if (this.language === 'xml') {
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyB, () => {
          this.validateBPMN();
        });
      }

      // JSON schema validation
      if (this.language === 'json') {
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyJ, () => {
          this.validateJSON();
        });
      }

      // AI prompt optimization
      if (this.language === 'markdown') {
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyP, () => {
          this.optimizePrompt();
        });
      }
    },

    validateBPMN() {
      const xml = this.editor.getValue();

      try {
        // Basic XML validation
        const parser = new DOMParser();
        const doc = parser.parseFromString(xml, 'application/xml');

        const errors = doc.getElementsByTagName('parsererror');
        if (errors.length > 0) {
          this.$emit('validation-error', 'Invalid BPMN XML format');
          return;
        }

        // BPMN-specific validation
        const processes = doc.getElementsByTagName('process');
        if (processes.length === 0) {
          this.$emit('validation-error', 'No BPMN process found');
          return;
        }

        this.$emit('validation-success', 'Valid BPMN XML');

      } catch (error) {
        this.$emit('validation-error', `BPMN validation failed: ${error.message}`);
      }
    },

    validateJSON() {
      const json = this.editor.getValue();

      try {
        JSON.parse(json);
        this.$emit('validation-success', 'Valid JSON schema');
      } catch (error) {
        this.$emit('validation-error', `Invalid JSON: ${error.message}`);
      }
    },

    optimizePrompt() {
      const prompt = this.editor.getValue();

      // Send to AI for prompt optimization
      this.$emit('optimize-prompt', prompt);
    },

    getValue() {
      return this.editor ? this.editor.getValue() : this.value;
    },

    setValue(value) {
      if (this.editor) {
        this.editor.setValue(value);
      }
    },

    focus() {
      if (this.editor) {
        this.editor.focus();
      }
    },

    format() {
      if (this.editor) {
        this.editor.getAction('editor.action.formatDocument').run();
      }
    }
  }
}
</script>

<style scoped>
.monaco-editor-container {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.monaco-editor {
  width: 100%;
}

/* BCM Platform Monaco theme customizations */
.monaco-editor .margin {
  background-color: #f8f9fa;
}

.monaco-editor .current-line {
  background-color: rgba(0, 123, 255, 0.1);
}
</style>