// ─── CRISPY KING MENU LOADER ─────────────────────────────────────────────────

const MENU_CATEGORIES = [
  { file: "veg-burgers",    grid: "grid-veg-burgers"   },
  { file: "nonveg-burgers", grid: "grid-nonveg-burgers" },
  { file: "chicken",        grid: "grid-chicken"        },
  { file: "fries",          grid: "grid-fries"          },
  { file: "pizza",          grid: "grid-pizza"          },
  { file: "wraps",          grid: "grid-wraps"          },
  { file: "sandwich",       grid: "grid-sandwich"       },
  { file: "shakes",         grid: "grid-shakes"         },
];

function buildCard(item) {
  const badge  = item.badge  ? <span class="menu-badge">${item.badge}</span>  : "";
  const tag    = item.tag    ? <span class="menu-tag">${item.tag}</span>      : "";
  const desc   = item.desc   ? <p class="menu-card-desc">${item.desc}</p>     : "";
  const waText = encodeURIComponent(Assalamualaikum! Mujhe ${item.name} order karna hai 🍔);
  return `
    <div class="menu-card">
      <div class="menu-card-img" id="img-${slugify(item.name)}">
        <span class="menu-card-emoji">🍔</span>
        ${badge}
      </div>
      <div class="menu-card-body">
        ${tag}
        <h3 class="menu-card-name">${item.name}</h3>
        ${desc}
        <div class="menu-card-footer">
          <span class="menu-card-price">₹${item.price}</span>
          <a class="menu-card-btn" href="https://wa.me/917895743536?text=${waText}" target="_blank">
            Order Karo
          </a>
        </div>
      </div>
    </div>`;
}

function slugify(str) {
  return String(str).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

async function loadCategory(cat) {
  const grid = document.getElementById(cat.grid);
  if (!grid) return;
  try {
    const res  = await fetch(/content/menu/${cat.file}.json);
    if (!res.ok) throw new Error(${cat.file}: HTTP ${res.status});
    const items = await res.json();
    grid.innerHTML = items.map(buildCard).join("");
  } catch (e) {
    console.error("[MenuLoader]", e);
    grid.innerHTML = <p style="color:#aaa;padding:20px">Menu load nahi hua. Refresh karo.</p>;
  }
}

function initMenu() {
  MENU_CATEGORIES.forEach(loadCategory);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initMenu);
} else {
  initMenu();
}
