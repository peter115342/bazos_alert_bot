import {db} from "@/db";
import {searches} from "@/db/schema";
import {addSearch} from "./actions";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Label} from "@/components/ui/label";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import Link from "next/link";

export default async function SearchesPage() {
    const allSearches = await db.select().from(searches);

    return (
        <div className="max-w-2xl mx-auto py-10 px-4 space-y-8">
            <div>
                <h1 className="text-2xl font-bold">Moje hľadania</h1>
                <p className="text-muted-foreground">
                    Spravuj hľadania, ktoré chceš sledovať na Bazose.
                </p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Pridať nové hľadanie</CardTitle>
                    <CardDescription>
                        Zadaj názov a URL z Bazosu (napr. výsledky vyhľadávania).
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form action={addSearch} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Názov</Label>
                            <Input id="name" name="name" placeholder="napr. Fiat Panda" required/>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="url">Bazos URL</Label>
                            <Input id="url" name="url" placeholder="https://auto.bazos.sk/?..." required/>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="priceMin">Cena od</Label>
                                <Input id="priceMin" name="priceMin" type="number" placeholder="2000"/>
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="priceMax">Cena do</Label>
                                <Input id="priceMax" name="priceMax" type="number" placeholder="15000"/>
                            </div>
                        </div>

                        <Button type="submit" className="w-full">
                            Pridať hľadanie
                        </Button>
                    </form>
                </CardContent>
            </Card>

            <div className="space-y-3">
                <h2 className="text-lg font-semibold">Aktívne hľadania</h2>
                {allSearches.length === 0 && (
                    <p className="text-muted-foreground text-sm">Zatiaľ žiadne hľadania.</p>
                )}
                {allSearches.map((s) => (
                    <Card key={s.id}>
                        <CardContent className="py-4 flex items-center justify-between">
                            <div>
                                <Link href={`/searches/${s.id}`} className="font-medium hover:underline">
                                    {s.name}
                                </Link>
                                <p className="text-sm text-muted-foreground">
                                    {s.source} · {s.priceMin ?? "?"}€ – {s.priceMax ?? "?"}€
                                </p>
                            </div>
                            <span
                                className={
                                    s.active
                                        ? "text-xs px-2 py-1 rounded-full bg-green-100 text-green-700"
                                        : "text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-500"
                                }
                            >
                {s.active ? "aktívne" : "vypnuté"}
              </span>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}