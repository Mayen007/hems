// HEMS Application Frontend Logic
let weeklyChart = null;
let donutChart = null;
let reportChart = null;
let activeCylinder = null;
let currentTariffs = null;
let applianceList = [];
let editingApplianceId = null;
let authenticatedUser = null;
let authRevision = 0;

// Initialize PWA Service Worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/sw.js').catch(console.error);
}

window.addEventListener('online', () => syncOfflineQueue());

// API Fetch with Auth (credentials: include sends session cookie)
async function apiFetch(url, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  const res = await fetch(url, { ...options, credentials: 'include', headers });
  if (res.status === 401) {
    updateAuthUI(null);
  }
  return res;
}

// Check existing authenticated session on page load
async function checkAuthSession() {
  try {
    const res = await fetch('/api/v1/auth/me', {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' }
    });
    if (res.ok) {
      const data = await res.json();
      if (data.status === 'success' && data.user) {
        updateAuthUI(data.user);
        return data.user;
      }
    }
  } catch (e) {
    console.warn('Session check failed:', e);
  }
  updateAuthUI(null);
  return null;
}

// Auth UI State
function updateAuthUI(user) {
  authenticatedUser = user;
  authRevision += 1;
  const userDropdown = document.getElementById('user-dropdown-container');
  const loginBtn = document.getElementById('btn-login-open');
  const displayName = document.getElementById('user-display-name');
  const dropdownHeader = document.getElementById('user-dropdown-header');
  const dropdownRole = document.getElementById('user-dropdown-role');
  const heroName = document.getElementById('hero-household-name');
  const manageAppliancesBtn = document.getElementById('btn-manage-appliances');
  const reportButton = document.getElementById('btn-generate-report');
  const tariffsButton = document.getElementById('btn-tariffs-modal');

  if (user) {
    if (userDropdown) userDropdown.classList.remove('d-none');
    if (loginBtn) loginBtn.classList.add('d-none');
    if (reportButton) reportButton.disabled = false;
    if (tariffsButton) tariffsButton.disabled = false;
    if (manageAppliancesBtn) {
      manageAppliancesBtn.classList.toggle('d-none', user.role !== 'ADMIN');
    }
    if (displayName) displayName.textContent = `${user.username} (${user.role === 'ADMIN' ? 'Admin' : 'Member'})`;
    if (dropdownHeader) dropdownHeader.textContent = `Logged in as ${user.username}`;
    if (dropdownRole) dropdownRole.textContent = `Role: ${user.role === 'ADMIN' ? 'Administrator' : 'Member'}`;
    if (heroName && user.household_name) heroName.textContent = user.household_name;
  } else {
    if (userDropdown) userDropdown.classList.add('d-none');
    if (loginBtn) { loginBtn.classList.remove('d-none'); loginBtn.classList.add('d-inline-flex'); }
    if (manageAppliancesBtn) manageAppliancesBtn.classList.add('d-none');
    if (reportButton) reportButton.disabled = true;
    if (tariffsButton) tariffsButton.disabled = true;
    currentTariffs = null;
    ['tariff-elec', 'tariff-lpg', 'tariff-kero'].forEach(id => {
      const input = document.getElementById(id);
      if (input) input.value = '';
    });
    const tariffDateInput = document.getElementById('tariff-effective-date');
    if (tariffDateInput) tariffDateInput.value = '';
    resetDashboardUI();
  }
}

function openAuthModal(tab = 'login') {
  const modalEl = document.getElementById('modal-auth');
  if (!modalEl) return;
  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
  modal.show();
  // Activate the requested tab
  const tabId = tab === 'signup' ? 'tab-register' : 'tab-login';
  const tabEl = document.getElementById(tabId);
  if (tabEl) bootstrap.Tab.getOrCreateInstance(tabEl).show();
  // Clear any previous alert
  const alert = document.getElementById('auth-alert');
  if (alert) { alert.textContent = ''; alert.classList.add('d-none'); }
}

function resetDashboardUI() {
  const heroName = document.getElementById('hero-household-name');
  if (heroName) heroName.textContent = 'My Household';
  const heroLocation = document.getElementById('hero-location');
  if (heroLocation) heroLocation.textContent = '';
  const heroPeriod = document.getElementById('hero-period-label');
  if (heroPeriod) heroPeriod.textContent = '';
  const totalEnergy = document.getElementById('kpi-total-energy');
  if (totalEnergy) totalEnergy.textContent = '-- kWh';
  const totalCost = document.getElementById('kpi-total-cost');
  if (totalCost) totalCost.textContent = 'KES --';
  const energyBadge = document.getElementById('kpi-energy-badge');
  if (energyBadge) energyBadge.classList.add('d-none');
  const costBreakdown = document.getElementById('kpi-cost-breakdown');
  if (costBreakdown) costBreakdown.textContent = 'Sign in to view breakdown';
  const lpgRemaining = document.getElementById('kpi-lpg-remaining');
  if (lpgRemaining) lpgRemaining.textContent = 'No cylinder registered';
  const lpgTitle = document.getElementById('lpg-card-title');
  if (lpgTitle) lpgTitle.textContent = 'Active Cylinder';
  const lpgBrand = document.getElementById('lpg-card-brand');
  if (lpgBrand) lpgBrand.textContent = 'LPG';
  const lpgMeta = document.getElementById('lpg-card-meta');
  if (lpgMeta) lpgMeta.textContent = 'No active cylinder';
  const solarOffset = document.getElementById('kpi-solar-offset');
  if (solarOffset) solarOffset.textContent = '-- kWh';
  const solarMeta = document.getElementById('solar-card-meta');
  if (solarMeta) solarMeta.textContent = 'Sign in to view household data';
  const advisoryContainer = document.getElementById('advisory-container');
  if (advisoryContainer) advisoryContainer.replaceChildren();
  const lpgFill = document.getElementById('lpg-fill-bar');
  if (lpgFill) {
    lpgFill.style.width = '0%';
    lpgFill.parentElement?.setAttribute('aria-valuenow', '0');
  }
  clearCharts();
  clearRecentLogs();
  clearFuelParity();
  clearReportData();
}

async function handleLogout() {
  try {
    await fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'include' });
  } catch (_) { /* ignore */ }
  updateAuthUI(null);
  showToast('Signed out successfully.', 'info');
}

function clearCharts() {
  weeklyChart?.destroy();
  donutChart?.destroy();
  weeklyChart = null;
  donutChart = null;

  const weeklyState = document.getElementById('weekly-chart-state');
  const donutState = document.getElementById('donut-chart-state');
  if (weeklyState) weeklyState.textContent = 'Sign in to view household data';
  if (donutState) donutState.textContent = 'Sign in to view household data';

  const weeklyTable = document.getElementById('sr-weekly-tbody');
  if (weeklyTable) weeklyTable.replaceChildren();
  ['sr-donut-elec', 'sr-donut-lpg', 'sr-donut-kero', 'sr-donut-solar'].forEach(id => {
    const value = document.getElementById(id);
    if (value) value.textContent = '—';
  });
}

function clearRecentLogs() {
  const tbody = document.getElementById('recent-logs-body');
  if (!tbody) return;
  const row = document.createElement('tr');
  const cell = document.createElement('td');
  cell.colSpan = 4;
  cell.className = 'text-center text-secondary';
  cell.textContent = 'Sign in to view household logs.';
  row.appendChild(cell);
  tbody.replaceChildren(row);
}

