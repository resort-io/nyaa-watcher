// https://orm.drizzle.team/docs/drizzle-config-file#driver
import { defineConfig } from "drizzle-kit";

export default defineConfig({
    dialect: "sqlite",
    dbCredentials: {
        url: 'file:./data/database.db',
    },
    schema: "./src/db/schema/*",
    out: "./src/db/migrations",
});
