export async function fetchRandomItem(options) {
  const params = new URLSearchParams();
  if (options.category) params.set("category", options.category);
  if (options.recentItemIds.length) {
    params.set("recent_item_ids", options.recentItemIds.join(","));
  }
  if (options.recentCategories.length) {
    params.set("recent_categories", options.recentCategories.join(","));
  }
  if (options.recentSubcategories.length) {
    params.set("recent_subcategories", options.recentSubcategories.join(","));
  }
  if (options.recentMoods.length) {
    params.set("recent_moods", options.recentMoods.join(","));
  }
  if (options.disableSmartRandom) params.set("disable_smart_random", "true");
  params.set("include_morbid", options.includeMorbid ? "true" : "false");

  const response = await fetch(`/api/random?${params.toString()}`);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}


export async function fetchCategories() {
  const response = await fetch("/api/categories");
  if (!response.ok) return [];
  return response.json();
}