function clearFuelParity() {
  const container = document.getElementById('parity-container');
  if (container) container.textContent = 'Sign in to view household cost comparison.';
}

// Offline Queue Persistence
function queueOfflineLog(endpoint, payload) {
  const queue = JSON.parse(localStorage.getItem('hems_offline_queue') || '[]');
  queue.push({ endpoint, payload, timestamp: Date.now() });
  localStorage.setItem('hems_offline_queue', JSON.stringify(queue));
  showToast('Saved offline. Will sync when reconnected.', 'info');
}

async function syncOfflineQueue() {
  const queue = JSON.parse(localStorage.getItem('hems_offline_queue') || '[]');
  if (!queue.length) return;
  
  const remaining = [];
  for (const item of queue) {
    try {
      const res = await apiFetch(item.endpoint, {
        method: 'POST',
        body: JSON.stringify(item.payload)
      });
      if (!res.ok) remaining.push(item);
    } catch (e) {
      remaining.push(item);
    }
  }
  localStorage.setItem('hems_offline_queue', JSON.stringify(remaining));
  if (queue.length > remaining.length) {
    showToast(`Synced ${queue.length - remaining.length} offline log(s)!`, 'success');
    loadDashboard();
  }
}

// Toast Notifications
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const icon = type === 'success' ? 'check-circle-fill' : 'exclamation-circle-fill';
  const toast = document.createElement('div');
  const tone = type === 'error' ? 'danger' : type === 'info' ? 'primary' : 'success';
  toast.className = `toast align-items-center text-bg-${tone} border-0`;
  toast.setAttribute('role', 'status');
  toast.setAttribute('aria-live', 'polite');
  toast.setAttribute('aria-atomic', 'true');
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body d-flex align-items-center gap-2">
        <i class="bi bi-${icon} icon" aria-hidden="true"></i>
        <span></span>
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>`;
  toast.querySelector('.toast-body span').textContent = message;
  container.appendChild(toast);
  toast.addEventListener('hidden.bs.toast', () => toast.remove(), { once: true });
  bootstrap.Toast.getOrCreateInstance(toast, { delay: 4000 }).show();
}

// Dashboard Data Loader
async function loadDashboard() {
  if (!authenticatedUser) return;
  const requestRevision = authRevision;
  try {
    const res = await apiFetch('/api/v1/analytics/dashboard');
    if (!res.ok) return;
    const { data } = await res.json();
    if (requestRevision !== authRevision || !authenticatedUser) return;
    currentTariffs = data.tariffs;
    [
      ['tariff-elec', 'electricity_per_kwh'],
      ['tariff-lpg', 'lpg_per_kg'],
      ['tariff-kero', 'kerosene_per_liter']
    ].forEach(([inputId, rateKey]) => {
      const input = document.getElementById(inputId);
      if (input && data.tariffs?.[rateKey] !== undefined) {
        input.value = data.tariffs[rateKey];
      }
    });
    const tariffDateInput = document.getElementById('tariff-effective-date');
    if (tariffDateInput && data.tariffs?.effective_date) {
      const nextStartDate = new Date(`${String(data.tariffs.effective_date).slice(0, 10)}T00:00:00Z`);
      nextStartDate.setUTCDate(nextStartDate.getUTCDate() + 1);
      tariffDateInput.min = nextStartDate.toISOString().slice(0, 10);
      tariffDateInput.value = tariffDateInput.min;
    }

    // Populate hero section from live data
    const heroName = document.getElementById('hero-household-name');
    const heroPeriod = document.getElementById('hero-period-label');
    const heroLocation = document.getElementById('hero-location');
    if (heroName) heroName.textContent = data.household_name || 'My Household';
    if (heroPeriod) heroPeriod.textContent = data.summary.period_label || data.summary.period;
    if (heroLocation) {
      heroLocation.textContent = data.location_county
        ? `${data.location_county} County \u2022 `
        : '';
    }

    document.getElementById('kpi-total-energy').textContent = `${data.summary.total_energy_kwh.toLocaleString()} kWh`;
    document.getElementById('kpi-total-cost').textContent = `KES ${data.summary.total_cost_kes.toLocaleString()}`;

    const energyBadge = document.getElementById('kpi-energy-badge');
    if (energyBadge) {
      if (data.summary.savings_vs_previous_month_pct !== null && data.summary.savings_vs_previous_month_pct !== undefined) {
        energyBadge.textContent = `${data.summary.savings_vs_previous_month_pct > 0 ? '+' : ''}${data.summary.savings_vs_previous_month_pct}% vs last month`;
        energyBadge.classList.remove('d-none');
      } else {
        energyBadge.classList.add('d-none');
      }
    }

    const costBreakdown = document.getElementById('kpi-cost-breakdown');
    if (costBreakdown && data.source_breakdown) {
      costBreakdown.textContent = `Grid: ${data.source_breakdown.grid_electricity.pct_cost}% • Gas: ${data.source_breakdown.lpg.pct_cost}% • Kerosene: ${data.source_breakdown.kerosene.pct_cost}%`;
    }
    
    activeCylinder = data.active_cylinder;
    document.getElementById('kpi-lpg-remaining').textContent = activeCylinder.id
      ? `${activeCylinder.net_gas_kg} kg (${activeCylinder.percent_remaining}%)`
      : 'No cylinder registered';
    const lpgFill = document.getElementById('lpg-fill-bar');
    if (lpgFill) {
      lpgFill.style.width = `${activeCylinder.percent_remaining}%`;
      lpgFill.parentElement.setAttribute('aria-valuenow', activeCylinder.percent_remaining);
    }

    const lpgTitle = document.getElementById('lpg-card-title');
    const lpgBrand = document.getElementById('lpg-card-brand');
    const lpgMeta = document.getElementById('lpg-card-meta');
    if (lpgTitle) lpgTitle.textContent = activeCylinder.nominal_capacity_kg ? `Active ${activeCylinder.nominal_capacity_kg}kg Cylinder` : 'Active Cylinder';
    if (lpgBrand) lpgBrand.textContent = activeCylinder.brand || 'LPG';
    const lpgProfile = document.getElementById('lpg-profile');
    if (lpgProfile) {
      if (activeCylinder.id && activeCylinder.brand && activeCylinder.brand !== 'None') {
        lpgProfile.value = `${activeCylinder.brand} ${activeCylinder.nominal_capacity_kg}kg (Tare: ${activeCylinder.tare_weight_kg} kg)`;
      } else {
        lpgProfile.value = 'No active cylinder registered';
      }
    }
    if (lpgMeta) {
      if (activeCylinder.id && activeCylinder.brand && activeCylinder.brand !== 'None') {
        lpgMeta.textContent = `Tare: ${activeCylinder.tare_weight_kg || 0} kg • ${activeCylinder.percent_remaining}% full`;
      } else {
        lpgMeta.textContent = 'No active cylinder registered';
      }
    }

    document.getElementById('kpi-solar-offset').textContent = `${data.source_breakdown.solar.kwh} kWh`;
    const solarMeta = document.getElementById('solar-card-meta');
    if (solarMeta && data.source_breakdown?.solar) {
      const savedKes = data.source_breakdown.solar.savings_kes;
      solarMeta.textContent = Number.isFinite(savedKes)
        ? `Avoided ~KES ${savedKes.toLocaleString()} in KPLC electricity tokens`
        : 'Savings estimate unavailable';
    }

    renderCharts(data.source_breakdown, data.weekly_trends);
    renderAdvisories(data.advisory);
    loadRecentLogs();
  } catch (err) {
    console.error('Failed to load dashboard:', err);
  }
}

// Fuel Parity Loader
async function loadFuelParity() {
  if (!authenticatedUser) return;
  const requestRevision = authRevision;
  try {
    const res = await apiFetch('/api/v1/analytics/parity');
    if (!res.ok) return;
    const { data: parity } = await res.json();
    if (requestRevision !== authRevision || !authenticatedUser) return;
    const container = document.getElementById('parity-container');
    if (!container) return;

    const inputEnergyRates = [
      parity.solar.cost_per_kwh_equiv || 0,
      parity.lpg.cost_per_kwh_equiv || 0,
      parity.grid_electricity.cost_per_kwh_equiv || 0,
      parity.kerosene.cost_per_kwh_equiv || 0
    ];
    const maxCost = Math.max(...inputEnergyRates, 1);

    const fuelRates = [
      parity.lpg.cost_per_kwh_equiv,
      parity.grid_electricity.cost_per_kwh_equiv,
      parity.kerosene.cost_per_kwh_equiv
    ];
    const lowestFuelRate = Math.min(...fuelRates);
    const highestFuelRate = Math.max(...fuelRates);
    const rateBadge = rate => {
      if (rate === lowestFuelRate) return { text: 'Lowest input-energy rate', color: 'success' };
      if (rate === highestFuelRate) return { text: 'Highest input-energy rate', color: 'danger' };
      return { text: 'Input-energy rate', color: 'secondary' };
    };
    const relativeWidth = rate => Math.max(0, (rate / maxCost) * 100);

    const sources = [
      { icon: 'sun-fill', name: 'Solar PV Harvest', note: 'Zero marginal-cost assumption', rate: parity.solar.cost_per_kwh_equiv, effectiveDate: parity.solar.effective_date, badge: 'Zero marginal fuel cost', color: 'success', bar: 'solar' },
      { icon: 'fire', name: 'LPG Cooking Gas', note: `${parity.lpg.retail_rate.toFixed(2)} KES / kg`, rate: parity.lpg.cost_per_kwh_equiv, effectiveDate: parity.lpg.effective_date, ...rateBadge(parity.lpg.cost_per_kwh_equiv), bar: 'lpg' },
      { icon: 'lightning-charge-fill', name: 'KPLC Grid Electricity', note: `${parity.grid_electricity.retail_rate.toFixed(2)} KES / kWh`, rate: parity.grid_electricity.cost_per_kwh_equiv, effectiveDate: parity.grid_electricity.effective_date, ...rateBadge(parity.grid_electricity.cost_per_kwh_equiv), bar: 'elec' },
      { icon: 'droplet-fill', name: 'Domestic Kerosene', note: `${parity.kerosene.retail_rate.toFixed(2)} KES / litre`, rate: parity.kerosene.cost_per_kwh_equiv, effectiveDate: parity.kerosene.effective_date, ...rateBadge(parity.kerosene.cost_per_kwh_equiv), bar: 'kero' }
    ];
    sources.forEach(source => {
      source.width = relativeWidth(source.rate);
    });
    container.innerHTML = sources.map(source => `
      <div class="border rounded p-2">
        <div class="d-flex justify-content-between align-items-center gap-2 mb-2">
          <span class="fw-semibold small"><i class="bi bi-${source.icon} icon" aria-hidden="true"></i> ${source.name}</span>
          <span class="badge bg-${source.color}-subtle text-${source.color}-emphasis">${source.badge}</span>
        </div>
        <div class="progress parity-bar mb-2" role="progressbar" aria-label="${source.name} input-energy cost relative to the most expensive source" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${source.width.toFixed(1)}">
          <div class="progress-bar progress-bar-${source.bar}" style="width: ${source.width.toFixed(1)}%"></div>
        </div>
        <div class="d-flex justify-content-between gap-2 small">
          <span class="text-secondary">${source.note}</span>
          <span class="fw-semibold text-nowrap">KES ${source.rate.toFixed(2)} / kWh</span>
        </div>
        <div class="small text-secondary mt-1">Rate set effective ${formatRateDate(source.effectiveDate)}</div>
      </div>`).join('');
  } catch (e) {
    console.error(e);
  }
}

function formatRateDate(value) {
  const datePart = String(value || '').slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(datePart)) return 'date unavailable';
  return new Date(`${datePart}T00:00:00Z`).toLocaleDateString('en-KE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC'
  });
}

function formatLocalDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function updateReportDateFields() {
  const period = document.getElementById('report-period')?.value;
  const range = document.getElementById('report-custom-range');
  const startInput = document.getElementById('report-start-date');
  const endInput = document.getElementById('report-end-date');
  if (!range || !startInput || !endInput) return;

  const isCustom = period === 'custom';
  range.classList.toggle('d-none', !isCustom);
  startInput.disabled = !isCustom;
  endInput.disabled = !isCustom;
  if (isCustom) return;

  const today = new Date();
  let start;
  let end;
  if (period === 'week') {
    start = new Date(today);
    start.setDate(today.getDate() - ((today.getDay() + 6) % 7));
    end = new Date(start);
    end.setDate(start.getDate() + 6);
  } else {
    start = new Date(today.getFullYear(), today.getMonth(), 1);
    end = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  }
  startInput.value = formatLocalDate(start);
  endInput.value = formatLocalDate(end);
}

function clearReportData() {
  reportChart?.destroy();
  reportChart = null;
  document.getElementById('report-results')?.classList.add('d-none');
  const status = document.getElementById('report-status');
  if (status) {
    status.textContent = 'Sign in to generate a household report.';
    status.className = 'small text-secondary mb-0';
  }
  document.getElementById('report-sources-table')?.replaceChildren();
  document.getElementById('report-trends-table')?.replaceChildren();
  document.getElementById('report-advisory')?.replaceChildren();
}

async function loadEnergyReport() {
  const startDate = document.getElementById('report-start-date')?.value;
  const endDate = document.getElementById('report-end-date')?.value;
  const status = document.getElementById('report-status');
  if (!startDate || !endDate || !status) return;

  status.textContent = 'Generating report...';
  status.className = 'small text-secondary mb-0';
  try {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    const response = await apiFetch(`/api/v1/analytics/report?${params}`);
    const body = await response.json();
    if (!response.ok) {
      throw new Error(body.message || 'Could not generate the report.');
    }
    renderEnergyReport(body.data);
  } catch (error) {
    console.error('Failed to generate energy report:', error);
    status.textContent = error.message || 'Could not generate the report.';
    status.className = 'small text-danger mb-0';
    document.getElementById('report-results')?.classList.add('d-none');
  }
}

function renderEnergyReport(report) {
  const { summary, source_breakdown: sources, daily_trends: trends, advisory } = report;
  const status = document.getElementById('report-status');
  const results = document.getElementById('report-results');
  document.getElementById('report-period-label').textContent =
    `${summary.start_date} through ${summary.end_date}`;
  document.getElementById('report-total-energy').textContent =
    `${Number(summary.total_energy_kwh).toLocaleString()} kWh`;
  document.getElementById('report-total-cost').textContent =
    `KES ${Number(summary.total_cost_kes).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const sourceRows = document.getElementById('report-sources-table');
  sourceRows.replaceChildren();
  const sourceLabels = [
    ['grid_electricity', 'Grid electricity'],
    ['lpg', 'LPG'],
    ['kerosene', 'Kerosene'],
    ['solar', 'Solar']
  ];
  sourceLabels.forEach(([key, label]) => {
    const source = sources[key];
    const row = sourceRows.insertRow();
    [label, `${source.quantity} ${source.unit}`, `${source.kwh} kWh`,
      `KES ${Number(source.cost_kes).toFixed(2)}`].forEach(value => {
      row.insertCell().textContent = value;
    });
  });

  const trendRows = document.getElementById('report-trends-table');
  trendRows.replaceChildren();
  trends.forEach(trend => {
    const row = trendRows.insertRow();
    [
      trend.date,
      `${trend.grid_electricity_kwh} kWh`,
      `${trend.lpg_kwh} kWh`,
      `${trend.kerosene_kwh} kWh`,
      `${trend.solar_kwh} kWh`
    ].forEach(value => {
      row.insertCell().textContent = value;
    });
  });
  renderReportChart(trends);
  renderReportAdvisories(advisory);

  const chartState = document.getElementById('report-chart-state');
  chartState.textContent = trends.length ? 'Daily energy' : 'No entries in this period';
  results.classList.remove('d-none');
  status.textContent = `Report generated for ${summary.start_date} through ${summary.end_date}.`;
}

