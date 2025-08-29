import * as fs from 'fs-extra';
import * as path from 'path';

export class FileUtils {
  static async isDirectory(filePath: string): Promise<boolean> {
    try {
      const stats = await fs.stat(filePath);
      return stats.isDirectory();
    } catch {
      return false;
    }
  }

  static async isFile(filePath: string): Promise<boolean> {
    try {
      const stats = await fs.stat(filePath);
      return stats.isFile();
    } catch {
      return false;
    }
  }

  static async getFileExtension(filePath: string): Promise<string> {
    return path.extname(filePath).toLowerCase();
  }

  static async getFileSize(filePath: string): Promise<number> {
    try {
      const stats = await fs.stat(filePath);
      return stats.size;
    } catch {
      return 0;
    }
  }

  static async getFileModificationDate(filePath: string): Promise<Date | null> {
    try {
      const stats = await fs.stat(filePath);
      return stats.mtime;
    } catch {
      return null;
    }
  }

  static async findFilesByPattern(dirPath: string, pattern: RegExp): Promise<string[]> {
    const results: string[] = [];
    
    try {
      const items = await fs.readdir(dirPath, { withFileTypes: true });
      
      for (const item of items) {
        const fullPath = path.join(dirPath, item.name);
        
        if (item.isDirectory()) {
          const subdirResults = await this.findFilesByPattern(fullPath, pattern);
          results.push(...subdirResults);
        } else if (item.isFile() && pattern.test(item.name)) {
          results.push(fullPath);
        }
      }
    } catch (error) {
      console.error(`Помилка сканування директорії ${dirPath}:`, error);
    }
    
    return results;
  }

  static async createDirectoryIfNotExists(dirPath: string): Promise<void> {
    await fs.ensureDir(dirPath);
  }

  static async copyFile(sourcePath: string, destinationPath: string): Promise<void> {
    await fs.ensureDir(path.dirname(destinationPath));
    await fs.copy(sourcePath, destinationPath);
  }

  static async readFileAsText(filePath: string, encoding: BufferEncoding = 'utf-8'): Promise<string> {
    return await fs.readFile(filePath, encoding);
  }

  static async writeTextFile(filePath: string, content: string, encoding: BufferEncoding = 'utf-8'): Promise<void> {
    await fs.ensureDir(path.dirname(filePath));
    await fs.writeFile(filePath, content, encoding);
  }

  static async deleteFile(filePath: string): Promise<void> {
    try {
      await fs.unlink(filePath);
    } catch (error) {
      console.error(`Помилка видалення файлу ${filePath}:`, error);
    }
  }

  static async deleteDirectory(dirPath: string): Promise<void> {
    try {
      await fs.remove(dirPath);
    } catch (error) {
      console.error(`Помилка видалення директорії ${dirPath}:`, error);
    }
  }

  static sanitizePath(inputPath: string): string {
    return path.resolve(inputPath.replace(/[<>:"|?*]/g, '_'));
  }

  static async calculateDirectorySize(dirPath: string): Promise<number> {
    let totalSize = 0;
    
    try {
      const items = await fs.readdir(dirPath, { withFileTypes: true });
      
      for (const item of items) {
        const fullPath = path.join(dirPath, item.name);
        
        if (item.isDirectory()) {
          totalSize += await this.calculateDirectorySize(fullPath);
        } else if (item.isFile()) {
          totalSize += await this.getFileSize(fullPath);
        }
      }
    } catch (error) {
      console.error(`Помилка обчислення розміру директорії ${dirPath}:`, error);
    }
    
    return totalSize;
  }

  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}