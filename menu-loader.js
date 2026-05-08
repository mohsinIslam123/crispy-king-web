const CATS = ["veg-burgers", "nonveg-burgers"];

function loadCat(cat) {
  fetch(`content/menu/${cat}.json`)
    .then(r => r.json())
    .then(items => {
      const section = document.getElementById(cat);
      if (!section) return;
      section.innerHTML = items.map(buildCard).join("");
    })
    .catch(err => console.error("Error loading", cat, err));
}

function buildCard(item) {
  const badge = item.badge
    ? `<span style="position:absolute;top:8px;left:8px;background:#e63946;color:#fff;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:700;z-index:2;">${item.badge}</span>`
    : "";

  const media = item.image
    ? `<img src="${item.image}" alt="${item.name}" style="width:100%;height:180px;object-fit:cover;display:block;" loading="lazy" onerror="this.style.display='none'">`
    : `<div style="font-size:4rem;text-align:center;padding:30px;">🍔</div>`;

  const dot = item.isVeg ? "🟢" : "🔴";

  return `
    <div class="menu-card">
      <div style="position:relative;overflow:hidden;border-radius:12px 12px 0 0;">
        ${badge}
        ${media}
      </div>
      <div class="card-body">
        <h3 class="card-name">${dot} ${item.name}</h3>
        <p class="card-desc">${item.description}</p>
        <div class="card-footer">
          <span class="card-price">₹${item.price}</span>
          <button class="add-btn" onclick="addToCart('${item.id}')">+ Cart Mein Daalo</button>
        </div>
      </div>
    </div>
  `;
}

function initMenu() {
  CATS.forEach(loadCat);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initMenu);
} else {
  initMenu();
}
