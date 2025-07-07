import * as t from "drizzle-orm/sqlite-core"
import { sqliteTable } from "drizzle-orm/sqlite-core"
import { createInsertSchema } from "drizzle-zod";
import { createPartialSchema } from "@/db/partial-schema";
import { subscriptionsFilters } from "@/db/schema/subscription-filters";

export const filterTags = sqliteTable("filter_tags", {
    id: t.integer().primaryKey({ autoIncrement: true }),
    filterID: t.integer().unique().notNull().references(() => subscriptionsFilters.id, { onDelete: 'cascade' }),
    value: t.text().notNull(),
});

export const filterTagsSchema = createInsertSchema(filterTags);

export const filterTagsPartial = createPartialSchema(filterTagsSchema);
