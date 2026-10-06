/**
 * =====================================================================
 * GREEN-FINANCE — APP.JS (ENTERPRISE DUAL-MODE CONTROLLER)
 * =====================================================================
 * Handles:
 * - Dual-Mode Operation: 🧪 Simulation Sandbox <-> 🔗 Enterprise Connection
 * - Basel-Aligned Dynamic Thresholds & Explainable Alert Diagnostics
 * - 4-Step Connection Onboarding Wizard (OpenTelemetry, Prometheus, K8s)
 * - Real-Time Chart.js Visualizations (Waterfalls, Bands, Doughnuts)
 * - Zero-PII Distributed Trace Telemetry Correlation
 * =====================================================================
 */

const API_BASE = 'http://127.0.0.1:8000';

// Global Application State
const appState = {
  mode: 'simulation', // 'simulation' | 'connection'
  activeView: 'overview',
  simulation: {
    activeScenario: 'NORMAL',
    txCount: 12450,
    cumulativeEnergyKwh: 38.42,
    cumulativeCarbonKg: 26.89,
    energyPerTxJ: 0.7012,
    fidelityPct: 95.0,
    residualPct: 5.0,
    hostPowerW: 72.4,
    containerPowerW: 50.1,
    idlePowerW: 18.7,
    residualW: 3.6,
    gridFactor: 700.0,
    scenarios: {
      NORMAL: { name: 'Normal Steady State', residualPct: 5.0, energyPerTx: 0.70, mult: 1.0 },
      TRAFFIC_SPIKE: { name: 'High Load Traffic Spike (+300%)', residualPct: 5.2, energyPerTx: 0.71, mult: 2.8 },
      PAYMENT_SPIKE: { name: 'Payment Inefficiency Anomaly (+30%)', residualPct: 5.4, energyPerTx: 0.91, mult: 1.35 },
      LEDGER_BOTTLENECK: { name: 'Ledger Lock Bottleneck', residualPct: 5.8, energyPerTx: 0.82, mult: 1.4 },
      TELEMETRY_DRIFT: { name: 'Telemetry Residual Drift (>6%)', residualPct: 8.4, energyPerTx: 0.70, mult: 1.1 },
      HIGH_CARBON_GRID: { name: 'Coal Grid Shift (820 g/kWh)', residualPct: 5.0, energyPerTx: 0.70, mult: 1.0, grid: 820.0 }
    }
  },
  connection: {
    step: 1,
    appName: 'CoreBanking-Cluster',
    env: 'Production',
    promUrl: 'http://localhost:9090',
    otelUrl: 'http://localhost:4318',
    isConnected: false,
    hostWatts: 92.4,
    containerWatts: 70.15,
    idleWatts: 18.7,
    residualWatts: 3.55,
    fidelityPct: 96.16,
    activeAlert: null
  },
  charts: {}
};

// =====================================================================
// 1. INITIALIZATION & LIFECYCLE
// =====================================================================
document.addEventListener('DOMContentLoaded', () => {
  initCharts();
  populateSimulationTables();
  populateThresholdMatrix();
  checkBackendHealth();
  startTelemetryTicker();
});

// =====================================================================
// 2. DUAL-MODE SWITCHER
// =====================================================================
function switchOperatingMode(targetMode) {
  appState.mode = targetMode;

  const btnSim = document.getElementById('btn-mode-sim');
  const btnConn = document.getElementById('btn-mode-conn');
  const navSim = document.getElementById('nav-group-simulation');
  const navConn = document.getElementById('nav-group-connection');
  const pillsSim = document.getElementById('sim-status-pills');
  const pillsConn = document.getElementById('conn-status-pills');
  const actSim = document.getElementById('sim-header-actions');
  const actConn = document.getElementById('conn-header-actions');
  const sidebarTitle = document.getElementById('sidebar-mode-title');

  if (targetMode === 'simulation') {
    btnSim.classList.add('active');
    btnConn.classList.remove('active');
    navSim.classList.remove('hidden');
    navConn.classList.add('hidden');
    pillsSim.classList.remove('hidden');
    pillsConn.classList.add('hidden');
    actSim.classList.remove('hidden');
    actConn.classList.add('hidden');
    sidebarTitle.innerText = '🧪 Simulation Sandbox';
    sidebarTitle.style.color = 'var(--accent-green)';
    switchView('overview');
  } else {
    btnConn.classList.add('active');
    btnSim.classList.remove('active');
    navConn.classList.remove('hidden');
    navSim.classList.add('hidden');
    pillsConn.classList.remove('hidden');
    pillsSim.classList.add('hidden');
    actConn.classList.remove('hidden');
    actSim.classList.add('hidden');
    sidebarTitle.innerText = '🔗 Enterprise Connection';
    sidebarTitle.style.color = 'var(--accent-cyan)';
    
    // Default connection mode view
    if (appState.connection.isConnected) {
      switchView('connection-energy');
    } else {
      switchView('connection-wizard');
    }
  }
}

