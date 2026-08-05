import { db } from "@/db";
import { searches, listings } from "@/db/schema";
import { eq } from "drizzle-orm";
import { notFound } from "next/navigation";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";

export default async function SearchDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const searchId = parseInt(id);

  const [search] = await db
    .select()
    .from(searches)
    .where(eq(searches.id, searchId));

  if (!search) {
    notFound();
  }

  const foundListings = await db
    .select()
    .from(listings)
    .where(eq(listings.searchId, searchId))
    .orderBy(listings.firstSeen);

  return (
    <div className="max-w-2xl mx-auto py-10 px-4 space-y-6">
      <div>
        <Link href="/searches" className="text-sm text-muted-foreground hover:underline">
          ← Späť na hľadania
        </Link>
        <h1 className="text-2xl font-bold mt-2">{search.name}</h1>
        <p className="text-muted-foreground">
          {search.source} · {search.priceMin ?? "?"}€ – {search.priceMax ?? "?"}€
        </p>
      </div>

      <div className="space-y-3">
        <h2 className="text-lg font-semibold">
          Nájdené inzeráty ({foundListings.length})
        </h2>

        {foundListings.length === 0 && (
          <p className="text-muted-foreground text-sm">
            Zatiaľ žiadne nálezy. Spusti scraping skript.
          </p>
        )}

        {foundListings.map((listing) => (
          <Card key={`${listing.id}-${listing.source}`}>
            <CardContent className="py-4 flex gap-4">
              {listing.imageUrl && (
                <img
                  src={listing.imageUrl}
                  alt={listing.title ?? ""}
                  className="w-20 h-20 object-cover rounded"
                />
              )}
              <div className="flex-1">
                <a
                  href={listing.url ?? "#"}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium hover:underline"
                >
                  {listing.title}
                </a>
                <p className="text-sm text-muted-foreground">
                  {listing.price} · {listing.location}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}