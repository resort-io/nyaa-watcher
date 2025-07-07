import * as path from 'node:path';

export const NODE_ENV = process.env.NODE_ENV?.toLowerCase() || 'production';

export const DATABASE_DIR = NODE_ENV === 'development'
    ? path.posix.join(__dirname, '../data')
    : path.posix.normalize('/data');

export const DATABASE_URL = process.env.DATABASE_URL || `file:${path.posix.join(DATABASE_DIR, 'database.db')}`;
