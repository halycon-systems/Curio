const HISTORY_KEY = "curio.history";
const SETTINGS_KEY = "curio.devSettings";
const LIMIT = 10;


export function loadHistory() {
  try {
    return { ...emptyHistory(), ...(JSON.parse(sessionStorage.getItem(HISTORY_KEY)) || {}) };
  } catch {
    return emptyHistory();
  }
}


export function rememberItem(item) {
  const history = loadHistory();
  history.recentItemIds.push(item.id);
  history.recentCategories.push(item.category);
  if (item.subcategory) history.recentSubcategories.push(item.subcategory);
  if (item.mood) history.recentMoods.push(item.mood);
  history.recentItemIds = history.recentItemIds.slice(-LIMIT);
  history.recentCategories = history.recentCategories.slice(-LIMIT);
  history.recentSubcategories = history.recentSubcategories.slice(-LIMIT);
  history.recentMoods = history.recentMoods.slice(-LIMIT);
  sessionStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  return history;
}


export function clearHistory() {
  sessionStorage.removeItem(HISTORY_KEY);
}


export function emptyHistory() {
  return {
    recentItemIds: [],
    recentCategories: [],
    recentSubcategories: [],
    recentMoods: [],
  };
}


export function loadDevSettings() {
  try {
    return JSON.parse(localStorage.getItem(SETTINGS_KEY)) || defaultDevSettings();
  } catch {
    return defaultDevSettings();
  }
}


export function saveDevSettings(settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}


export function defaultDevSettings() {
  return {
    showId: false,
    showSource: false,
    showJson: false,
    disableSmartRandom: false,
    morbidContent: true,
    forceCategory: "",
    forceTemplate: "",
  };
}
