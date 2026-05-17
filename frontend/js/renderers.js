function text(value) {
  if (value === null || value === undefined || value === "") return "";
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function rawText(value) {
  return value === null || value === undefined || value === "" ? "" : String(value);
}


function field(label, value) {
  if (!value) return "";
  return `<div><dt>${label}</dt><dd>${text(value)}</dd></div>`;
}


const categoryLabels = {
  sacred_history: "Sacred History",
  creatures: "Creature Archive",
  plants: "Field Notes",
  mushrooms: "Field Notes",
  objects: "Curious Object",
  domestic_objects: "Domestic Relic",
  folklore: "Folklore Fragment",
  places: "Curious Place",
  morbid_history: "Peat Archive",
  maritime: "Maritime Incident",
  systems: "System Record",
};


const categoryArt = {
  sacred_history: {
    src: "/media/category_art/monistary.jpg",
    alt: "Stone monastery mark",
  },
  morbid_history: {
    src: "/media/category_art/bog.png",
    alt: "Bog archive mark",
  },
};


function categoryLabel(item) {
  if (item.metadata?.display_label) return item.metadata.display_label;
  return categoryLabels[item.category] || titleCase(rawText(item.category).replaceAll("_", " "));
}


function categoryArtFor(item) {
  if (item.metadata?.icon) {
    return {
      src: item.metadata.icon,
      alt: `${categoryLabel(item)} mark`,
      className: "category-art-symbol",
    };
  }
  return categoryArt[item.category];
}


function titleCase(value) {
  return value.replace(/\w\S*/g, (word) => word[0].toUpperCase() + word.slice(1).toLowerCase());
}


function classification(item) {
  return titleCase(
    rawText(item.metadata?.classification || item.metadata?.order || item.subcategory).replaceAll("_", " "),
  );
}


function baseCard(item, dev, actions = {}) {
  const art = categoryArtFor(item);
  const meta = [
    field("Era", item.era),
    field("Region", item.region),
    field("Classification", classification(item)),
    dev.showId ? field("Item ID", item.id) : "",
    dev.showSource ? field("Dataset", item.dataset?.name) : "",
  ].join("");

  const json = dev.showJson
    ? `<pre class="dev-json">${text(JSON.stringify(item, null, 2))}</pre>`
    : "";

  return `
    ${
      art
        ? `<figure class="category-medallion category-art-${text(item.category)} ${text(art.className || "")}" aria-label="${text(art.alt)}"><img src="${text(art.src)}" alt=""></figure>`
        : ""
    }
    <header>
      <div class="kicker">${text(categoryLabel(item))}</div>
      <h1>${text(item.title)}</h1>
      ${item.subtitle ? `<p class="subtitle">${text(item.subtitle)}</p>` : ""}
    </header>
    ${
      item.description
        ? `<div class="description">${text(item.description)}${
            actions.canReadMore
              ? ` <button class="inline-read-more" type="button" data-card-action="read-more">Read more</button>`
              : ""
          }</div>`
        : ""
    }
    ${meta ? `<dl>${meta}</dl>` : ""}
    ${json}
  `;
}


export function renderArchiveCard(item, dev, actions) {
  return baseCard(item, dev, actions);
}


export function renderMemorialCard(item, dev, actions) {
  return baseCard(item, dev, actions);
}


export function renderTaleCard(item, dev, actions) {
  return baseCard(item, dev, actions);
}


export function renderSpecimenCard(item, dev, actions) {
  return baseCard(item, dev, actions);
}


export function renderIncidentCard(item, dev, actions) {
  return baseCard(item, dev, actions);
}


export const templates = {
  archive: renderArchiveCard,
  memorial: renderMemorialCard,
  tale: renderTaleCard,
  specimen: renderSpecimenCard,
  incident: renderIncidentCard,
};