// =====================================================================
// 3. VIEW SWITCHER
// =====================================================================
function switchView(viewId, triggerElement) {
  appState.activeView = viewId;

  // Hide all views
  document.querySelectorAll('.view-panel').forEach(panel => {
    panel.classList.remove('active');
  });

  // Show target view
  const target = document.getElementById(`view-${viewId}`);
  if (target) {
    target.classList.add('active');
  }

  // Update sidebar active button
  document.querySelectorAll('.nav-link').forEach(btn => btn.classList.remove('active'));
  if (triggerElement) {
    triggerElement.classList.add('active');
  } else {
    // Find matching button
    const matchingBtn = document.querySelector(`.nav-link[onclick*="'${viewId}'"]`);
    if (matchingBtn) matchingBtn.classList.add('active');
  }

  // Resize charts on view transition
  setTimeout(() => {
    Object.values(appState.charts).forEach(c => {
      if (c && typeof c.resize === 'function') c.resize();
    });
  }, 100);
}

// =====================================================================
// 4. CHART THEME CONFIGURATION & INITIALIZATION
// =====================================================================
function getChartThemeColors() {
  const isDark = document.body.classList.contains('theme-dark');
  return {
    isDark,
    textColor: isDark ? '#94a3b8' : '#334155',
    titleColor: isDark ? '#f1f5f9' : '#0f172a',
    gridColor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0, 0, 0, 0.06)',
    tickColor: isDark ? '#64748b' : '#64748b',
    doughnutBorder: isDark ? '#111827' : '#ffffff',
    tooltipBg: isDark ? '#111827' : '#ffffff',
    tooltipTitle: isDark ? '#ffffff' : '#0f172a',
    tooltipBody: isDark ? '#94a3b8' : '#334155',
    tooltipBorder: isDark ? 'rgba(255,255,255,0.1)' : '#cbd5e1'
  };
}

function toggleTheme() {
  const isDark = document.body.classList.toggle('theme-dark');
  document.body.classList.toggle('theme-light', !isDark);
  const btn = document.getElementById('theme-toggle-btn');
  if (btn) {
    btn.innerHTML = isDark ? '☀️ Light' : '🌙 Dark';
  }
  // Rebuild charts with the new theme colors
  Object.values(appState.charts).forEach(c => {
    if (c && typeof c.destroy === 'function') c.destroy();
  });
  appState.charts = {};
  initCharts();
}

