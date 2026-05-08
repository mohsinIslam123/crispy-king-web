/**
 * menu-loader.js — Crispy King Dynamic Menu System
 * Fetches JSON files from /content/menu/{category}.json (written by Netlify CMS)
 * Handles: parallel fetch, tab filtering, image fallback, WhatsApp cart hook
 */

"use strict";

// ─── 1. CATEGORY MAP ──────────────────────────────────────────────────────────
const CATEGORY_MAP = {
  "veg-burgers":    { label: "Veg Burgers",    emoji: "🥬" },
  "nonveg-burgers": { label: "Non-Veg Burgers", emoji: "🍔" },
  "chicken":        { label: "Chicken",          emoji: "🍗" },
  "fries":          { label: "Fries",            emoji: "🍟" },
  "pizza":          { label: "Pizza",            emoji: "🍕" },
  "wraps":          { label: "Wraps",            emoji: "🌯" },
  "sandwich":       { label: "Sandwich",         emoji: "🥪" },
  "shakes":         { label: "Shakes",           emoji: "🥤" },
};

// ─── 2. STATE ──────────────────────────────────────────────────────────────────
let _menuData   = {};       // { category: [items] }
let _activeTab  = "all";    // tracks the active filter tab

// ─── 3. FETCH ONE CATEGORY ────────────────────────────────────────────────────
async function fetchCategory(category) {
  try {
    const res = await fetch(/content/menu/${category}.json, { cache: "no-cache" });
    if (!res.ok) {
      console.warn([Menu] ${category}.json → ${res.status}. Skipping.);
      return [];
    }
    const data = await res.json();
    // CMS saves { items: [...] }; handle bare arrays too
    return Array.isArray(data) ? data : (data.items ?? []);
  } catch (err) {
    console.error([Menu] Failed to load "${category}":, err);
    return [];
  }
}

// ─── 4. LOAD ALL CATEGORIES IN PARALLEL ──────────────────────────────────────
async function loadMenuFromCMS() {
  const categories = Object.keys(CATEGORY_MAP);

  const results = await Promise.allSettled(
    categories.map((cat) => fetchCategory(cat))
  );

  const menuData = {};
  results.forEach((result, i) => {
    menuData[categories[i]] =
      result.status === "fulfilled" ? result.value : [];
  });

  return menuData;
}

// ─── 5. BUILD ONE MENU CARD ───────────────────────────────────────────────────
function buildMenuCard(item, category) {
  const fallback = CATEGORY_MAP[category]?.emoji ?? "🍽️";
  const price    = item.price != null ? ₹${Number(item.price).toFixed(0)} : "";
  const badge    = item.badge
    ? <span class="menu-badge">${esc(item.badge)}</span> : "";

  const media = item.image
    ? `<img
         src="${esc(item.image)}"
         alt="${esc(item.name ?? "")}"
         class="menu-card__img"
         loading="lazy"
         onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"
       />
       <div class="menu-card__emoji" style="display:none" aria-hidden="true">${fallback}</div>`
    : <div class="menu-card__emoji" aria-hidden="true">${fallback}</div>;

  const vegDot = item.isVeg != null
    ? `<span class="veg-dot ${item.isVeg ? "veg" : "nonveg"}"
          title="${item.isVeg ? "Veg" : "Non-Veg"}"></span>` : "";

  return `
    <article class="menu-card" data-category="${esc(category)}">
      <div class="menu-card__media">
        ${media}${badge}
      </div>
      <div class="menu-card__body">
        <h3 class="menu-card__name">${esc(item.name ?? "")}</h3>
        ${item.description
          ? <p class="menu-card__desc">${esc(item.description)}</p> : ""}
        <div class="menu-card__footer">
          <span class="menu-card__price">${price}</span>
          ${vegDot}
          <button
            class="menu-card__order-btn"
            data-name="${esc(item.name ?? "")}"
            data-price="${esc(price)}"
            aria-label="Order ${esc(item.name ?? "")} on WhatsApp"
          >Order</button>
        </div>
      </div>
    </article>`;
}