function renderReportChart(trends) {
  const canvas = document.getElementById('reportChart');
  if (!canvas || !window.Chart) return;
  reportChart?.destroy();
  reportChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels: trends.map(trend => trend.date),
      datasets: [
        { label: 'Grid electricity', data: trends.map(item => item.grid_electricity_kwh), borderColor: '#238eaa', tension: 0.25 },
        { label: 'LPG', data: trends.map(item => item.lpg_kwh), borderColor: '#d7a827', tension: 0.25 },
        { label: 'Kerosene', data: trends.map(item => item.kerosene_kwh), borderColor: '#c75b4b', tension: 0.25 },
        { label: 'Solar', data: trends.map(item => item.solar_kwh), borderColor: '#198754', tension: 0.25 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { position: 'bottom' } },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: 'Energy (kWh)' } }
      }
    }
  });
}

function renderReportAdvisories(advisories) {
  const container = document.getElementById('report-advisory');
  if (!container) return;
  container.replaceChildren();
  container.className = '';
  if (!advisories.length) {
    container.textContent = 'No additional efficiency recommendations for this period.';
    container.className = 'small text-secondary';
    return;
  }
  advisories.forEach(advisory => {
    const alert = document.createElement('div');
    alert.className = 'alert alert-warning mb-2';
    alert.setAttribute('role', 'status');
    const title = document.createElement('h3');
    title.className = 'h6 fw-semibold';
    title.textContent = advisory.title;
    const message = document.createElement('p');
    message.className = 'mb-0';
    message.textContent = advisory.message;
    alert.append(title, message);
    container.appendChild(alert);
  });
}

