import * as t from "drizzle-orm/sqlite-core"
import { sqliteTable } from "drizzle-orm/sqlite-core"
import { createInsertSchema } from "drizzle-zod";
import { createPartialSchema } from "@/db/partial-schema";
import { subscriptions } from "@/db/schema/subscriptions";
import { webhooks } from "@/db/schema/webhooks";

export const subscriptionWebhooks = sqliteTable("subscription_webhooks", {
    id: t.integer().primaryKey({ autoIncrement: true }),
    subscriptionID: t.integer().unique().notNull().references(() => subscriptions.id, { onDelete: 'cascade' }),
    webhookID: t.integer().unique().notNull().references(() => webhooks.id, { onDelete: 'cascade' }),
});

export const subscriptionWebhooksSchema = createInsertSchema(subscriptionWebhooks);

export const subscriptionWebhooksPartial = createPartialSchema(subscriptionWebhooksSchema);
