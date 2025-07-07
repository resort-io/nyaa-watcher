import { client } from '@/db';
import { migrate } from '@/db/migrate';
import type { DatabaseError } from "@/types";

export const init = async (): Promise<{
    error: null,
} | {
    error: Error,
    type: DatabaseError,
}> => {
    const db = client();

    try {
        await migrate(db);
    } catch (e) {
        console.error('[DB INIT] Migration failed:', e)
        db.close()
        return {
            error: e as Error,
            type: 'migration',
        }
    }

    // TODO: Seeding

    db.close()

    return {
        error: null,
    }
}