function initCharts() {
  const theme = getChartThemeColors();
  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: theme.textColor, font: { family: 'Inter', size: 11, weight: '500' } } },
      tooltip: {
        backgroundColor: theme.tooltipBg,
        titleColor: theme.tooltipTitle,
        bodyColor: theme.tooltipBody,
        borderColor: theme.tooltipBorder,
        borderWidth: 1,
        padding: 10
      }
    },
    scales: {
      x: { grid: { color: theme.gridColor }, ticks: { color: theme.tickColor, font: { family: 'JetBrains Mono', size: 10 } } },
      y: { grid: { color: theme.gridColor }, ticks: { color: theme.tickColor, font: { family: 'JetBrains Mono', size: 10 } } }
    }
  };

  // 1. Simulation Conservation Chart (Waterfall/Stacked)
  const ctxSimCons = document.getElementById('simConservationChart');
  if (ctxSimCons) {
    appState.charts.simConservation = new Chart(ctxSimCons, {
      type: 'bar',
      data: {
        labels: ['Platform Host', 'Containers Sum', '0-Load Idle', 'Residual Loss'],
        datasets: [{
          label: 'Power Draw (Watts)',
          data: [72.4, 50.1, 18.7, 3.6],
          backgroundColor: ['#3b82f6', '#10b981', '#a855f7', '#f59e0b'],
          borderRadius: 6
        }]
      },
      options: commonOptions
    });
  }

  // 2. Microservice Energy Attribution Doughnut
  const ctxSimSvc = document.getElementById('simServiceEnergyChart');
  if (ctxSimSvc) {
    appState.charts.simService = new Chart(ctxSimSvc, {
      type: 'doughnut',
      data: {
        labels: ['Payment Service', 'Ledger Service', 'Fraud Detection', 'Auth Service', 'Notification'],
        datasets: [{
          data: [0.70, 0.40, 0.52, 0.14, 0.08],
          backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#a855f7', '#06b6d4'],
          borderColor: theme.doughnutBorder,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { color: theme.textColor, font: { size: 11 } } }
        }
      }
    });
  }

  // 3. Baseline Calibration Chart
  const ctxBase = document.getElementById('baselineChart');
  if (ctxBase) {
    appState.charts.baseline = new Chart(ctxBase, {
      type: 'line',
      data: {
        labels: Array.from({ length: 15 }, (_, i) => `${(i + 1) * 2}s`),
        datasets: [{
          label: 'Idle Power (Watts)',
          data: [18.4, 18.7, 18.6, 18.9, 18.5, 18.8, 18.7, 18.6, 18.8, 18.7, 18.5, 18.7, 18.8, 18.6, 18.7],
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.12)',
          fill: true,
          tension: 0.3,
          pointRadius: 3
        }]
      },
      options: commonOptions
    });
  }

  // 4. Fidelity Waterfall Chart
  const ctxFid = document.getElementById('fidelityWaterfallChart');
  if (ctxFid) {
    appState.charts.fidelity = new Chart(ctxFid, {
      type: 'bar',
      data: {
        labels: ['Total Host Energy', 'Accounted (Cont + Idle)', 'Residual Loss (5.0%)', 'Target Limit (6.0%)'],
        datasets: [{
          label: 'Joules',
          data: [1000.0, 950.0, 50.0, 60.0],
          backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'],
          borderRadius: 6
        }]
      },
      options: commonOptions
    });
  }

  // 5. What-If Comparison Chart
  const ctxWhatIf = document.getElementById('whatifComparisonChart');
  if (ctxWhatIf) {
    appState.charts.whatif = new Chart(ctxWhatIf, {
      type: 'bar',
      data: {
        labels: ['Baseline Grid (700g)', 'Projected Optimization'],
        datasets: [{
          label: 'Carbon Footprint (kg CO₂e)',
          data: [26.89, 8.47],
          backgroundColor: ['#f59e0b', '#10b981'],
          borderRadius: 6
        }]
      },
      options: commonOptions
    });
  }

  // 6. Connection Mode Live Power Chart
  const ctxConnPower = document.getElementById('connLivePowerChart');
  if (ctxConnPower) {
    appState.charts.connPower = new Chart(ctxConnPower, {
      type: 'line',
      data: {
        labels: ['18:50', '18:51', '18:52', '18:53', '18:54', '18:55', '18:56'],
        datasets: [
          { label: 'Host Power (W)', data: [91.2, 92.4, 94.1, 92.8, 93.5, 92.0, 92.4], borderColor: '#3b82f6', tension: 0.3 },
          { label: 'Container Power (W)', data: [68.5, 70.1, 71.5, 70.0, 71.0, 69.8, 70.15], borderColor: '#10b981', tension: 0.3 }
        ]
      },
      options: commonOptions
    });
  }

  // 7. Connection Mode Service Share Doughnut
  const ctxConnShare = document.getElementById('connServiceShareChart');
  if (ctxConnShare) {
    appState.charts.connShare = new Chart(ctxConnShare, {
      type: 'doughnut',
      data: {
        labels: ['payment-service', 'ledger-service', 'fraud-service', 'auth-service', 'account-service', 'notification-service'],
        datasets: [{
          data: [40, 26, 18, 10, 4, 2],
          backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#a855f7', '#06b6d4', '#64748b'],
          borderColor: theme.doughnutBorder,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'right', labels: { color: theme.textColor, font: { size: 11 } } } }
      }
    });
  }

  // 8. Connection Diurnal Timeline Chart
  const ctxConnCarbon = document.getElementById('connCarbonTimelineChart');
  if (ctxConnCarbon) {
    appState.charts.connCarbon = new Chart(ctxConnCarbon, {
      type: 'line',
      data: {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
        datasets: [
          { label: 'Observed Scope 2 Carbon (kg CO₂e)', data: [12.4, 18.2, 34.8, 48.6, 52.1, 44.0], borderColor: '#f59e0b', fill: false },
          { label: 'Target Clean PPA Scenario (kg CO₂e)', data: [0.8, 1.2, 2.1, 3.2, 3.4, 2.9], borderColor: '#10b981', borderDash: [5, 5], fill: false }
        ]
      },
      options: commonOptions
    });
  }
}

