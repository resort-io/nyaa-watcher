import * as t from "drizzle-orm/sqlite-core"
import { sqliteTable } from "drizzle-orm/sqlite-core"
import { createInsertSchema } from "drizzle-zod";
import { createPartialSchema } from "@/db/partial-schema";
import { subscriptions } from "@/db/schema/subscriptions";

export const downloads = sqliteTable("downloads", {
    id: t.integer().primaryKey({ autoIncrement: true }),
    subscriptionID: t.integer().unique().notNull().references(() => subscriptions.id, { onDelete: 'cascade' }),
    success: t.integer({ mode: 'boolean' }).notNull(),
    title: t.text().notNull(),
    page: t.text().notNull(),
    hash: t.text().notNull(),
    datetime: t.text().notNull(),
});

export const downloadsSchema = createInsertSchema(downloads);

export const downloadsPartial = createPartialSchema(downloadsSchema);
