"use server";

import { db } from "@/db";
import { searches } from "@/db/schema";
import { revalidatePath } from "next/cache";

export async function addSearch(formData: FormData) {
  const name = formData.get("name") as string;
  const url = formData.get("url") as string;
  const priceMin = formData.get("priceMin") as string;
  const priceMax = formData.get("priceMax") as string;

  await db.insert(searches).values({
    name,
    source: "bazos_sk",
    url,
    priceMin: priceMin ? parseInt(priceMin) : null,
    priceMax: priceMax ? parseInt(priceMax) : null,
    maxPages: 1,
    active: true,
  });

  revalidatePath("/searches");
}