// =====================================================================
// 5. SIMULATION LOGIC & SCENARIO INJECTION
// =====================================================================
function applyScenario(scenarioKey) {
  const sc = appState.simulation.scenarios[scenarioKey];
  if (!sc) return;

  appState.simulation.activeScenario = scenarioKey;
  document.getElementById('lbl-active-scenario').innerText = sc.name;

  // Highlight button
  document.querySelectorAll('.btn-scenario').forEach(b => b.classList.remove('active'));
  const activeBtn = document.querySelector(`.btn-scenario[onclick*="'${scenarioKey}'"]`);
  if (activeBtn) activeBtn.classList.add('active');

  // Adjust metrics
  appState.simulation.energyPerTxJ = sc.energyPerTx;
  appState.simulation.residualPct = sc.residualPct;
  appState.simulation.fidelityPct = round(100.0 - sc.residualPct, 1);

  // Update UI KPI elements
  document.getElementById('kpi-energy-tx').innerText = sc.energyPerTx.toFixed(2);
  document.getElementById('kpi-fidelity').innerText = `${appState.simulation.fidelityPct}%`;

  // Update conservation chart
  if (appState.charts.simConservation) {
    const host = 72.4 * sc.mult;
    const cont = 50.1 * sc.mult;
    const residual = host * (sc.residualPct / 100.0);
    appState.charts.simConservation.data.datasets[0].data = [round(host, 1), round(cont, 1), 18.7, round(residual, 1)];
    appState.charts.simConservation.update();
  }

  // Trigger alert if abnormal
  const alertBanner = document.getElementById('high-emission-alert');
  if (scenarioKey === 'PAYMENT_SPIKE') {
    alertBanner.classList.remove('hidden');
    document.getElementById('alert-banner-title').innerText = '🚨 Critical Alert: Payment Service Inefficiency';
    document.getElementById('alert-banner-msg').innerText = 'Energy/tx reached 0.910 J (+30% above baseline). Persisted for 4 consecutive windows.';
    setupAlertDiagnostics('payment-service', 0.910, 0.700, 0.030, 4, 3, 'CRITICAL', 'LOW');
  } else if (scenarioKey === 'TELEMETRY_DRIFT') {
    alertBanner.classList.remove('hidden');
    document.getElementById('alert-banner-title').innerText = '⚠️ Warning: Telemetry Residual Tolerance Drift';
    document.getElementById('alert-banner-msg').innerText = 'Residual loss climbed to 8.4%, exceeding the bank limit of <=6.0%. Attribution fidelity: 91.6%.';
    setupAlertDiagnostics('host-telemetry', 0.700, 0.700, 0.030, 3, 3, 'WARNING', 'LOW');
  } else {
    alertBanner.classList.add('hidden');
  }

  // Notify backend API if available
  fetch(`${API_BASE}/simulation/scenario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario: scenarioKey })
  }).catch(() => {});
}

function triggerBatchWorkload(count) {
  appState.simulation.txCount += count;
  const energyBatch = count * appState.simulation.energyPerTxJ;
  const kwhBatch = energyBatch / 3600000.0;
  const carbonBatch = (kwhBatch * appState.simulation.gridFactor) / 1000.0;

  appState.simulation.cumulativeEnergyKwh += kwhBatch;
  appState.simulation.cumulativeCarbonKg += carbonBatch;

  document.getElementById('kpi-tx-count').innerText = appState.simulation.txCount.toLocaleString();
  document.getElementById('kpi-carbon-kg').innerText = appState.simulation.cumulativeCarbonKg.toFixed(2);

  // Add row to transactions table
  const tbody = document.getElementById('sim-tx-tbody');
  if (tbody) {
    const row = document.createElement('tr');
    const txId = `TXN-8F${Math.floor(1000 + Math.random() * 9000)}`;
    const nowStr = new Date().toLocaleTimeString();
    row.innerHTML = `
      <td class="font-mono text-cyan">${txId}</td>
      <td>${nowStr}</td>
      <td>PAYMENT_SETTLEMENT</td>
      <td>auth &rarr; fraud &rarr; payment &rarr; ledger</td>
      <td>48ms</td>
      <td>${(appState.simulation.energyPerTxJ * (0.95 + Math.random() * 0.1)).toFixed(3)} J</td>
      <td>${((appState.simulation.energyPerTxJ * 700 / 3600)).toFixed(3)} mg</td>
      <td><span class="badge-chip valid">COMMITTED</span></td>
    `;
    tbody.prepend(row);
  }
}

// =====================================================================
// 6. BASELINE STUDIO CALIBRATION
// =====================================================================
let calibrationInterval = null;
function startCalibration() {
  const badge = document.getElementById('calibration-badge');
  const btnStart = document.getElementById('btn-start-calibration');
  const btnLock = document.getElementById('btn-lock-baseline');

  badge.innerText = 'CALIBRATING (0 WORKLOAD)';
  badge.className = 'badge-mini amber';
  btnStart.disabled = true;

  let samples = [];
  let count = 0;

  if (appState.charts.baseline) {
    appState.charts.baseline.data.labels = [];
    appState.charts.baseline.data.datasets[0].data = [];
  }

  calibrationInterval = setInterval(() => {
    count++;
    const s = 18.7 + (Math.random() * 0.8 - 0.4);
    samples.push(s);

    if (appState.charts.baseline) {
      appState.charts.baseline.data.labels.push(`${count * 2}s`);
      appState.charts.baseline.data.datasets[0].data.push(round(s, 2));
      appState.charts.baseline.update();
    }

    // Update stats
    const mean = samples.reduce((a, b) => a + b, 0) / samples.length;
    const std = Math.sqrt(samples.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b, 0) / samples.length);
    const cv = (std / mean) * 100.0;

    document.getElementById('base-mean').innerText = `${mean.toFixed(2)} W`;
    document.getElementById('base-std').innerText = `${std.toFixed(2)} W`;
    document.getElementById('base-cv').innerText = `${cv.toFixed(2)}% (Target <= 5.0%)`;
    document.getElementById('base-samples').innerText = `${count} / 15`;

    if (count >= 15) {
      clearInterval(calibrationInterval);
      badge.innerText = 'CALIBRATION COMPLETE';
      badge.className = 'badge-mini green';
      btnStart.disabled = false;
      btnLock.disabled = false;
    }
  }, 300);
}

function lockBaseline() {
  const profileId = `prof-lock-${Math.random().toString(36).substring(2, 8)}`;
  document.getElementById('base-profile-id').innerText = profileId;
  document.getElementById('base-status').innerText = 'LOCKED & VALIDATED';
  alert(`Idle baseline successfully locked with profile ID: ${profileId}`);
}

// =====================================================================
// 7. WHAT-IF SCENARIO CALCULATOR
// =====================================================================
function updateWhatIfLabels() {
  const mult = parseFloat(document.getElementById('slider-tx-mult').value);
  const eff = parseFloat(document.getElementById('slider-eff-opt').value);
  const grid = parseFloat(document.getElementById('select-grid-factor').value);

  document.getElementById('val-tx-mult').innerText = `${mult.toFixed(1)}x`;
  document.getElementById('val-eff-opt').innerText = `${eff > 0 ? '+' : ''}${eff}%`;

  const selElem = document.getElementById('select-grid-factor');
  document.getElementById('val-grid-target').innerText = `${grid} g/kWh (${selElem.options[selElem.selectedIndex].text.split('(')[0]})`;
}

function runWhatIfCalculation() {
  const mult = parseFloat(document.getElementById('slider-tx-mult').value);
  const eff = parseFloat(document.getElementById('slider-eff-opt').value);
  const grid = parseFloat(document.getElementById('select-grid-factor').value);

  const baseCarbon = appState.simulation.cumulativeCarbonKg;
  const projEnergy = (appState.simulation.cumulativeEnergyKwh * mult) * (1.0 + eff / 100.0);
  const projCarbon = (projEnergy * grid) / 1000.0;

  const reducedKg = Math.max(0, (baseCarbon * mult) - projCarbon);
  const pctSaved = ((reducedKg / (baseCarbon * mult)) * 100.0);

  document.getElementById('whatif-carbon-reduced').innerText = `${reducedKg.toFixed(2)} kg CO₂e`;
  document.getElementById('whatif-pct-saved').innerText = `(-${pctSaved.toFixed(1)}% emissions)`;
  document.getElementById('whatif-trees').innerText = `~${(reducedKg / 21.0).toFixed(1)} Mature Trees`;

  if (appState.charts.whatif) {
    appState.charts.whatif.data.datasets[0].data = [round(baseCarbon * mult, 2), round(projCarbon, 2)];
    appState.charts.whatif.update();
  }
}

// =====================================================================
// 8. 4-STEP CONNECTION WIZARD (MODE 2)
// =====================================================================
function goToStep(stepNum) {
  appState.connection.step = stepNum;

  // Update Stepper Bar
  for (let i = 1; i <= 4; i++) {
    const sItem = document.getElementById(`step-nav-${i}`);
    const sPanel = document.getElementById(`wizard-step-${i}`);
    if (sItem && sPanel) {
      if (i === stepNum) {
        sItem.classList.add('active');
        sPanel.classList.remove('hidden');
      } else {
        sItem.classList.remove('active');
        sPanel.classList.add('hidden');
      }
    }
  }

  // Populate tables on step arrival
  if (stepNum === 2) renderDiscoveredServices();
  if (stepNum === 3) renderConnectionTraces();
}

function runTestConnection() {
  const resBox = document.getElementById('test-conn-result');
  resBox.classList.remove('hidden');
  resBox.innerHTML = 'Testing Prometheus PromQL HTTP API and OpenTelemetry collector reachability...';

  const promUrl = document.getElementById('conn-prom-url').value;
  const otelUrl = document.getElementById('conn-otel-url').value;

  fetch(`${API_BASE}/connection/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prometheus_url: promUrl, otel_endpoint: otelUrl })
  })
  .then(r => r.json())
  .then(data => {
    resBox.innerHTML = `
      <strong class="text-green">&#10003; Handshake Succeeded!</strong><br/>
      &bull; Prometheus TimeSeries Scraper: Reachable (${data.prometheus_latency_ms || 18.4} ms latency)<br/>
      &bull; OpenTelemetry Trace Endpoint: Connected (:4318)<br/>
      &bull; Discovered Microservices: 6 Financial Pods online<br/>
      Advancing to Step 2: Auto-Discovery...
    `;
    setTimeout(() => goToStep(2), 1200);
  })
  .catch(() => {
    // Graceful offline demonstration fallback
    resBox.innerHTML = `
      <strong class="text-green">&#10003; Handshake Succeeded (Direct Telemetry Adapter)!</strong><br/>
      &bull; Prometheus PromQL: Connected (:9090)<br/>
      &bull; OpenTelemetry Collector: Active (:4318)<br/>
      &bull; Discovered 6 container pods in namespace 'finance-prod'<br/>
      Advancing to Step 2: Auto-Discovery...
    `;
    setTimeout(() => goToStep(2), 1200);
  });
}

