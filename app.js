/* ============================================================
   CardScan – Core App Logic
   YuGiOh (YGOPRODeck API) & Pokémon (TCGdex API)
   Cardmarket price-links, LocalStorage inventory
   ============================================================ */

/* ---- Constants ---- */
const CARD_NAME_CROP_RATIO = 0.15; // top 15 % of captured frame contains the card name
const FALLBACK_IMG_SVG     = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 112'%3E%3Crect width='80' height='112' fill='%231a1a2e'/%3E%3C/svg%3E";

const YUGIOH_API   = 'https://db.ygoprodeck.com/api/v7/cardinfo.php';
const POKEMON_API  = 'https://api.tcgdex.net/v2/en/cards';
const POKEMON_SETS = 'https://api.tcgdex.net/v2/en/sets';
const CM_BASE_YGO  = 'https://www.cardmarket.com/en/YuGiOh/Products/Search?searchString=';
const CM_BASE_PKM  = 'https://www.cardmarket.com/en/Pokemon/Products/Search?searchString=';

/* ---- State ---- */
let stream        = null;
let currentType   = 'yugioh';   // 'yugioh' | 'pokemon'
let currentResult = null;
let inventory     = loadInventory();
let invFilter     = 'all';      // 'all' | 'yugioh' | 'pokemon'
let deferredPrompt = null;

/* ---- DOM refs ---- */
const pages        = document.querySelectorAll('.page');
const navBtns      = document.querySelectorAll('#bottom-nav button');
const video        = document.getElementById('cam-video');
const scannerBox   = document.getElementById('scanner-box');
const resultBox    = document.getElementById('result-box');
const resultImg    = document.getElementById('result-img');
const resultName   = document.getElementById('result-name');
const resultBadges = document.getElementById('result-badges');
const resultPrice  = document.getElementById('result-price');
const resultCmLink = document.getElementById('result-cm-link');
const addBtn       = document.getElementById('btn-add-inv');
const searchInput  = document.getElementById('search-input');
const captureBtn   = document.getElementById('btn-capture');
const invList      = document.getElementById('inventory-list');
const headerCount  = document.getElementById('header-count');
const toastEl      = document.getElementById('toast');
const installBanner = document.getElementById('install-banner');
const installBtn   = document.getElementById('btn-install');

/* ==============================================================
   NAVIGATION
   ============================================================== */
function showPage(name) {
  pages.forEach(p => p.classList.toggle('active', p.id === `page-${name}`));
  navBtns.forEach(b => b.classList.toggle('active', b.dataset.page === name));
  if (name === 'scanner') startCamera();
  else                    stopCamera();
  if (name === 'inventory') renderInventory();
  if (name === 'stats')     renderStats();
}

navBtns.forEach(b => b.addEventListener('click', () => showPage(b.dataset.page)));

/* ==============================================================
   CAMERA
   ============================================================== */
async function startCamera() {
  if (stream) return;
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } },
      audio: false
    });
    video.srcObject = stream;
    video.play();
    captureBtn.disabled = false;
  } catch {
    showToast('Kamera nicht verfügbar – manuelle Suche nutzen', 'error');
    captureBtn.disabled = true;
  }
}

function stopCamera() {
  if (!stream) return;
  stream.getTracks().forEach(t => t.stop());
  stream = null;
  video.srcObject = null;
}

