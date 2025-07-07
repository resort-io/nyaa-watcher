import * as t from "drizzle-orm/sqlite-core"
import { sqliteTable } from "drizzle-orm/sqlite-core"
import { createInsertSchema } from "drizzle-zod";
import { createPartialSchema } from "@/db/partial-schema";
import type { NyaaType } from "@/types";

export const users = sqliteTable("users", {
    id: t.integer().primaryKey({ autoIncrement: true }),
    name: t.text().unique().notNull(),
    type: t.text().$type<NyaaType>().notNull(),
    url: t.text().notNull(),
})

export const usersSchema = createInsertSchema(users);

export const usersPartial = createPartialSchema(usersSchema);
