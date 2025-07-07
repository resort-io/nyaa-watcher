import * as t from "drizzle-orm/sqlite-core"
import { sqliteTable } from "drizzle-orm/sqlite-core"
import { createInsertSchema } from "drizzle-zod";
import { createPartialSchema } from "@/db/partial-schema";
import { webhooks } from "@/db/schema/webhooks";

export const webhookConfig = sqliteTable("webhook_config", {
    webhookID: t.integer().notNull().references(() => webhooks.id, { onDelete: 'cascade' }),
    key: t.text().primaryKey().notNull(),
    value: t.text(),
    description: t.text(),
});

export const webhookConfigSchema = createInsertSchema(webhookConfig);

export const webhookConfigPartial = createPartialSchema(webhookConfigSchema);
