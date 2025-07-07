import * as t from "drizzle-orm/sqlite-core"
import { sqliteTable } from "drizzle-orm/sqlite-core"
import { createInsertSchema } from "drizzle-zod";
import { createPartialSchema } from "@/db/partial-schema";
import { subscriptionsFilters } from "@/db/schema/subscription-filters";
import { webhooks } from "@/db/schema/webhooks";

export const filterWebhooks = sqliteTable("filter_webhooks", {
    id: t.integer().primaryKey({ autoIncrement: true }),
    filterID: t.integer().unique().notNull().references(() => subscriptionsFilters.id, { onDelete: 'cascade' }),
    webhookID: t.integer().unique().notNull().references(() => webhooks.id, { onDelete: 'cascade' }),
});

export const filterWebhooksSchema = createInsertSchema(filterWebhooks);

export const filterWebhooksPartial = createPartialSchema(filterWebhooksSchema);