// ─── 6. RENDER A CATEGORY SECTION ─────────────────────────────────────────────
function renderCategorySection(containerEl, items, category) {
  if (!containerEl) return;

  if (!items || items.length === 0) {
    containerEl.innerHTML =
      <p class="menu-empty">No items right now. Check back soon!</p>;
    return;
  }

  containerEl.innerHTML = items
    .map((item) => buildMenuCard(item, category))
    .join("");
}

// ─── 7. TAB FILTER ────────────────────────────────────────────────────────────
/**
 * Hides/shows entire category sections based on the active tab.
 * Expects <section data-menu-section="veg-burgers"> wrappers in the HTML.
 */
function applyTabFilter(tab) {
  _activeTab = tab;

  // Update tab button active states
  document.querySelectorAll(".menu-tab-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tab);
    btn.setAttribute("aria-selected", btn.dataset.tab === tab);
  });

  // Show/hide sections
  document.querySelectorAll("[data-menu-section]").forEach((section) => {
    const cat = section.dataset.menuSection;
    const show = tab === "all" || cat === tab;
    section.hidden = !show;
  });
}

// ─── 8. WHATSAPP ORDER HANDLER ────────────────────────────────────────────────
const WHATSAPP_NUMBER = "919999999999"; // ← Replace with owner's number (91 + 10 digits)

function handleOrderClick(e) {
  const btn = e.target.closest(".menu-card__order-btn");
  if (!btn) return;

  const name  = btn.dataset.name;
  const price = btn.dataset.price;
  const msg   = encodeURIComponent(
    Hi Crispy King Muradnagar! 🍔\nI'd like to order:\n\n• ${name} — ${price}\n\nPlease confirm my order.
  );
  window.open(https://wa.me/${WHATSAPP_NUMBER}?text=${msg}, "_blank");
}

// ─── 9. MAIN INIT ─────────────────────────────────────────────────────────────
async function initMenu() {
  const categories = Object.keys(CATEGORY_MAP);

  // Show skeletons in every section while fetching
  document.querySelectorAll("[data-menu-category]").forEach((el) => {
    el.innerHTML = buildSkeleton();
  });

  _menuData = await loadMenuFromCMS();

  // Render each category into its container
  document.querySelectorAll("[data-menu-category]").forEach((el) => {
    const cat = el.dataset.menuCategory;
    renderCategorySection(el, _menuData[cat] ?? [], cat);
  });

  // Wire tab buttons (generated by buildTabs or present in HTML)
  document.addEventListener("click", (e) => {
    const tabBtn = e.target.closest(".menu-tab-btn");
    if (tabBtn) applyTabFilter(tabBtn.dataset.tab);

    // WhatsApp order
    handleOrderClick(e);
  });

  // Default: show all
  applyTabFilter("all");

  // Let other scripts know the menu is ready
  document.dispatchEvent(new CustomEvent("menuLoaded", { detail: _menuData }));
}

// ─── 10. SKELETON BUILDER ─────────────────────────────────────────────────────
function buildSkeleton(count = 4) {
  return Array.from({ length: count })
    .map(
      () => `<div class="menu-skeleton" aria-hidden="true">
               <div class="skel-media"></div>
               <div class="skel-body">
                 <div class="skel-line skel-title"></div>
                 <div class="skel-line skel-desc"></div>
                 <div class="skel-line skel-price"></div>
               </div>
             </div>`
    )
    .join("");
}

// ─── 11. UTILITY ──────────────────────────────────────────────────────────────
function esc(str) {
  if (typeof str !== "string") return "";
  return str
    .replace(/&/g,  "&amp;")
    .replace(/</g,  "&lt;")
    .replace(/>/g,  "&gt;")
    .replace(/"/g,  "&quot;")
    .replace(/'/g,  "&#039;");
}

// ─── 12. BOOTSTRAP ────────────────────────────────────────────────────────────
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initMenu);
} else {
  initMenu();
}