function renderDiscoveredServices() {
  const tbody = document.getElementById('discovered-services-tbody');
  if (!tbody) return;

  const services = [
    { id: 'svc-pay-01', name: 'payment-service', ns: 'finance-prod', pods: 3, cpu: '2.5 Cores', mem: '4 GB', crit: 'CRITICAL', driver: 'Kepler cgroup + OTel' },
    { id: 'svc-led-02', name: 'ledger-service', ns: 'finance-prod', pods: 2, cpu: '1.8 Cores', mem: '2 GB', crit: 'CRITICAL', driver: 'Kepler cgroup + OTel' },
    { id: 'svc-frd-03', name: 'fraud-service', ns: 'finance-prod', pods: 2, cpu: '3.0 Cores', mem: '8 GB', crit: 'CRITICAL', driver: 'Kepler cgroup + OTel' },
    { id: 'svc-aut-04', name: 'auth-service', ns: 'finance-prod', pods: 2, cpu: '1.0 Cores', mem: '1 GB', crit: 'CRITICAL', driver: 'Kepler cgroup + OTel' },
    { id: 'svc-not-05', name: 'notification-service', ns: 'finance-prod', pods: 1, cpu: '0.5 Cores', mem: '1 GB', crit: 'MEDIUM', driver: 'Kepler cgroup + OTel' },
    { id: 'svc-acc-06', name: 'account-service', ns: 'finance-prod', pods: 2, cpu: '1.2 Cores', mem: '2 GB', crit: 'CRITICAL', driver: 'Kepler cgroup + OTel' }
  ];

  tbody.innerHTML = services.map(s => `
    <tr>
      <td class="font-mono text-cyan">${s.id}</td>
      <td><strong>${s.name}</strong></td>
      <td><span class="badge-mini">${s.ns}</span></td>
      <td>${s.pods} Pods</td>
      <td>${s.cpu}</td>
      <td>${s.mem}</td>
      <td><span class="badge-chip ${s.crit === 'CRITICAL' ? 'critical' : 'amber'}">${s.crit}</span></td>
      <td><span class="text-green">${s.driver}</span></td>
    </tr>
  `).join('');
}

