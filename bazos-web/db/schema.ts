import { pgTable, serial, text, integer, boolean, timestamp } from "drizzle-orm/pg-core";

export const searches = pgTable("searches", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  source: text("source").notNull(),
  url: text("url"),
  searchTerm: text("search_term"),
  priceMin: integer("price_min"),
  priceMax: integer("price_max"),
  location: text("location"),
  radius: integer("radius"),
  maxPages: integer("max_pages").notNull().default(3),
  active: boolean("active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const listings = pgTable("listings", {
  id: text("id").notNull(),
  source: text("source").notNull(),
  searchId: integer("search_id").references(() => searches.id, { onDelete: "cascade" }),
  title: text("title"),
  url: text("url"),
  price: text("price"),
  imageUrl: text("image_url"),
  description: text("description"),
  location: text("location"),
  category: text("category"),
  datePosted: text("date_posted"),
  viewCount: integer("view_count"),
  firstSeen: timestamp("first_seen").notNull().defaultNow(),
  lastChecked: timestamp("last_checked").notNull().defaultNow(),
  notified: boolean("notified").notNull().default(false),
});