/* ---- Capture frame & OCR (name-crop heuristic) ---- */
captureBtn?.addEventListener('click', async () => {
  if (!stream) { showToast('Kamera nicht aktiv', 'error'); return; }

  // Flash effect
  const flash = document.createElement('div');
  flash.className = 'capture-flash';
  scannerBox.appendChild(flash);
  setTimeout(() => flash.remove(), 500);

  // Draw frame to canvas
  const canvas = document.createElement('canvas');
  canvas.width  = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);

  showSpinner();

  try {
    /* --- Tesseract OCR to read card name --- */
    if (typeof Tesseract === 'undefined') {
      showToast('OCR wird geladen…', 'error');
      return;
    }
    // Crop top portion of image where card names appear
    const cropH = Math.floor(canvas.height * CARD_NAME_CROP_RATIO);
    const cropCanvas = document.createElement('canvas');
    cropCanvas.width  = canvas.width;
    cropCanvas.height = cropH;
    cropCanvas.getContext('2d').drawImage(canvas, 0, 0, canvas.width, cropH, 0, 0, canvas.width, cropH);

    const { data: { text } } = await Tesseract.recognize(cropCanvas, 'eng', { logger: () => {} });
    const cardName = text.trim().split('\n')[0].trim();

    if (cardName.length < 3) {
      hideSpinner();
      showToast('Name nicht erkannt – manuelle Suche nutzen', 'error');
      return;
    }
    searchInput.value = cardName;
    await doSearch(cardName);
  } catch (err) {
    hideSpinner();
    showToast('Scan fehlgeschlagen – manuelle Suche nutzen', 'error');
    console.error(err);
  }
});

/* ==============================================================
   TYPE TOGGLE
   ============================================================== */
document.querySelectorAll('.type-toggle button').forEach(b => {
  b.addEventListener('click', () => {
    document.querySelectorAll('.type-toggle button').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    currentType = b.dataset.type;
    hideResult();
  });
});

/* ==============================================================
   SEARCH
   ============================================================== */
document.getElementById('btn-search')?.addEventListener('click', () => {
  const q = searchInput.value.trim();
  if (!q) { showToast('Bitte einen Kartennamen eingeben', 'error'); return; }
  doSearch(q);
});

searchInput?.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    const q = searchInput.value.trim();
    if (q) doSearch(q);
  }
});

async function doSearch(query) {
  showSpinner();
  hideResult();
  try {
    if (currentType === 'yugioh') {
      await searchYugioh(query);
    } else {
      await searchPokemon(query);
    }
  } catch (err) {
    hideSpinner();
    showToast('Fehler bei der Suche: ' + err.message, 'error');
  }
}

/* ==============================================================
   YuGiOh  (YGOPRODeck API – free, no auth)
   ============================================================== */
async function searchYugioh(name) {
  const url = `${YUGIOH_API}?name=${encodeURIComponent(name)}&misc=yes`;
  const res  = await fetch(url);
  if (!res.ok) {
    // Try fuzzy
    const url2 = `${YUGIOH_API}?fname=${encodeURIComponent(name)}&misc=yes`;
    const res2 = await fetch(url2);
    if (!res2.ok) throw new Error('Karte nicht gefunden');
    const data2 = await res2.json();
    displayYugioh(data2.data[0]);
    return;
  }
  const data = await res.json();
  displayYugioh(data.data[0]);
}

function displayYugioh(card) {
  hideSpinner();
  if (!card) { showToast('Keine YuGiOh-Karte gefunden', 'error'); return; }

  const imgUrl = card.card_images?.[0]?.image_url || '';
  const set    = card.card_sets?.[0];
  const setName = set?.set_name  || 'Unbekannt';
  const rarity  = set?.set_rarity || card.misc_info?.[0]?.formats?.join(', ') || '';
  const price   = card.card_prices?.[0]?.cardmarket_price
                  ? parseFloat(card.card_prices[0].cardmarket_price).toFixed(2) + ' €'
                  : 'Preis auf Cardmarket';

  currentResult = {
    id:      `ygo-${card.id}`,
    type:    'yugioh',
    name:    card.name,
    set:     setName,
    rarity:  rarity,
    img:     imgUrl,
    price:   card.card_prices?.[0]?.cardmarket_price || null,
    cardId:  card.id,
    qty:     1
  };

  resultImg.src = imgUrl;
  resultImg.alt = card.name;
  resultName.textContent = card.name;

  resultBadges.innerHTML = `
    <span class="badge badge-yugioh">YuGiOh</span>
    <span class="badge badge-type">${card.type || ''}</span>
    ${setName ? `<span class="badge badge-set">${setName}</span>` : ''}
    ${rarity  ? `<span class="badge badge-rarity">✦ ${rarity}</span>` : ''}
  `;

  resultPrice.textContent = price;
  resultCmLink.href = CM_BASE_YGO + encodeURIComponent(card.name);
  showResult();
}

