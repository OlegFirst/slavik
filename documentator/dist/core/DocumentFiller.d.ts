export interface FillableField {
    id: string;
    type: 'text' | 'date' | 'number' | 'select' | 'multiline' | 'boolean' | 'list' | 'table';
    placeholder: string;
    originalText: string;
    position: {
        line: number;
        column: number;
        length: number;
    };
    context: {
        beforeText: string;
        afterText: string;
        sectionTitle?: string;
    };
    validation?: {
        required?: boolean;
        format?: string;
        minLength?: number;
        maxLength?: number;
        options?: string[];
    };
    suggestedQuestions: string[];
    relatedFields?: string[];
}
export interface SourceDocument {
    path: string;
    type: 'reference' | 'template' | 'data';
    content: string;
    extractedData: Map<string, any>;
    confidence: number;
}
export interface FillSession {
    sessionId: string;
    targetDocument: string;
    fields: FillableField[];
    sourceDocuments: SourceDocument[];
    currentFieldIndex: number;
    responses: Map<string, any>;
    status: 'analyzing' | 'questioning' | 'filling' | 'completed' | 'cancelled';
    createdAt: Date;
    lastUpdated: Date;
}
export interface QuestionResponse {
    fieldId: string;
    answer: any;
    confidence: number;
    source: 'user' | 'auto' | 'document';
}
export declare class DocumentFiller {
    private sessions;
    private fieldPatterns;
    private contextAnalyzer;
    constructor();
    private initializePatterns;
    analyzeDocument(filePath: string, sourceDocuments?: string[]): Promise<FillSession>;
    private detectFillableFields;
    private createFieldFromMatch;
    private determineFieldType;
    private generateQuestionsForField;
    private determineValidation;
    private isDuplicateField;
    private identifyRelatedFields;
    private analyzeSourceDocument;
    private findMatchingData;
    private extractKeywords;
    private calculateMatchScore;
    private determineDocumentType;
    private autoFillFromSources;
    getNextQuestion(sessionId: string): Promise<{
        field: FillableField;
        question: string;
        context: any;
        isLastField: boolean;
    } | null>;
    private generateContextualQuestion;
    private buildQuestionContext;
    private generateExamples;
    submitResponse(sessionId: string, fieldId: string, answer: any): Promise<{
        accepted: boolean;
        error?: string;
        nextField?: {
            field: FillableField;
            question: string;
            context: any;
        };
    }>;
    private validateResponse;
    fillDocument(sessionId: string): Promise<{
        success: boolean;
        filledDocument?: string;
        outputPath?: string;
        error?: string;
    }>;
    private replaceFieldInContent;
    getSession(sessionId: string): FillSession | undefined;
    getAllSessions(): FillSession[];
    cancelSession(sessionId: string): boolean;
    private generateSessionId;
}
//# sourceMappingURL=DocumentFiller.d.ts.map