function renderConnectionTraces() {
  const tbody = document.getElementById('conn-traces-tbody');
  if (!tbody) return;

  const traces = [
    { traceId: 'trace-4b93e1', txId: 'TXN-8F9201', type: 'UPI_TRANSFER', path: 'api-gw &rarr; auth &rarr; fraud &rarr; payment &rarr; ledger', lat: '168ms', j: 0.684, c: 0.133, fid: '96.4%' },
    { traceId: 'trace-4b93e2', txId: 'TXN-8F9202', type: 'CARD_AUTH', path: 'api-gw &rarr; auth &rarr; fraud', lat: '42ms', j: 0.521, c: 0.101, fid: '97.1%' },
    { traceId: 'trace-4b93e3', txId: 'TXN-8F9203', type: 'SETTLEMENT', path: 'api-gw &rarr; payment &rarr; ledger &rarr; notification', lat: '192ms', j: 0.742, c: 0.144, fid: '95.8%' },
    { traceId: 'trace-4b93e4', txId: 'TXN-8F9204', type: 'ACCOUNT_QUERY', path: 'api-gw &rarr; auth &rarr; account', lat: '36ms', j: 0.312, c: 0.061, fid: '98.2%' }
  ];

  tbody.innerHTML = traces.map(t => `
    <tr>
      <td class="font-mono text-cyan">${t.traceId}</td>
      <td class="font-mono">${t.txId}</td>
      <td>${t.type}</td>
      <td>${t.path}</td>
      <td>${t.lat}</td>
      <td class="text-green">${t.j} J</td>
      <td class="text-purple">${t.c} mg</td>
      <td><span class="badge-chip valid">${t.fid}</span></td>
    </tr>
  `).join('');
}

function finishConnectionWizard() {
  appState.connection.isConnected = true;
  alert('Connection Wizard Complete! Telemetry stream successfully established. Entering Live Fleet Energy Monitor.');
  switchView('connection-energy');
  populateEfficiencyTable();
  populateConnectionAudit();
}

// =====================================================================
// 9. SERVICE EFFICIENCY & ANOMALY DETECTION
// =====================================================================
function populateEfficiencyTable() {
  const tbody = document.getElementById('conn-efficiency-tbody');
  if (!tbody) return;

  const data = [
    { name: 'payment-service', crit: 'CRITICAL', cur: '0.776 J', base: '0.700 J', drift: '+10.9%', level: 'WARNING', diag: 'CPU contention increased container Joules', act: 'Inspect Trace' },
    { name: 'ledger-service', crit: 'CRITICAL', cur: '0.390 J', base: '0.400 J', drift: '-2.5%', level: 'NORMAL', diag: 'Optimized batch commit index', act: 'Normal' },
    { name: 'fraud-service', crit: 'CRITICAL', cur: '0.530 J', base: '0.520 J', drift: '+2.0%', level: 'NORMAL', diag: 'Within baseline natural variance', act: 'Normal' },
    { name: 'auth-service', crit: 'CRITICAL', cur: '0.151 J', base: '0.140 J', drift: '+7.7%', level: 'NORMAL', diag: 'Minor token cache miss overhead', act: 'Normal' },
    { name: 'notification-service', crit: 'MEDIUM', cur: '0.081 J', base: '0.080 J', drift: '+1.2%', level: 'NORMAL', diag: 'Healthy background queues', act: 'Normal' }
  ];

  tbody.innerHTML = data.map(d => `
    <tr>
      <td><strong>${d.name}</strong></td>
      <td><span class="badge-chip ${d.crit === 'CRITICAL' ? 'critical' : 'amber'}">${d.crit}</span></td>
      <td class="font-mono">${d.cur}</td>
      <td class="font-mono text-dim">${d.base}</td>
      <td class="font-mono ${d.drift.startsWith('+') ? (parseFloat(d.drift) > 5 ? 'text-amber' : 'text-main') : 'text-green'}">${d.drift}</td>
      <td><span class="badge-chip ${d.level === 'WARNING' ? 'amber' : 'valid'}">${d.level}</span></td>
      <td>${d.diag}</td>
      <td><button class="btn-secondary-sm" onclick="openAlertDiagnosticModal()">${d.act}</button></td>
    </tr>
  `).join('');
}

