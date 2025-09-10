"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.FileUtils = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class FileUtils {
    static async isDirectory(filePath) {
        try {
            const stats = await fs.stat(filePath);
            return stats.isDirectory();
        }
        catch {
            return false;
        }
    }
    static async isFile(filePath) {
        try {
            const stats = await fs.stat(filePath);
            return stats.isFile();
        }
        catch {
            return false;
        }
    }
    static async getFileExtension(filePath) {
        return path.extname(filePath).toLowerCase();
    }
    static async getFileSize(filePath) {
        try {
            const stats = await fs.stat(filePath);
            return stats.size;
        }
        catch {
            return 0;
        }
    }
    static async getFileModificationDate(filePath) {
        try {
            const stats = await fs.stat(filePath);
            return stats.mtime;
        }
        catch {
            return null;
        }
    }
    static async findFilesByPattern(dirPath, pattern) {
        const results = [];
        try {
            const items = await fs.readdir(dirPath, { withFileTypes: true });
            for (const item of items) {
                const fullPath = path.join(dirPath, item.name);
                if (item.isDirectory()) {
                    const subdirResults = await this.findFilesByPattern(fullPath, pattern);
                    results.push(...subdirResults);
                }
                else if (item.isFile() && pattern.test(item.name)) {
                    results.push(fullPath);
                }
            }
        }
        catch (error) {
            console.error(`Помилка сканування директорії ${dirPath}:`, error);
        }
        return results;
    }
    static async createDirectoryIfNotExists(dirPath) {
        await fs.ensureDir(dirPath);
    }
    static async copyFile(sourcePath, destinationPath) {
        await fs.ensureDir(path.dirname(destinationPath));
        await fs.copy(sourcePath, destinationPath);
    }
    static async readFileAsText(filePath, encoding = 'utf-8') {
        return await fs.readFile(filePath, encoding);
    }
    static async writeTextFile(filePath, content, encoding = 'utf-8') {
        await fs.ensureDir(path.dirname(filePath));
        await fs.writeFile(filePath, content, encoding);
    }
    static async deleteFile(filePath) {
        try {
            await fs.unlink(filePath);
        }
        catch (error) {
            console.error(`Помилка видалення файлу ${filePath}:`, error);
        }
    }
    static async deleteDirectory(dirPath) {
        try {
            await fs.remove(dirPath);
        }
        catch (error) {
            console.error(`Помилка видалення директорії ${dirPath}:`, error);
        }
    }
    static sanitizePath(inputPath) {
        return path.resolve(inputPath.replace(/[<>:"|?*]/g, '_'));
    }
    static async calculateDirectorySize(dirPath) {
        let totalSize = 0;
        try {
            const items = await fs.readdir(dirPath, { withFileTypes: true });
            for (const item of items) {
                const fullPath = path.join(dirPath, item.name);
                if (item.isDirectory()) {
                    totalSize += await this.calculateDirectorySize(fullPath);
                }
                else if (item.isFile()) {
                    totalSize += await this.getFileSize(fullPath);
                }
            }
        }
        catch (error) {
            console.error(`Помилка обчислення розміру директорії ${dirPath}:`, error);
        }
        return totalSize;
    }
    static formatFileSize(bytes) {
        if (bytes === 0)
            return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}
exports.FileUtils = FileUtils;
//# sourceMappingURL=FileUtils.js.map