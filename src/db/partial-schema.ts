import type { BuildSchema } from "drizzle-zod";

export const createPartialSchema = <
    T extends "insert" | "select" | "update",
    C extends Record<string, any>,
    R extends Record<string, any> | undefined,
    O extends true | Partial<Record<"string" | "number" | "bigint" | "boolean" | "date", true>> | undefined
>(schema: BuildSchema<T, C, R, O>) => {
    return schema
        .partial()
        .refine(data => Object.keys(data).some(key => data[key as keyof typeof data] !== undefined), {
            message: "At least one property is required",
        })
}
