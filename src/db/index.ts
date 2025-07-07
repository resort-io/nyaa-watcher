// https://orm.drizzle.team/docs/get-started/sqlite-new
import 'dotenv/config';
import { drizzle } from 'drizzle-orm/libsql';
import { createClient, type Config } from '@libsql/client';
import { DATABASE_DIR, DATABASE_URL } from "@/lib/utils.ts";
import { ensureDir } from '@/utils/ensure_dir';

const connection: Config = {
    url: DATABASE_URL,
    authToken: process.env.DATABASE_AUTH_TOKEN || '',
}

try {
    await ensureDir(DATABASE_DIR);
} catch (e) {
    throw e // TODO: Use logger
}

export const client = () => createClient(connection);
export const pool = drizzle({ connection });