function setupReportForm() {
  const period = document.getElementById('report-period');
  const form = document.getElementById('form-report-range');
  updateReportDateFields();
  period?.addEventListener('change', updateReportDateFields);
  form?.addEventListener('submit', event => {
    event.preventDefault();
    loadEnergyReport();
  });
}

function renderCharts(breakdown, weeklyTrends = null) {
  const weeklyState = document.getElementById('weekly-chart-state');
  const donutState = document.getElementById('donut-chart-state');
  const breakdownData = breakdown || {};
  if (donutState) {
    const hasSpend = ['grid_electricity', 'lpg', 'kerosene']
      .some(source => (breakdownData[source]?.pct_cost ?? 0) > 0);
    donutState.textContent = hasSpend ? 'Household mix' : 'No spend logged yet';
  }

  const labels = weeklyTrends?.labels || [];
  const elecData = weeklyTrends?.electricity || [];
  const lpgData = weeklyTrends?.lpg || [];
  const keroseneData = weeklyTrends?.kerosene || [];
  const solarData = weeklyTrends?.solar || [];

  const hasWeeklyLogs = [elecData, lpgData, keroseneData, solarData]
    .some(source => source.some(value => value > 0));
  if (weeklyState) {
    if (hasWeeklyLogs) {
      weeklyState.textContent = '4-Week Live Consumption';
    } else {
      weeklyState.textContent = 'No usage logged yet';
    }
  }

  // Update screen-reader accessible tables
  const srTbody = document.getElementById('sr-weekly-tbody');
  if (srTbody) {
    srTbody.innerHTML = labels.map((lbl, idx) => `
      <tr>
        <td>${lbl}</td>
        <td>${(elecData[idx] ?? 0).toFixed(1)}</td>
        <td>${(lpgData[idx] ?? 0).toFixed(1)}</td>
        <td>${(keroseneData[idx] ?? 0).toFixed(1)}</td>
        <td>${(solarData[idx] ?? 0).toFixed(1)}</td>
      </tr>
    `).join('');
  }

  const srDonutElec = document.getElementById('sr-donut-elec');
  const srDonutLpg = document.getElementById('sr-donut-lpg');
  const srDonutKero = document.getElementById('sr-donut-kero');
  const srDonutSolar = document.getElementById('sr-donut-solar');
  if (srDonutElec) srDonutElec.textContent = `${(breakdownData.grid_electricity?.pct_cost ?? 0).toFixed(1)}%`;
  if (srDonutLpg) srDonutLpg.textContent = `${(breakdownData.lpg?.pct_cost ?? 0).toFixed(1)}%`;
  if (srDonutKero) srDonutKero.textContent = `${(breakdownData.kerosene?.pct_cost ?? 0).toFixed(1)}%`;
  if (srDonutSolar) srDonutSolar.textContent = `${(breakdownData.solar?.pct_cost ?? 0).toFixed(1)}%`;

  // 1. Weekly Trends Area Chart
  const ctxWeekly = document.getElementById('weeklyChart');
  if (ctxWeekly && window.Chart) {
    if (weeklyChart) weeklyChart.destroy();
    const ctx = ctxWeekly.getContext('2d');

    const gradElec = ctx.createLinearGradient(0, 0, 0, 240);
    gradElec.addColorStop(0, 'rgba(6, 182, 212, 0.35)');
    gradElec.addColorStop(1, 'rgba(6, 182, 212, 0.01)');

    const gradLpg = ctx.createLinearGradient(0, 0, 0, 240);
    gradLpg.addColorStop(0, 'rgba(245, 158, 11, 0.35)');
    gradLpg.addColorStop(1, 'rgba(245, 158, 11, 0.01)');

    const gradKerosene = ctx.createLinearGradient(0, 0, 0, 240);
    gradKerosene.addColorStop(0, 'rgba(199, 91, 75, 0.35)');
    gradKerosene.addColorStop(1, 'rgba(199, 91, 75, 0.01)');

    const gradSolar = ctx.createLinearGradient(0, 0, 0, 240);
    gradSolar.addColorStop(0, 'rgba(16, 185, 129, 0.35)');
    gradSolar.addColorStop(1, 'rgba(16, 185, 129, 0.01)');

    weeklyChart = new Chart(ctxWeekly, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Grid Electricity',
            data: elecData,
            borderColor: '#238eaa',
            backgroundColor: gradElec,
            borderWidth: 2.5,
            fill: true,
            tension: 0.38,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: '#ffffff',
            pointHoverBorderColor: '#238eaa',
            pointHoverBorderWidth: 2
          },
          {
            label: 'LPG Gas Equiv',
            data: lpgData,
            borderColor: '#d7a827',
            backgroundColor: gradLpg,
            borderWidth: 2.5,
            fill: true,
            tension: 0.38,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: '#ffffff',
            pointHoverBorderColor: '#d7a827',
            pointHoverBorderWidth: 2
          },
          {
            label: 'Kerosene',
            data: keroseneData,
            borderColor: '#c75b4b',
            backgroundColor: gradKerosene,
            borderWidth: 2.5,
            fill: true,
            tension: 0.38,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: '#ffffff',
            pointHoverBorderColor: '#c75b4b',
            pointHoverBorderWidth: 2
          },
          {
            label: 'Solar Harvest',
            data: solarData,
            borderColor: '#198754',
            backgroundColor: gradSolar,
            borderWidth: 2.5,
            fill: true,
            tension: 0.38,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: '#ffffff',
            pointHoverBorderColor: '#198754',
            pointHoverBorderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: {
              color: '#475569',
              usePointStyle: true,
              pointStyle: 'circle',
              boxWidth: 8,
              boxHeight: 8,
              padding: 16,
              font: { family: 'system-ui, sans-serif', size: 12, weight: '500' }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.96)',
            titleColor: '#f8fafc',
            bodyColor: '#cbd5e1',
            borderColor: 'rgba(255, 255, 255, 0.12)',
            borderWidth: 1,
            padding: 12,
            boxPadding: 6,
            cornerRadius: 10,
            usePointStyle: true,
            callbacks: {
              label: function(ctx) {
                return ` ${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)} kWh`;
              }
            }
          }
        },
        scales: {
          x: {
            ticks: { color: '#475569', font: { family: 'system-ui, sans-serif', size: 11 } },
            grid: { color: 'rgba(15, 23, 42, 0.08)' }
          },
          y: {
            ticks: {
              color: '#475569',
              font: { family: 'system-ui, sans-serif', size: 11 },
              callback: (val) => `${val} kWh`
            },
            grid: { color: 'rgba(15, 23, 42, 0.08)' }
          }
        }
      }
    });
  }

  // 2. Fuel Expense Donut Chart with Center Stat Plugin
  const ctxDonut = document.getElementById('donutChart');
  if (ctxDonut && window.Chart) {
    if (donutChart) donutChart.destroy();

    const centerStatPlugin = {
      id: 'centerStatPlugin',
      beforeDraw(chart) {
        const { width, height, ctx } = chart;
        ctx.save();
        const costElem = document.getElementById('kpi-total-cost');
        const costStr = costElem ? costElem.textContent : 'KES --';

        const subSize = Math.max(9, Math.min(12, Math.round(width * 0.038)));
        const mainSize = Math.max(12, Math.min(16, Math.round(width * 0.055)));

        ctx.font = `600 ${subSize}px system-ui, sans-serif`;
        ctx.fillStyle = '#475569';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('EST. SPEND', width / 2, height / 2 - (mainSize * 0.75));

        ctx.font = `800 ${mainSize}px system-ui, sans-serif`;
        ctx.fillStyle = '#212529';
        ctx.fillText(costStr, width / 2, height / 2 + (mainSize * 0.65));
        ctx.restore();
      }
    };

    donutChart = new Chart(ctxDonut, {
      type: 'doughnut',
      plugins: [centerStatPlugin],
      data: {
        labels: ['Grid Electricity', 'LPG Gas', 'Kerosene', 'Solar Offset'],
        datasets: [{
          data: [
            breakdownData.grid_electricity?.pct_cost ?? 0,
            breakdownData.lpg?.pct_cost ?? 0,
            breakdownData.kerosene?.pct_cost ?? 0,
            breakdownData.solar?.pct_cost ?? 0
          ],
          backgroundColor: ['#238eaa', '#d7a827', '#c75b4b', '#198754'],
          borderColor: '#ffffff',
          borderWidth: 4,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#475569',
              boxWidth: 8,
              boxHeight: 8,
              usePointStyle: true,
              pointStyle: 'circle',
              padding: 12,
              font: { family: 'system-ui, sans-serif', size: 11, weight: '500' }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.96)',
            titleColor: '#f8fafc',
            bodyColor: '#cbd5e1',
            borderColor: 'rgba(255, 255, 255, 0.12)',
            borderWidth: 1,
            padding: 10,
            cornerRadius: 8,
            usePointStyle: true,
            callbacks: {
              label: function(ctx) {
                return ` ${ctx.label}: ${ctx.parsed.toFixed(1)}% of budget`;
              }
            }
          }
        },
        cutout: '72%'
      }
    });
  }
}

