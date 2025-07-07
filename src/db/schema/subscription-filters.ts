import * as t from "drizzle-orm/sqlite-core"
import { sqliteTable } from "drizzle-orm/sqlite-core"
import { createInsertSchema } from "drizzle-zod";
import { createPartialSchema } from "@/db/partial-schema";
import { subscriptions } from "@/db/schema/subscriptions";

export const subscriptionsFilters = sqliteTable("subscription_filters", {
    id: t.integer().primaryKey({ autoIncrement: true }),
    subscriptionID: t.integer().unique().notNull().references(() => subscriptions.id, { onDelete: 'cascade' }),
    name: t.text().unique().notNull(),
});

export const subscriptionFiltersSchema = createInsertSchema(subscriptionsFilters);

export const subscriptionFiltersPartial = createPartialSchema(subscriptionFiltersSchema);