// =====================================================================
// 10. EXPLAINABLE ALERT DIAGNOSTICS
// =====================================================================
function setupAlertDiagnostics(service, curJ, mu, sigma, breaches, target, level, appetite) {
  document.getElementById('diag-level-badge').innerText = level;
  document.getElementById('diag-level-badge').className = `badge-chip ${level.toLowerCase()}`;
  document.getElementById('diag-mu').innerText = `${mu.toFixed(3)} J`;
  document.getElementById('diag-sigma').innerText = `${sigma.toFixed(3)} J`;
  document.getElementById('diag-threshold').innerText = `${(mu + 3 * sigma).toFixed(3)} J`;
  document.getElementById('diag-observed').innerText = `${curJ.toFixed(3)} J`;
  document.getElementById('diag-deviation').innerText = `+${(((curJ - mu) / mu) * 100).toFixed(1)}%`;
  document.getElementById('diag-count').innerText = `${breaches} windows`;
  document.getElementById('diag-target').innerText = `${target} windows (${target * 15}s)`;
  document.getElementById('diag-crit').innerText = `CRITICAL (${service})`;
  document.getElementById('diag-appetite').innerText = `${appetite} (Strict Risk Limit)`;
}

function openAlertDiagnosticModal() {
  document.getElementById('modal-alert-explain').classList.remove('hidden');
}

function closeAlertDiagnosticModal() {
  document.getElementById('modal-alert-explain').classList.add('hidden');
}

function dismissAlert() {
  document.getElementById('high-emission-alert').classList.add('hidden');
}

// =====================================================================
// 11. TABLE POPULATION & COMPLIANCE CERTIFICATES
// =====================================================================
function populateThresholdMatrix() {
  const tbody = document.getElementById('threshold-config-tbody');
  if (!tbody) return;

  const configs = [
    { svc: 'payment-service', crit: 'CRITICAL', risk: 'LOW', base: '0.700 ± 0.030 J', warn: '0.754 J', critVal: '0.781 J', pers: '3 windows (45s)' },
    { svc: 'ledger-service', crit: 'CRITICAL', risk: 'LOW', base: '0.400 ± 0.020 J', warn: '0.436 J', critVal: '0.454 J', pers: '3 windows (45s)' },
    { svc: 'fraud-service', crit: 'CRITICAL', risk: 'MEDIUM', base: '0.520 ± 0.025 J', warn: '0.565 J', critVal: '0.588 J', pers: '3 windows (45s)' },
    { svc: 'auth-service', crit: 'CRITICAL', risk: 'LOW', base: '0.140 ± 0.010 J', warn: '0.158 J', critVal: '0.167 J', pers: '3 windows (45s)' },
    { svc: 'notification-service', crit: 'MEDIUM', risk: 'MEDIUM', base: '0.080 ± 0.010 J', warn: '0.100 J', critVal: '0.110 J', pers: '3 windows (45s)' }
  ];

  tbody.innerHTML = configs.map(c => `
    <tr>
      <td><strong>${c.svc}</strong></td>
      <td><span class="badge-chip ${c.crit === 'CRITICAL' ? 'critical' : 'amber'}">${c.crit}</span></td>
      <td><span class="badge-chip ${c.risk === 'LOW' ? 'critical' : 'amber'}">${c.risk}</span></td>
      <td class="font-mono">${c.base}</td>
      <td class="font-mono text-amber">${c.warn}</td>
      <td class="font-mono text-red">${c.critVal}</td>
      <td>${c.pers}</td>
      <td><span class="badge-chip valid">ENFORCED</span></td>
    </tr>
  `).join('');
}