// Advisories Renderer
function renderAdvisories(advisories) {
  const container = document.getElementById('advisory-container');
  if (!container) return;
  if (!advisories || !advisories.length) {
    container.innerHTML = '';
    return;
  }
  container.innerHTML = advisories.map(adv => `
    <div class="alert alert-warning d-flex align-items-start gap-3 mb-2" role="status">
      <i class="bi bi-lightbulb-fill icon flex-shrink-0 mt-1" aria-hidden="true"></i>
      <div>
        <h2 class="h6 fw-semibold mb-1">${adv.title}</h2>
        <p class="mb-1">${adv.message}</p>
        ${adv.potential_monthly_saving_kes > 0 ? `<span class="badge text-bg-success">Potential monthly saving from shifting loads: KES ${adv.potential_monthly_saving_kes.toFixed(2)}</span>` : ''}
        ${adv.estimated_avoided_cost_kes > 0 ? `<span class="badge text-bg-info">Estimated KPLC cost already avoided: KES ${adv.estimated_avoided_cost_kes.toFixed(2)}</span>` : ''}
      </div>
    </div>`).join('');
}

function getSourceIcon(source) {
  const icons = {
    LPG: 'fire',
    Electricity: 'lightning-charge-fill',
    Kerosene: 'droplet-fill',
    Solar: 'sun-fill'
  };
  return icons[source] || 'lightning-charge-fill';
}

function formatLogTimestamp(logDate, createdAt) {
  const raw = createdAt || logDate;
  if (!raw) return '--';
  if (typeof raw === 'string') {
    if (raw.includes(' ') || raw.includes('T')) {
      const parts = raw.replace('T', ' ').split(' ');
      const datePart = parts[0];
      const timePart = parts[1]?.slice(0, 5);
      if (timePart && timePart !== '00:00') {
        return `${datePart} <small class="text-secondary">${timePart}</small>`;
      }
      return datePart;
    }
    return raw.slice(0, 10);
  }
  return String(raw).slice(0, 10);
}