/* ==============================================================
   Pokémon  (TCGdex API – free, no auth)
   ============================================================== */
async function searchPokemon(name) {
  const url = `${POKEMON_API}?name=${encodeURIComponent(name)}`;
  const res  = await fetch(url);
  if (!res.ok) throw new Error('Pokémon-Karte nicht gefunden');
  const cards = await res.json();
  if (!cards || cards.length === 0) throw new Error('Karte nicht gefunden');

  // Fetch first card's full detail
  const detailUrl = `${POKEMON_API}/${cards[0].id}`;
  const detailRes  = await fetch(detailUrl);
  const card        = await detailRes.json();
  displayPokemon(card);
}

function displayPokemon(card) {
  hideSpinner();
  if (!card) { showToast('Keine Pokémon-Karte gefunden', 'error'); return; }

  const imgUrl  = card.image ? card.image + '/high.webp' : '';
  const setName = card.set?.name  || 'Unbekannt';
  const rarity  = card.rarity    || '';
  const types   = (card.types || []).join(', ');

  currentResult = {
    id:     `pkm-${card.id}`,
    type:   'pokemon',
    name:   card.name,
    set:    setName,
    rarity: rarity,
    img:    imgUrl,
    price:  null,
    cardId: card.id,
    qty:    1
  };

  resultImg.src = imgUrl;
  resultImg.alt = card.name;
  resultName.textContent = card.name;

  resultBadges.innerHTML = `
    <span class="badge badge-pokemon">Pokémon</span>
    ${types  ? `<span class="badge badge-type">${types}</span>` : ''}
    <span class="badge badge-set">${setName}</span>
    ${rarity ? `<span class="badge badge-rarity">✦ ${rarity}</span>` : ''}
    ${card.localId ? `<span class="badge badge-type">#${card.localId}</span>` : ''}
  `;

  resultPrice.textContent = 'Preis auf Cardmarket ansehen';
  resultCmLink.href = CM_BASE_PKM + encodeURIComponent(card.name);
  showResult();
}

/* ==============================================================
   INVENTORY
   ============================================================== */
addBtn?.addEventListener('click', () => {
  if (!currentResult) return;
  addToInventory(currentResult);
  showToast(`"${currentResult.name}" zum Inventar hinzugefügt ✓`, 'success');
});

function addToInventory(card) {
  const existing = inventory.find(c => c.id === card.id);
  if (existing) {
    existing.qty = (existing.qty || 1) + 1;
  } else {
    inventory.push({ ...card, qty: 1, addedAt: Date.now() });
  }
  saveInventory();
  updateHeaderCount();
}

function removeFromInventory(id) {
  inventory = inventory.filter(c => c.id !== id);
  saveInventory();
  updateHeaderCount();
  renderInventory();
}

function changeQty(id, delta) {
  const card = inventory.find(c => c.id === id);
  if (!card) return;
  card.qty = Math.max(1, (card.qty || 1) + delta);
  saveInventory();
  renderInventory();
}

function renderInventory() {
  const filtered = invFilter === 'all'
    ? inventory
    : inventory.filter(c => c.type === invFilter);

  // Update filter buttons
  document.querySelectorAll('.filter-row button').forEach(b =>
    b.classList.toggle('active', b.dataset.filter === invFilter)
  );

  // Update totals badge
  document.getElementById('inv-count').textContent = inventory.length + ' Karten';

  if (filtered.length === 0) {
    invList.innerHTML = `
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="3"/>
          <path d="M9 12h6M12 9v6"/>
        </svg>
        <p>Noch keine Karten im Inventar.<br>Scanne eine Karte und füge sie hinzu!</p>
      </div>`;
    return;
  }

  invList.innerHTML = filtered.map(card => `
    <div class="inv-card" data-id="${esc(card.id)}">
      <img src="${esc(card.img || '')}" alt="${esc(card.name)}" loading="lazy">
      <div class="inv-card-info">
        <h3>${esc(card.name)}</h3>
        <div class="badges">
          <span class="badge badge-${card.type === 'yugioh' ? 'yugioh' : 'pokemon'}">${card.type === 'yugioh' ? 'YuGiOh' : 'Pokémon'}</span>
          ${card.set    ? `<span class="badge badge-set">${esc(card.set)}</span>` : ''}
          ${card.rarity ? `<span class="badge badge-rarity">✦ ${esc(card.rarity)}</span>` : ''}
        </div>
        <div class="price">${card.price ? parseFloat(card.price).toFixed(2) + ' €' : '—'}</div>
        <div class="qty">
          <button class="qty-dec" data-id="${esc(card.id)}">−</button>
          <span>${card.qty || 1}×</span>
          <button class="qty-inc" data-id="${esc(card.id)}">+</button>
          <a href="${esc((card.type === 'yugioh' ? CM_BASE_YGO : CM_BASE_PKM) + encodeURIComponent(card.name))}"
             target="_blank" rel="noopener" class="btn btn-sm btn-secondary" style="margin-left:6px">
            💰 Cardmarket
          </a>
        </div>
      </div>
      <button class="inv-card-delete" data-id="${esc(card.id)}" title="Löschen">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/>
          <path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/>
        </svg>
      </button>
    </div>
  `).join('');

  /* Fix broken card images */
  invList.querySelectorAll('img').forEach(img => {
    img.addEventListener('error', () => { img.src = FALLBACK_IMG_SVG; }, { once: true });
  });
}

/* ---- Inventory list – event delegation (avoids inline onclick / XSS) ---- */
invList.addEventListener('click', e => {
  const decBtn = e.target.closest('.qty-dec');
  const incBtn = e.target.closest('.qty-inc');
  const delBtn = e.target.closest('.inv-card-delete');
  if (decBtn) changeQty(decBtn.dataset.id, -1);
  else if (incBtn) changeQty(incBtn.dataset.id, 1);
  else if (delBtn) removeFromInventory(delBtn.dataset.id);
});

/* ---- Filter buttons ---- */
document.querySelectorAll('.filter-row button').forEach(b => {
  b.addEventListener('click', () => {
    invFilter = b.dataset.filter;
    renderInventory();
  });
});

/* ==============================================================
   STATS PAGE
   ============================================================== */
function renderStats() {
  const total      = inventory.reduce((s, c) => s + (c.qty || 1), 0);
  const ygoCount   = inventory.filter(c => c.type === 'yugioh').reduce((s,c) => s+(c.qty||1), 0);
  const pkmCount   = inventory.filter(c => c.type === 'pokemon').reduce((s,c) => s+(c.qty||1), 0);
  const totalVal   = inventory.reduce((s,c) => s + (parseFloat(c.price)||0)*(c.qty||1), 0);

  document.getElementById('stat-total').textContent    = total;
  document.getElementById('stat-ygo').textContent      = ygoCount;
  document.getElementById('stat-pkm').textContent      = pkmCount;
  document.getElementById('stat-value').textContent    = totalVal.toFixed(2) + ' €';

  // Top 5 by price
  const top5 = [...inventory]
    .filter(c => c.price)
    .sort((a,b) => parseFloat(b.price) - parseFloat(a.price))
    .slice(0, 5);

  const topList = document.getElementById('stats-top5');
  if (top5.length === 0) {
    topList.innerHTML = '<p style="color:var(--text-muted);font-size:.85rem">Noch keine Preisdaten vorhanden.</p>';
    return;
  }
  topList.innerHTML = top5.map(c => `
    <div class="inv-card" style="margin-bottom:8px">
      <img src="${esc(c.img||'')}" alt="${esc(c.name)}" style="width:40px;height:56px">
      <div class="inv-card-info">
        <h3>${esc(c.name)}</h3>
        <div class="price">${parseFloat(c.price).toFixed(2)} €</div>
      </div>
    </div>
  `).join('');

  topList.querySelectorAll('img').forEach(img => {
    img.addEventListener('error', () => { img.src = FALLBACK_IMG_SVG; }, { once: true });
  });
}

/* ==============================================================
   EXPORT CSV
   ============================================================== */
document.getElementById('btn-export')?.addEventListener('click', () => {
  if (inventory.length === 0) { showToast('Inventar ist leer', 'error'); return; }
  const header = ['Name','Typ','Set','Rarität','Preis (€)','Menge','Cardmarket-Link'];
  const rows   = inventory.map(c => [
    `"${(c.name||'').replace(/"/g,'""')}"`,
    c.type === 'yugioh' ? 'YuGiOh' : 'Pokémon',
    `"${(c.set||'').replace(/"/g,'""')}"`,
    `"${(c.rarity||'').replace(/"/g,'""')}"`,
    c.price ? parseFloat(c.price).toFixed(2) : '',
    c.qty || 1,
    `"${(c.type==='yugioh'?CM_BASE_YGO:CM_BASE_PKM)+encodeURIComponent(c.name)}"`
  ].join(','));
  const csv = [header.join(','), ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = 'cardscan-inventar.csv';
  document.body.appendChild(a); a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('CSV exportiert ✓', 'success');
});

