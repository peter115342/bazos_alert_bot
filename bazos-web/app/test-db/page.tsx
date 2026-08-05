import { db } from "@/db";
import { searches } from "@/db/schema";

export default async function TestDb() {
  const rows = await db.select().from(searches);
  return <pre>{JSON.stringify(rows, null, 2)}</pre>;
}