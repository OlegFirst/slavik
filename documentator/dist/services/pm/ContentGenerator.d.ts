import { ContentPrompt, ContentRequest, ContentResponse, PromptField } from './types';
export declare class ContentGenerator {
    private prompts;
    constructor();
    private loadBuiltInPrompts;
    registerPrompt(prompt: ContentPrompt): void;
    getPrompt(id: string): ContentPrompt | undefined;
    getAllPrompts(): ContentPrompt[];
    getPromptsByCategory(category: string): ContentPrompt[];
    validateFieldData(field: PromptField, value: any): {
        valid: boolean;
        error?: string;
    };
    validateRequest(request: ContentRequest): {
        valid: boolean;
        errors: string[];
    };
    generateContent(request: ContentRequest): Promise<ContentResponse>;
    private processPrompt;
    private generateMockContent;
    private generatePressReleaseMock;
    private generateProjectPointMock;
    private getAnnouncementTypeText;
    private generateSubheadline;
    private generateAchievementTitle;
    private saveContent;
}
//# sourceMappingURL=ContentGenerator.d.ts.map