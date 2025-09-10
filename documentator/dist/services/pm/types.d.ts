export interface ContentPrompt {
    id: string;
    name: string;
    description: string;
    systemPrompt: string;
    requiredFields: PromptField[];
    optionalFields?: PromptField[];
    outputFormat: 'markdown' | 'text' | 'html';
    category: string;
}
export interface PromptField {
    name: string;
    type: 'text' | 'textarea' | 'select' | 'multiselect' | 'date' | 'number';
    description: string;
    required: boolean;
    placeholder?: string;
    options?: string[];
    validation?: {
        minLength?: number;
        maxLength?: number;
        pattern?: string;
    };
}
export interface ContentRequest {
    promptId: string;
    data: Record<string, any>;
    outputPath?: string;
}
export interface ContentResponse {
    success: boolean;
    content?: string;
    outputPath?: string;
    error?: string;
    generatedAt: Date;
}
export interface PMConfig {
    openaiApiKey?: string;
    defaultModel?: string;
    outputDirectory?: string;
    customPrompts?: ContentPrompt[];
}
//# sourceMappingURL=types.d.ts.map