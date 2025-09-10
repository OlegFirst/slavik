export interface TextError {
    type: 'spelling' | 'grammar' | 'punctuation' | 'style';
    line: number;
    column: number;
    originalText: string;
    correctedText: string;
    description: string;
    severity: 'low' | 'medium' | 'high';
}
export interface DocumentStructure {
    type: 'markdown' | 'text' | 'html';
    headers: HeaderInfo[];
    lists: ListInfo[];
    codeBlocks: CodeBlockInfo[];
    links: LinkInfo[];
    formatting: FormattingInfo[];
}
export interface HeaderInfo {
    level: number;
    text: string;
    line: number;
    originalMarkdown: string;
}
export interface ListInfo {
    type: 'ordered' | 'unordered';
    items: string[];
    startLine: number;
    endLine: number;
}
export interface CodeBlockInfo {
    language?: string;
    content: string;
    startLine: number;
    endLine: number;
}
export interface LinkInfo {
    text: string;
    url: string;
    line: number;
    originalMarkdown: string;
}
export interface FormattingInfo {
    type: 'bold' | 'italic' | 'code';
    text: string;
    line: number;
    originalMarkdown: string;
}
export interface CheckResult {
    errors: TextError[];
    correctedText: string;
    structure: DocumentStructure;
    summary: {
        totalErrors: number;
        fixedErrors: number;
        errorsByType: Record<string, number>;
    };
}
export declare class DocumentChecker {
    private grammarRules;
    private spellingDictionary;
    private ukrainianRules;
    constructor();
    private initializeRules;
    private loadDictionary;
    checkDocument(filePath: string): Promise<CheckResult>;
    checkText(content: string, fileExtension?: string): CheckResult;
    private getDocumentType;
    private parseDocumentStructure;
    private parseMarkdownStructure;
    private extractTextBlocks;
    private shouldSkipLine;
    private stripMarkdownFormatting;
    private checkTextBlock;
    private checkGrammar;
    private checkSpelling;
    private checkPunctuation;
    private getSuggestion;
    private levenshteinDistance;
    private shouldAutoFix;
    private groupErrorsByType;
    saveCheckedDocument(filePath: string, correctedContent: string, originalBackup?: boolean): Promise<string>;
}
//# sourceMappingURL=DocumentChecker.d.ts.map