import * as t from "drizzle-orm/sqlite-core"
import { sqliteTable } from "drizzle-orm/sqlite-core"
import { createInsertSchema } from "drizzle-zod";
import { createPartialSchema } from "@/db/partial-schema";

export const config = sqliteTable("config", {
    key: t.text().primaryKey().notNull(),
    value: t.text(),
});

export const configSchema = createInsertSchema(config);

export const configPartial = createPartialSchema(configSchema);