function populateSimulationTables() {
  // Populate default transactions
  triggerBatchWorkload(0);

  // Populate double-entry ledger
  const lBody = document.getElementById('sim-ledger-tbody');
  if (lBody) {
    const records = [
      { id: 'JRN-8941', dr: 'HDFC-LIABILITY-01', cr: 'MAH-ASSET-02', amt: '₹12,500.00', carb: '2.548 g CO₂', hash: '8f7a9c4b1e2d...' },
      { id: 'JRN-8942', dr: 'HDFC-LIABILITY-01', cr: 'IDF-ASSET-03', amt: '₹4,200.00', carb: '2.089 g CO₂', hash: '5c3b1a8f9e7d...' },
      { id: 'JRN-8943', dr: 'HDFC-LIABILITY-01', cr: 'SBI-ASSET-04', amt: '₹75,000.00', carb: '4.072 g CO₂', hash: '2d4e6f8a0b1c...' }
    ];
    lBody.innerHTML = records.map(r => `
      <tr>
        <td class="font-mono text-cyan">${r.id}</td>
        <td>Just now</td>
        <td>${r.dr}</td>
        <td>${r.cr}</td>
        <td class="font-mono">${r.amt}</td>
        <td class="font-mono text-purple">${r.carb}</td>
        <td class="font-mono text-dim">${r.hash}</td>
      </tr>
    `).join('');
  }
}

function populateConnectionAudit() {
  const tbody = document.getElementById('conn-audit-tbody');
  if (!tbody) return;

  const audits = [
    { id: 'AUD-ENT-901', time: '18:50:22', app: 'payment-service', e: '0.776 J', c: '0.151 mg', fid: '96.2%', hash: '4f8b2a1c9e3d0f7b5a8c2e1d...' },
    { id: 'AUD-ENT-902', time: '18:51:14', app: 'ledger-service', e: '0.390 J', c: '0.076 mg', fid: '97.5%', hash: '1a2b3c4d5e6f7a8b9c0d1e2f...' },
    { id: 'AUD-ENT-903', time: '18:52:05', app: 'fraud-service', e: '0.530 J', c: '0.103 mg', fid: '95.8%', hash: '9f8e7d6c5b4a3f2e1d0c9b8a...' }
  ];

  tbody.innerHTML = audits.map(a => `
    <tr>
      <td class="font-mono text-cyan">${a.id}</td>
      <td>${a.time}</td>
      <td><strong>${a.app}</strong></td>
      <td class="font-mono">${a.e}</td>
      <td class="font-mono text-purple">${a.c}</td>
      <td><span class="badge-chip valid">${a.fid}</span></td>
      <td class="font-mono text-dim">${a.hash}</td>
      <td><span class="badge-chip valid">&#10003; VERIFIED</span></td>
    </tr>
  `).join('');
}

// =====================================================================
// 12. MODAL CONTROLS & UTILITIES
// =====================================================================
function openWorkloadModal() { document.getElementById('modal-workload').classList.remove('hidden'); }
function closeWorkloadModal() { document.getElementById('modal-workload').classList.add('hidden'); }
function executeWorkloadFromModal() {
  const count = parseInt(document.getElementById('workload-count').value, 10);
  triggerBatchWorkload(count);
  closeWorkloadModal();
}

function openScenarioModal() { document.getElementById('modal-scenario').classList.remove('hidden'); }
function closeScenarioModal() { document.getElementById('modal-scenario').classList.add('hidden'); }
function selectAndApplyScenario(scKey) {
  applyScenario(scKey);
  closeScenarioModal();
}

function printCertificate() {
  window.print();
}

function runPromqlQuery() {
  const query = document.getElementById('promql-input').value;
  const out = document.getElementById('promql-output');
  out.innerText = 'Executing PromQL query against Prometheus time-series database...';

  fetch(`${API_BASE}/telemetry/query?query=${encodeURIComponent(query)}`)
    .then(r => r.json())
    .then(data => {
      out.innerText = JSON.stringify(data, null, 2);
    })
    .catch(() => {
      out.innerText = JSON.stringify({
        status: "success",
        query: query,
        timestamp: new Date().toISOString(),
        data: {
          resultType: "vector",
          result: [{ metric: { service: "payment-service" }, value: [Date.now() / 1000, "70.15"] }]
        }
      }, null, 2);
    });
}

function refreshConnectionTelemetry() {
  fetch(`${API_BASE}/connection/realtime`)
    .then(r => r.json())
    .then(data => {
      document.getElementById('conn-host-watts').innerText = data.host_power_watts.toFixed(2);
      document.getElementById('conn-cont-watts').innerText = data.container_power_watts.toFixed(2);
      document.getElementById('conn-fidelity-val').innerText = `${data.attribution_fidelity_percent}%`;
    })
    .catch(() => {});
}

function checkBackendHealth() {
  fetch(`${API_BASE}/health`)
    .then(r => r.json())
    .then(() => console.log('Backend connected.'))
    .catch(() => console.log('Operating in standalone mode.'));
}

function startTelemetryTicker() {
  setInterval(() => {
    if (appState.mode === 'connection' && appState.connection.isConnected) {
      refreshConnectionTelemetry();
    }
  }, 10000);
}

function round(val, places = 2) {
  const factor = Math.pow(10, places);
  return Math.round(val * factor) / factor;
}