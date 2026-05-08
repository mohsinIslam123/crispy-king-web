var CATS = [
  {file:"veg-burgers",grid:"grid-veg-burgers"},
  {file:"nonveg-burgers",grid:"grid-nonveg-burgers"},
  {file:"chicken",grid:"grid-chicken"},
  {file:"fries",grid:"grid-fries"},
  {file:"pizza",grid:"grid-pizza"},
  {file:"wraps",grid:"grid-wraps"},
  {file:"sandwich",grid:"grid-sandwich"},
  {file:"shakes",grid:"grid-shakes"}
];

function buildCard(item) {
  var wa = encodeURIComponent("Assalamualaikum! Mujhe " + item.name + " order karna hai");
  return '<div class="menu-card">' +
    '<div class="menu-card-img"><span style="font-size:40px">🍔</span>' +
    (item.badge ? '<span class="menu-badge">' + item.badge + '</span>' : '') +
    '</div><div class="menu-card-body">' +
    (item.tag ? '<span class="menu-tag">' + item.tag + '</span>' : '') +
    '<h3 class="menu-card-name">' + item.name + '</h3>' +
    (item.desc ? '<p class="menu-card-desc">' + item.desc + '</p>' : '') +
    '<div class="menu-card-footer">' +
    '<span class="menu-card-price">&#8377;' + item.price + '</span>' +
    '<a class="menu-card-btn" href="https://wa.me/917895743536?text=' + wa + '" target="_blank">Order Karo</a>' +
    '</div></div></div>';
}

function loadCat(cat) {
  var grid = document.getElementById(cat.grid);
  if (!grid) return;
  fetch("/content/menu/" + cat.file + ".json")
    .then(function(r) { return r.json(); })
    .then(function(items) {
      grid.innerHTML = items.map(buildCard).join("");
    })
    .catch(function(e) {
      console.error("MenuLoader error:", cat.file, e);
    });
}

function initMenu() {
  CATS.forEach(loadCat);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initMenu);
} else {
  initMenu();
}