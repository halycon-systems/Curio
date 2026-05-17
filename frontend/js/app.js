import { fetchCategories, fetchRandomItem } from "./api.js";
import { templates } from "./renderers.js";
import {
  clearHistory,
  loadDevSettings,
  loadHistory,
  rememberItem,
  saveDevSettings,
} from "./settings.js";

const mysteryBox = document.querySelector("#mystery-box");
const itemCard = document.querySelector("#item-card");
const another = document.querySelector("#another");
const devTrigger = document.querySelector("#dev-trigger");
const devPanel = document.querySelector("#dev-panel");
const forceCategory = document.querySelector("#force-category");
const forceTemplate = document.querySelector("#force-template");

let currentItem = null;
let currentExpanded = false;
let isRevealing = false;
let devSettings = loadDevSettings();

function syncDevControls() {
  document.querySelector("#show-id").checked = devSettings.showId;
  document.querySelector("#show-source").checked = devSettings.showSource;
  document.querySelector("#show-json").checked = devSettings.showJson;
  document.querySelector("#disable-smart").checked = devSettings.disableSmartRandom;
  document.querySelector("#toggle-morbid").checked = devSettings.morbidContent;
  forceCategory.value = devSettings.forceCategory;
  forceTemplate.value = devSettings.forceTemplate;
}

function readDevControls() {
  devSettings = {
    showId: document.querySelector("#show-id").checked,
    showSource: document.querySelector("#show-source").checked,
    showJson: document.querySelector("#show-json").checked,
    disableSmartRandom: document.querySelector("#disable-smart").checked,
    morbidContent: document.querySelector("#toggle-morbid").checked,
    forceCategory: forceCategory.value,
    forceTemplate: forceTemplate.value,
  };
  saveDevSettings(devSettings);
  if (currentItem) renderItem(currentItem);
}

function renderItem(item) {
  const itemToRender = { ...item };
  if (devSettings.forceTemplate) itemToRender.template = devSettings.forceTemplate;
  const renderer = templates[itemToRender.template] || templates.archive;
  itemCard.className = `item-card template-${itemToRender.template} category-${itemToRender.category}`;
  itemCard.innerHTML = renderer(itemToRender, devSettings, {
    canReadMore: canReadMore(itemToRender),
  });
  itemCard.classList.remove("is-hidden");
  itemCard.classList.add("is-entering");
  window.setTimeout(() => itemCard.classList.remove("is-entering"), 420);
  document.body.className = `theme-${itemToRender.theme || "velvet"}`;
}

async function reveal() {
  if (isRevealing) return;
  isRevealing = true;
  another.disabled = true;
  try {
    currentExpanded = false;
    const hasCard = !itemCard.classList.contains("is-hidden") && itemCard.innerHTML;

    if (hasCard) {
      itemCard.classList.add("is-exiting");
      await wait(220);
    } else {
      mysteryBox.hidden = true;
      itemCard.classList.add("is-hidden");
    }

    const history = loadHistory();
    const category = devSettings.forceCategory;
    currentItem = await fetchRandomItem({
      category,
      recentItemIds: history.recentItemIds,
      recentCategories: history.recentCategories,
      recentSubcategories: history.recentSubcategories || [],
      recentMoods: history.recentMoods,
      disableSmartRandom: devSettings.disableSmartRandom,
      includeMorbid: devSettings.morbidContent,
    });
    rememberItem(currentItem);
    itemCard.classList.remove("is-exiting");
    renderItem(currentItem);
    another.hidden = false;
  } finally {
    another.disabled = false;
    isRevealing = false;
  }
}

function wait(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function canReadMore(item) {
  return Boolean(
    item?.source_url ||
      (item?.metadata?.full_description &&
        item.metadata.full_description !== item.description &&
        !currentExpanded)
  );
}

async function loadCategoryOptions() {
  const categories = await fetchCategories();
  for (const entry of categories) {
    const option = document.createElement("option");
    option.value = entry.category;
    option.textContent = `${entry.category.replaceAll("_", " ")} (${entry.item_count})`;
    forceCategory.append(option);
  }
  syncDevControls();
}

mysteryBox.addEventListener("click", reveal);
another.addEventListener("click", reveal);

itemCard.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) return;
  const action = event.target.closest("[data-card-action]");
  if (!action || action.dataset.cardAction !== "read-more") return;

  if (currentItem?.source_url) {
    window.open(currentItem.source_url, "_blank", "noopener");
    return;
  }
  if (currentItem?.metadata?.full_description) {
    currentExpanded = true;
    renderItem({
      ...currentItem,
      description: currentItem.metadata.full_description,
    });
  }
});

devPanel.addEventListener("change", readDevControls);
document.querySelector("#clear-history").addEventListener("click", clearHistory);

loadCategoryOptions();
