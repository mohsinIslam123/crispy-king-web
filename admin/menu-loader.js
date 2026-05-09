const CATS = ["veg-burgers", "nonveg-burgers"];

function loadCat(cat) {
  fetch(`${cat}.json`)
    .then(r => r.json())
    .then(items => {
      const section = document.getElementById(cat);
      if (!section) return;
      section.innerHTML = items.map(buildCard).join("");
    })
    .catch(err => console.error("Error loading", cat, err));
}

function buildCard(item) {
  const badgeHTML = item.badge
    ? `<span class="badge">${item.badge}</span>`
    : "";

  const vegDot = item.isVeg
    ? `<span class="veg-dot">🟢</span>`
    : `<span class="veg-dot">🔴</span>`;

  const mediaHTML = item.image
    ? `<img src="${item.image}" alt="${item.name}" class="card-img" loading="lazy">`
    : `<div class="card-emoji">🍔</div>`;

  return `
    <div class="menu-card">
      <div class="card-media">
        ${badgeHTML}
        ${mediaHTML}
      </div>
      <div class="card-body">
        <div class="card-title-row">
          ${vegDot}
          <h3 class="card-name">${item.name}</h3>
        </div>
        <p class="card-desc">${item.description}</p>
        <div class="card-footer">
          <span class="card-price">₹${item.price}</span>
          <button class="add-btn">Add +</button>
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