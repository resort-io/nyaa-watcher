import * as path from 'node:path';
import { readFile } from 'node:fs/promises';
import type { Client } from "@libsql/core/api";

export const MIGRATION_DIR = path.posix.join(__dirname, 'migrations');
export const MIGRATION_FILENAME = '0000_init.sql';
export const MIGRATION_FILEPATH = path.posix.join(MIGRATION_DIR, MIGRATION_FILENAME)

export const migrate = async (db: Client): Promise<void> => {
    console.log('[MIGRATION] Starting migration...')

    console.log(`[MIGRATION] Reading filepath: ${MIGRATION_FILEPATH}`)
    const migrations = await readFile(MIGRATION_FILEPATH, 'utf8')

    if (!migrations) {
        throw new Error(`[MIGRATION] Migration file is empty: ${MIGRATION_FILEPATH}`)
    }

    console.log('[MIGRATION] Executing migration statements...')

    const statements = migrations
        .replace(/[\n\t\r`]/g, '')
        .split('--> statement-breakpoint')
        .filter(statement => statement.trim().length > 0)

    for (const statement of statements) {
        const formatted = statement.trim()
            .replace(/(CREATE TABLE)/, 'CREATE TABLE IF NOT EXISTS')
            .replace(/(CREATE UNIQUE INDEX)/, 'CREATE UNIQUE INDEX IF NOT EXISTS')

        console.log(`[MIGRATION] -> ${formatted}`)
        await db.execute(formatted)
    }

    console.log('[MIGRATION] Successfully completed migration!')
}
