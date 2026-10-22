import { drizzle, type PostgresJsDatabase } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const globalForPostgres = globalThis as typeof globalThis & {
  postgresClient?: ReturnType<typeof postgres>;
  drizzleDb?: PostgresJsDatabase<typeof schema>;
};

export function getDb(): PostgresJsDatabase<typeof schema> {
  if (globalForPostgres.drizzleDb) return globalForPostgres.drizzleDb;

  const connectionString = process.env.DATABASE_URL;
  if (!connectionString) {
    throw new Error("Falta DATABASE_URL. Configura apps/panel/.env.local.");
  }

  const client =
    globalForPostgres.postgresClient ??
    postgres(connectionString, {
      max: 5,
      idle_timeout: 20,
      connect_timeout: 10,
    });

  if (process.env.NODE_ENV !== "production") {
    globalForPostgres.postgresClient = client;
  }

  const database = drizzle(client, { schema });
  if (process.env.NODE_ENV !== "production") {
    globalForPostgres.drizzleDb = database;
  }
  return database;
}

export async function closeDb(): Promise<void> {
  await globalForPostgres.postgresClient?.end({ timeout: 5 });
  delete globalForPostgres.postgresClient;
  delete globalForPostgres.drizzleDb;
}