// Recent Logs Loader
async function loadRecentLogs() {
  if (!authenticatedUser) return;
  const requestRevision = authRevision;
  try {
    const res = await apiFetch('/api/v1/fuel-logs/recent');
    if (!res.ok) return;
    const { data: rows = [] } = await res.json();
    if (requestRevision !== authRevision || !authenticatedUser) return;
    const tbody = document.getElementById('recent-logs-body');
    if (!tbody) return;

    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="4" class="text-center text-secondary">No recent fuel logs recorded yet.</td></tr>';
      return;
    }

    const sourceBadges = {
      LPG: 'text-bg-warning',
      Electricity: 'text-bg-info',
      Kerosene: 'text-bg-danger',
      Solar: 'text-bg-success'
    };
    tbody.innerHTML = rows.map(r => `
      <tr>
        <td>${formatLogTimestamp(r.log_date, r.created_at)}</td>
        <td><span class="badge energy-source-badge ${sourceBadges[r.source] || 'text-bg-secondary'}"><i class="bi bi-${getSourceIcon(r.source)} icon" aria-hidden="true"></i> ${r.source}</span></td>
        <td>${r.amount} ${r.unit} ${r.is_refill_event ? '<strong>(Refill)</strong>' : ''}</td>
        <td><strong>${r.computed_kwh.toFixed(3)} kWh</strong></td>
      </tr>
    `).join('');
  } catch (e) {
    console.error(e);
  }
}

// Button Loading Helper
function setButtonLoading(btn, isLoading) {
  if (!btn) return;
  if (isLoading) {
    btn.dataset.originalText = btn.innerHTML;
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    btn.insertAdjacentHTML('beforeend', '<span class="spinner-border spinner-border-sm ms-2" aria-hidden="true"></span>');
  } else {
    btn.disabled = false;
    btn.removeAttribute('aria-busy');
    if (btn.dataset.originalText) {
      btn.innerHTML = btn.dataset.originalText;
      delete btn.dataset.originalText;
    }
  }
}

function openModal(id) {
  const m = document.getElementById(id);
  if (!m) return;
  bootstrap.Modal.getOrCreateInstance(m).show();
}

function closeModal(id) {
  const m = document.getElementById(id);
  if (!m) return;
  // Blur focused child before hide to avoid aria-hidden-on-focused-element warning
  const focused = m.querySelector(':focus');
  if (focused) focused.blur();
  bootstrap.Modal.getOrCreateInstance(m).hide();
}

// LPG Form Dynamic Calculator
function setupLpgForm() {
  const input = document.getElementById('lpg-gross-weight');
  const refillBox = document.getElementById('lpg-refill-check');
  const submitBtn = document.getElementById('btn-submit-lpg');
  if (!input) return;

  function recalculate() {
    const rawVal = parseFloat(input.value);
    const tare = parseFloat(activeCylinder?.tare_weight_kg);
    const nominal = parseFloat(activeCylinder?.nominal_capacity_kg);
    const isRefill = refillBox ? refillBox.checked : false;

    if (isNaN(rawVal) || rawVal <= 0) {
      document.getElementById('calc-net-gas').textContent = '0.00 kg (0.0%)';
      document.getElementById('calc-burned-kwh').textContent = '0.00 kg (0.00 kWh)';
      document.getElementById('calc-val-kes').textContent = 'KES 0.00';
      return;
    }

    if (!activeCylinder?.id || !Number.isFinite(tare) || !Number.isFinite(nominal)) {
      document.getElementById('calc-net-gas').textContent = 'No active cylinder registered';
      document.getElementById('calc-burned-kwh').textContent = '--';
      document.getElementById('calc-val-kes').textContent = 'KES --';
      return;
    }

    const gross = rawVal;
    const net = Math.max(0, gross - tare);
    const pct = Math.min(100, Math.max(0, (net / nominal) * 100));

    let burned = 0.0;
    if (activeCylinder && !isRefill) {
      const prevNet = parseFloat(activeCylinder.net_gas_kg) || 0.0;
      const prevGross = prevNet + tare;
      if (prevGross > gross) {
        burned = prevGross - gross;
      }
    }
    const kwh = burned * 12.80;
    const tariffRate = parseFloat(currentTariffs?.lpg_per_kg);
    const cost = Number.isFinite(tariffRate) ? `KES ${(burned * tariffRate).toFixed(2)}` : 'KES --';

    document.getElementById('calc-net-gas').textContent = `${net.toFixed(2)} kg (${pct.toFixed(1)}%)`;
    document.getElementById('calc-burned-kwh').textContent = `${burned.toFixed(2)} kg (${kwh.toFixed(2)} kWh)`;
    document.getElementById('calc-val-kes').textContent = cost;
  }

  input.addEventListener('input', recalculate);
  if (refillBox) refillBox.addEventListener('change', recalculate);

  const form = document.getElementById('form-lpg-log');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const grossWeight = parseFloat(input.value);
      const tare = parseFloat(activeCylinder?.tare_weight_kg);
      const previousGross = (parseFloat(activeCylinder?.net_gas_kg) || 0) + tare;
      const refillConfirmed = refillBox.checked;
      const implicitRefill = Number.isFinite(previousGross) && grossWeight > previousGross;
      const confirmZeroConsumption = !refillConfirmed && !implicitRefill
        && window.confirm(
          'This reading may record 0 kg LPG consumed. Save it as a baseline or zero-usage reading?'
        );
      if (!refillConfirmed && !implicitRefill && !confirmZeroConsumption) return;

      setButtonLoading(submitBtn, true);

      const payload = {
        cylinder_id: (activeCylinder && activeCylinder.id) ? activeCylinder.id : null,
        log_date: document.getElementById('lpg-log-date').value || new Date().toISOString().slice(0, 10),
        gross_weight_kg: grossWeight,
        is_refill_event: refillConfirmed,
        confirm_zero_consumption: confirmZeroConsumption
      };

      if (!navigator.onLine) {
        queueOfflineLog('/api/v1/fuel-logs/lpg', payload);
        setButtonLoading(submitBtn, false);
        closeModal('modal-lpg');
        return;
      }

      try {
        const res = await apiFetch('/api/v1/fuel-logs/lpg', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          showToast('LPG reading saved successfully!');
          closeModal('modal-lpg');
          loadDashboard();
        } else {
          const response = await res.json();
          showToast(response.message || 'Failed to save reading', 'error');
        }
      } catch (err) {
        queueOfflineLog('/api/v1/fuel-logs/lpg', payload);
        closeModal('modal-lpg');
      } finally {
        setButtonLoading(submitBtn, false);
      }
    });
  }
}

function updateAppliancePreview() {
  const select = document.getElementById('appliance-select');
  const hoursInput = document.getElementById('appliance-runtime');
  if (!select || !hoursInput) return;
  const opt = select.selectedOptions[0];
  if (!opt) return;
  const watt = parseFloat(opt.getAttribute('data-watt') || 0);
  const duty = parseFloat(opt.getAttribute('data-duty') || 1.0);
  const hours = parseFloat(hoursInput.value) || 0;
  const kwh = (watt * hours * duty) / 1000.0;
  const tariffRate = parseFloat(currentTariffs?.electricity_per_kwh);
  const cost = Number.isFinite(tariffRate) ? `KES ${(kwh * tariffRate).toFixed(2)}` : 'KES --';

  document.getElementById('appliance-calc-kwh').textContent = `${kwh.toFixed(3)} kWh`;
  document.getElementById('appliance-calc-cost').textContent = cost;
}

