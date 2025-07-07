import * as t from "drizzle-orm/sqlite-core"
import { sqliteTable } from "drizzle-orm/sqlite-core"
import { createInsertSchema } from "drizzle-zod";
import { createPartialSchema } from "@/db/partial-schema";
import type { WebhookService } from "@/types.ts";

export const webhooks = sqliteTable("webhooks", {
    id: t.integer().primaryKey({ autoIncrement: true }),
    name: t.text().unique().notNull(),
    type: t.text().$type<WebhookService>().notNull(),
});

export const webhooksSchema = createInsertSchema(webhooks);

export const webhooksPartial = createPartialSchema(webhooksSchema);
