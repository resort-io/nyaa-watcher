import fs from 'fs';

/** @throws {Error} If the directory cannot be created. */
export async function ensureDir(dirPath: string): Promise<void> {
    try {
        await fs.promises.mkdir(dirPath, { recursive: true });
    } catch (error: any) {
        if (error.code && error.code === 'EEXIST') {
            return;
        }
        throw new Error('Error while creating directory: ' + dirPath, { cause: error });
    }
}