async function loadAppliances() {
  try {
    const res = await apiFetch('/api/v1/appliances');
    if (!res.ok) {
      throw new Error(`Appliance list request failed (${res.status}).`);
    }
    const json = await res.json();
    if (!Array.isArray(json.data)) {
      throw new Error('Appliance list response was invalid.');
    }
    applianceList = json.data;
    const select = document.getElementById('appliance-select');
    if (select) {
      const selectedId = select.value;
      select.replaceChildren();
      applianceList.forEach(appliance => {
        const option = document.createElement('option');
        option.value = appliance.id;
        option.dataset.watt = appliance.rated_wattage;
        option.dataset.duty = appliance.default_duty_cycle;
        option.textContent = `${appliance.name} (${appliance.rated_wattage}W)`;
        select.appendChild(option);
      });
      if (applianceList.some(appliance => String(appliance.id) === selectedId)) {
        select.value = selectedId;
      }
      updateAppliancePreview();
    }
    renderManagedAppliances();
  } catch (error) {
    console.error('Failed to load appliance profiles:', error);
    const feedback = document.getElementById('appliance-profile-feedback');
    if (feedback) {
      feedback.textContent = 'Could not load appliance profiles. Please try again.';
      feedback.className = 'small mb-0 mt-2 text-danger';
    }
  }
}

function renderManagedAppliances() {
  const tbody = document.getElementById('managed-appliances-body');
  if (!tbody) return;
  tbody.replaceChildren();

  if (!applianceList.length) {
    const row = tbody.insertRow();
    const cell = row.insertCell();
    cell.colSpan = 5;
    cell.className = 'text-center text-secondary';
    cell.textContent = 'No appliance profiles yet.';
    return;
  }

  applianceList.forEach(appliance => {
    const row = tbody.insertRow();
    [appliance.name, appliance.category, `${appliance.rated_wattage} W`,
      Number(appliance.default_duty_cycle).toFixed(2)].forEach(value => {
      row.insertCell().textContent = value;
    });
    const actions = row.insertCell();
    actions.className = 'appliance-actions';

    const editButton = document.createElement('button');
    editButton.type = 'button';
    editButton.className = 'btn btn-sm btn-outline-secondary me-1';
    editButton.textContent = 'Edit';
    editButton.setAttribute('aria-label', `Edit ${appliance.name}`);
    editButton.addEventListener('click', () => editApplianceProfile(appliance));
    actions.appendChild(editButton);

    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.className = 'btn btn-sm btn-outline-danger';
    deleteButton.textContent = 'Delete';
    deleteButton.setAttribute('aria-label', `Delete ${appliance.name}`);
    deleteButton.addEventListener('click', () => deleteApplianceProfile(appliance));
    actions.appendChild(deleteButton);
  });
}

function editApplianceProfile(appliance) {
  editingApplianceId = appliance.id;
  document.getElementById('appliance-profile-name').value = appliance.name;
  document.getElementById('appliance-profile-category').value = appliance.category;
  document.getElementById('appliance-profile-wattage').value = appliance.rated_wattage;
  document.getElementById('appliance-profile-duty').value = appliance.default_duty_cycle;
  document.getElementById('btn-submit-appliance-profile').textContent = 'Save changes';
  document.getElementById('btn-cancel-appliance-edit').classList.remove('d-none');
  document.getElementById('appliance-profile-feedback').textContent = '';
  document.getElementById('appliance-profile-name').focus();
}

function resetApplianceProfileForm() {
  document.getElementById('form-appliance-profile').reset();
  editingApplianceId = null;
  document.getElementById('btn-submit-appliance-profile').textContent = 'Add appliance';
  document.getElementById('btn-cancel-appliance-edit').classList.add('d-none');
  const feedback = document.getElementById('appliance-profile-feedback');
  feedback.textContent = '';
  feedback.className = 'small mb-0 mt-2';
}

async function deleteApplianceProfile(appliance) {
  const confirmed = window.confirm(
    `Delete ${appliance.name}? Its runtime logs will also be deleted.`
  );
  if (!confirmed) return;

  try {
    const res = await apiFetch(`/api/v1/appliances/${appliance.id}`, {
      method: 'DELETE'
    });
    const body = await res.json();
    if (!res.ok) {
      throw new Error(body.message || 'Could not delete appliance.');
    }
    if (editingApplianceId === appliance.id) resetApplianceProfileForm();
    await loadAppliances();
    await loadDashboard();
    showToast('Appliance profile deleted.');
  } catch (error) {
    console.error('Failed to delete appliance profile:', error);
    showToast(error.message || 'Could not delete appliance.', 'error');
  }
}

function setupApplianceManagement() {
  const form = document.getElementById('form-appliance-profile');
  const feedback = document.getElementById('appliance-profile-feedback');
  const submitButton = document.getElementById('btn-submit-appliance-profile');
  const manageButton = document.getElementById('btn-manage-appliances');
  const cancelButton = document.getElementById('btn-cancel-appliance-edit');
  manageButton?.addEventListener('click', loadAppliances);
  cancelButton?.addEventListener('click', resetApplianceProfileForm);
  if (!form || !feedback || !submitButton) return;

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const payload = {
      name: document.getElementById('appliance-profile-name').value.trim(),
      category: document.getElementById('appliance-profile-category').value.trim(),
      rated_wattage: Number(document.getElementById('appliance-profile-wattage').value),
      default_duty_cycle: Number(document.getElementById('appliance-profile-duty').value)
    };
    const isEditing = editingApplianceId !== null;
    const url = isEditing
      ? `/api/v1/appliances/${editingApplianceId}`
      : '/api/v1/appliances';

    setButtonLoading(submitButton, true);
    feedback.textContent = '';
    try {
      const res = await apiFetch(url, {
        method: isEditing ? 'PUT' : 'POST',
        body: JSON.stringify(payload)
      });
      const body = await res.json();
      if (!res.ok) {
        throw new Error(body.message || 'Could not save appliance profile.');
      }
      resetApplianceProfileForm();
      await loadAppliances();
      await loadDashboard();
      showToast(isEditing ? 'Appliance profile updated.' : 'Appliance profile added.');
    } catch (error) {
      console.error('Failed to save appliance profile:', error);
      feedback.textContent = error.message || 'Could not save appliance profile.';
      feedback.className = 'small mb-0 mt-2 text-danger';
    } finally {
      setButtonLoading(submitButton, false);
      submitButton.textContent = editingApplianceId ? 'Save changes' : 'Add appliance';
    }
  });
}