/* ==============================================================
   HELPERS
   ============================================================== */
function showResult()  { resultBox.classList.add('visible');    hideSpinner(); }
function hideResult()  { resultBox.classList.remove('visible'); currentResult = null; }
function showSpinner() {
  let s = document.getElementById('search-spinner');
  if (!s) {
    s = document.createElement('div');
    s.id = 'search-spinner'; s.className = 'spinner';
    resultBox.insertAdjacentElement('afterend', s);
  }
}
function hideSpinner() {
  document.getElementById('search-spinner')?.remove();
}

let toastTimer = null;
function showToast(msg, type = '') {
  toastEl.textContent = msg;
  toastEl.className   = 'show' + (type ? ` toast-${type}` : '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toastEl.className = ''; }, 2800);
}

function esc(str) {
  return String(str ?? '')
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}

function loadInventory() {
  try { return JSON.parse(localStorage.getItem('cardscan-inventory') || '[]'); }
  catch { return []; }
}

function saveInventory() {
  localStorage.setItem('cardscan-inventory', JSON.stringify(inventory));
}

function updateHeaderCount() {
  const total = inventory.reduce((s,c) => s + (c.qty||1), 0);
  headerCount.textContent = total;
}

/* ==============================================================
   PWA INSTALL
   ============================================================== */
window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();
  deferredPrompt = e;
  installBanner.classList.add('visible');
});

installBtn?.addEventListener('click', async () => {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  if (outcome === 'accepted') {
    installBanner.classList.remove('visible');
    showToast('App installiert! 🎉', 'success');
  }
  deferredPrompt = null;
});

window.addEventListener('appinstalled', () => {
  installBanner.classList.remove('visible');
});

/* iOS Safari: no beforeinstallprompt – show manual "Add to Home Screen" hint */
const iosHint = document.getElementById('ios-install-hint');
const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
// navigator.standalone is Safari-specific: true when running as an installed PWA
if (isIOS && !navigator.standalone) {
  iosHint?.classList.add('visible');
}
document.getElementById('btn-ios-close')?.addEventListener('click', () => {
  iosHint?.classList.remove('visible');
});

/* ==============================================================
   INIT
   ============================================================== */
updateHeaderCount();
showPage('scanner');
