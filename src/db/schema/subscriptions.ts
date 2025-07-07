import * as t from "drizzle-orm/sqlite-core"
import { sqliteTable } from "drizzle-orm/sqlite-core"
import { createInsertSchema } from "drizzle-zod";
import { createPartialSchema } from "@/db/partial-schema";
import { users } from "@/db/schema/users";

export const subscriptions = sqliteTable("webhooks", {
    id: t.integer().primaryKey({ autoIncrement: true }),
    userID: t.integer().unique().notNull().references(() => users.id, { onDelete: 'cascade' }),
    name: t.text().unique().notNull(),
    interval: t.integer().notNull(),
});

export const subscriptionsSchema = createInsertSchema(subscriptions);

export const subscriptionsPartial = createPartialSchema(subscriptionsSchema);
