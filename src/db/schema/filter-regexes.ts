import * as t from "drizzle-orm/sqlite-core"
import { sqliteTable } from "drizzle-orm/sqlite-core"
import { createInsertSchema } from "drizzle-zod";
import { createPartialSchema } from "@/db/partial-schema";
import { subscriptionsFilters } from "@/db/schema/subscription-filters";

export const filterRegexes = sqliteTable("filter_regexes", {
    id: t.integer().primaryKey({ autoIncrement: true }),
    filterID: t.integer().unique().notNull().references(() => subscriptionsFilters.id, { onDelete: 'cascade' }),
    value: t.text().notNull(),
});

export const filterRegexesSchema = createInsertSchema(filterRegexes);

export const filterRegexesPartial = createPartialSchema(filterRegexesSchema);