// Appliance Form Setup
function setupApplianceForm() {
  const select = document.getElementById('appliance-select');
  const hoursInput = document.getElementById('appliance-runtime');
  if (select) select.addEventListener('change', updateAppliancePreview);
  if (hoursInput) hoursInput.addEventListener('input', updateAppliancePreview);

  const form = document.getElementById('form-appliance-log');
  const submitApplianceBtn = document.getElementById('btn-submit-appliance');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      setButtonLoading(submitApplianceBtn, true);
      const payload = {
        log_date: document.getElementById('appliance-log-date').value || new Date().toISOString().slice(0, 10),
        entries: [
          {
            appliance_id: parseInt(select.value),
            runtime_hours: parseFloat(hoursInput.value)
          }
        ]
      };

      try {
        const res = await apiFetch('/api/v1/appliances/batch-log', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          showToast('Appliance runtime recorded!');
          closeModal('modal-appliance');
          loadDashboard();
        } else {
          showToast('Failed to record runtime', 'error');
        }
      } catch (err) {
        queueOfflineLog('/api/v1/appliances/batch-log', payload);
        closeModal('modal-appliance');
      } finally {
        setButtonLoading(submitApplianceBtn, false);
      }
    });
  }
}

// Other Fuel Log Forms
function setupOtherFuelForms() {
  const formKero = document.getElementById('form-kerosene-log');
  const submitKeroBtn = document.getElementById('btn-submit-fuel');
  if (formKero) {
    formKero.addEventListener('submit', async (e) => {
      e.preventDefault();
      setButtonLoading(submitKeroBtn, true);
      const payload = {
        log_date: document.getElementById('kero-log-date').value || new Date().toISOString().slice(0, 10),
        liters_used: parseFloat(document.getElementById('kero-liters').value),
        purpose: document.getElementById('kero-purpose').value
      };
      try {
        const res = await apiFetch('/api/v1/fuel-logs/kerosene', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          showToast('Kerosene log saved!');
          closeModal('modal-fuel');
          loadDashboard();
        } else {
          showToast('Failed to save kerosene log', 'error');
        }
      } catch (err) {
        showToast('Network error saving kerosene log', 'error');
      } finally {
        setButtonLoading(submitKeroBtn, false);
      }
    });
  }

  const formSolar = document.getElementById('form-solar-log');
  const submitSolarBtn = document.getElementById('btn-submit-solar');
  if (formSolar) {
    formSolar.addEventListener('submit', async (e) => {
      e.preventDefault();
      setButtonLoading(submitSolarBtn, true);
      const payload = {
        log_date: document.getElementById('solar-log-date').value || new Date().toISOString().slice(0, 10),
        yield_kwh: parseFloat(document.getElementById('solar-yield').value)
      };
      try {
        const res = await apiFetch('/api/v1/fuel-logs/solar', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          showToast('Solar generation logged!');
          closeModal('modal-solar');
          loadDashboard();
        } else {
          showToast('Failed to save solar log', 'error');
        }
      } catch (err) {
        showToast('Network error saving solar log', 'error');
      } finally {
        setButtonLoading(submitSolarBtn, false);
      }
    });
  }

  const formTariff = document.getElementById('form-tariff');
  const submitTariffBtn = document.getElementById('btn-submit-tariff');
  if (formTariff) {
    formTariff.addEventListener('submit', async (e) => {
      e.preventDefault();
      setButtonLoading(submitTariffBtn, true);
      const payload = {
        electricity_per_kwh: parseFloat(document.getElementById('tariff-elec').value),
        lpg_per_kg: parseFloat(document.getElementById('tariff-lpg').value),
        kerosene_per_liter: parseFloat(document.getElementById('tariff-kero').value),
        effective_date: document.getElementById('tariff-effective-date').value
      };
      try {
        const res = await apiFetch('/api/v1/settings/tariffs', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          showToast('Tariffs updated!');
          closeModal('modal-tariff');
          loadDashboard();
          loadFuelParity();
        } else {
          showToast('Failed to update tariffs', 'error');
        }
      } catch (err) {
        showToast('Network error updating tariffs', 'error');
      } finally {
        setButtonLoading(submitTariffBtn, false);
      }
    });
  }
}

// Auth form handlers
function setupAuthForms() {
  const authAlert = document.getElementById('auth-alert');
  function showAuthAlert(msg) {
    if (!authAlert) return;
    authAlert.textContent = msg;
    authAlert.classList.remove('d-none');
  }
  function hideAuthAlert() {
    if (authAlert) authAlert.classList.add('d-none');
  }

  const formLogin = document.getElementById('form-login');
  const submitLoginBtn = document.getElementById('btn-submit-login');
  if (formLogin) {
    formLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAuthAlert();
      setButtonLoading(submitLoginBtn, true);
      const username = document.getElementById('login-username').value.trim();
      const password = document.getElementById('login-password').value;
      try {
        const res = await fetch('/api/v1/auth/login', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        const body = await res.json();
        if (res.ok) {
          updateAuthUI(body.user);
          bootstrap.Modal.getInstance(document.getElementById('modal-auth'))?.hide();
          showToast(`Welcome back, ${body.user.username}!`);
          await loadDashboard();
          await loadFuelParity();
          await loadAppliances();
          await loadEnergyReport();
        } else {
          showAuthAlert(body.message || 'Login failed. Check credentials.');
        }
      } catch (_) {
        showAuthAlert('Network error. Please try again.');
      } finally {
        setButtonLoading(submitLoginBtn, false);
      }
    });
  }

  const formRegister = document.getElementById('form-register');
  const submitRegisterBtn = document.getElementById('btn-submit-register');
  if (formRegister) {
    formRegister.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAuthAlert();
      setButtonLoading(submitRegisterBtn, true);
      const payload = {
        household_name: document.getElementById('register-household').value.trim(),
        username: document.getElementById('register-username').value.trim(),
        email: document.getElementById('register-email').value.trim() || null,
        password: document.getElementById('register-password').value
      };
      try {
        const res = await fetch('/api/v1/auth/register', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const body = await res.json();
        if (res.ok) {
          showToast('Account created! Please sign in.');
          // Auto-switch to login tab
          bootstrap.Tab.getOrCreateInstance(document.getElementById('tab-login')).show();
          const u = document.getElementById('login-username');
          if (u) u.value = payload.username;
          formRegister.reset();
        } else {
          showAuthAlert(body.message || 'Registration failed.');
        }
      } catch (_) {
        showAuthAlert('Network error. Please try again.');
      } finally {
        setButtonLoading(submitRegisterBtn, false);
      }
    });
  }
}

// Page Load
document.addEventListener('DOMContentLoaded', async () => {
  clearCharts();
  setupReportForm();
  setupApplianceManagement();
  // Restore authenticated session from cookie
  const currentUser = await checkAuthSession();
  if (currentUser) {
    await loadDashboard();
    await loadFuelParity();
    await loadAppliances();
    await loadEnergyReport();
  }
  setupLpgForm();
  setupApplianceForm();
  setupOtherFuelForms();
  setupAuthForms();

  // Set today's date in form date pickers
  const today = new Date().toISOString().slice(0, 10);
  document.querySelectorAll('input[type="date"]').forEach(inp => {
    if (!inp.value) inp.value = today;
  });

  // Auto-close collapsible mobile navbar when clicking navigation links
  const collapseElem = document.getElementById('navbarMainCollapse');
  if (collapseElem) {
    collapseElem.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        if (collapseElem.classList.contains('show') && window.bootstrap) {
          bootstrap.Collapse.getOrCreateInstance(collapseElem).hide();
        }
      });
    });
  }
});
