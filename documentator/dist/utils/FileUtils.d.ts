export declare class FileUtils {
    static isDirectory(filePath: string): Promise<boolean>;
    static isFile(filePath: string): Promise<boolean>;
    static getFileExtension(filePath: string): Promise<string>;
    static getFileSize(filePath: string): Promise<number>;
    static getFileModificationDate(filePath: string): Promise<Date | null>;
    static findFilesByPattern(dirPath: string, pattern: RegExp): Promise<string[]>;
    static createDirectoryIfNotExists(dirPath: string): Promise<void>;
    static copyFile(sourcePath: string, destinationPath: string): Promise<void>;
    static readFileAsText(filePath: string, encoding?: BufferEncoding): Promise<string>;
    static writeTextFile(filePath: string, content: string, encoding?: BufferEncoding): Promise<void>;
    static deleteFile(filePath: string): Promise<void>;
    static deleteDirectory(dirPath: string): Promise<void>;
    static sanitizePath(inputPath: string): string;
    static calculateDirectorySize(dirPath: string): Promise<number>;
    static formatFileSize(bytes: number): string;
}
//# sourceMappingURL=FileUtils.d.ts.map