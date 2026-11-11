// State variables
let currentTab = 'advisor';
let systemOverviewData = null;
let junkData = null;
let installedAppsData = [];
let currentRenderedApps = [];
let commonPaths = {};
let pendingModalAction = null;
let sidebarCollapsed = false;
let isAdminMode = false;
let adminStatusChecked = false;
let heavyScannedOnce = false;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    initSidebarState();
    try {
        await loadCommonPaths();
    } catch (e) {
        console.warn("Aviso al cargar rutas:", e);
    }
    try {
        loadAdvisor();
        loadOverview();
    } catch (e) {
        console.warn("Aviso al iniciar modulos:", e);
    }
    // Auto-refresh metrics every 20 seconds
    setInterval(updateQuickMetrics, 20000);

    // Ocultar y remover suavemente el Splash Loader (Capa 4: Cero Pantallas Blancas)
    const splash = document.getElementById('nosclean-splash-loader');
    if (splash) {
        splash.style.opacity = '0';
        splash.style.pointerEvents = 'none';
        setTimeout(() => {
            if (splash.parentNode) splash.parentNode.removeChild(splash);
            checkWelcomeModal();
        }, 300);
    } else {
        checkWelcomeModal();
    }
}

// ======================== SIDEBAR TOGGLE & PERSISTENCE ========================
function initSidebarState() {
    const saved = localStorage.getItem('sidebar_collapsed');
    if (saved !== null) {
        sidebarCollapsed = (saved === 'true');
    } else {
        // Si la pantalla es mediana o pequeña (< 1150px), arranca plegado para ganar espacio
        sidebarCollapsed = (window.innerWidth < 1150);
    }
    applySidebarState();
}

function toggleSidebar() {
    sidebarCollapsed = !sidebarCollapsed;
    localStorage.setItem('sidebar_collapsed', sidebarCollapsed);
    applySidebarState();
}

function applySidebarState() {
    const sidebar = document.getElementById('main-sidebar');
    const toggleIcon = document.getElementById('sidebar-toggle-icon');
    const toggleBtn = document.getElementById('sidebar-toggle-btn');
    const mainContent = document.getElementById('main-content-scroll');
    const body = document.body;

    if (!sidebar) return;

    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
        sidebar.classList.remove('manual-expanded');
        body.classList.add('sidebar-is-collapsed');
        if (mainContent) {
            mainContent.style.marginLeft = '68px';
            mainContent.style.width = 'calc(100vw - 68px)';
        }
        if (toggleIcon) toggleIcon.setAttribute('data-lucide', 'chevron-right');
        if (toggleBtn) toggleBtn.title = "Expandir menú lateral";
    } else {
        sidebar.classList.remove('collapsed');
        sidebar.classList.add('manual-expanded');
        body.classList.remove('sidebar-is-collapsed');
        if (mainContent) {
            mainContent.style.marginLeft = '250px';
            mainContent.style.width = 'calc(100vw - 250px)';
        }
        if (toggleIcon) toggleIcon.setAttribute('data-lucide', 'chevron-left');
        if (toggleBtn) toggleBtn.title = "Plegar menú lateral";
    }
    lucide.createIcons();
}

window.addEventListener('resize', () => {
    if (window.innerWidth < 1150 && !localStorage.getItem('sidebar_collapsed')) {
        sidebarCollapsed = true;
        applySidebarState();
    }
});

// ======================== TABS & NAVIGATION ========================
function switchTab(tabId) {
    currentTab = tabId;
    
    // Hide all tabs
    ['advisor', 'overview', 'cleaner', 'heavy', 'apps', 'organizer', 'startup', 'guide', 'about'].forEach(id => {
        const sec = document.getElementById(`tab-${id}`);
        const btn = document.getElementById(`tab-btn-${id}`);
        if (sec) sec.classList.add('hidden');
        if (btn) {
            if (id === 'guide') {
                btn.className = "nav-tab flex items-center space-x-3 w-full px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all bg-amber-500/15 hover:bg-amber-500/25 text-amber-200 border border-amber-500/35 cursor-pointer";
            } else {
                btn.className = "nav-tab flex items-center space-x-3 w-full px-3 py-2 rounded-xl text-xs sm:text-sm font-medium transition-all text-slate-300 hover:text-white hover:bg-[#087A45]/30 border border-transparent";
            }
        }
    });

    // Show active tab
    const activeSec = document.getElementById(`tab-${tabId}`);
    const activeBtn = document.getElementById(`tab-btn-${tabId}`);
    if (activeSec) activeSec.classList.remove('hidden');
    if (activeBtn) {
        if (tabId === 'guide') {
            activeBtn.className = "nav-tab active flex items-center space-x-3 w-full px-3 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all text-white bg-amber-600 border border-amber-400 shadow-md shadow-amber-950/40";
        } else {
            activeBtn.className = "nav-tab active flex items-center space-x-3 w-full px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all text-white bg-[#087A45] border border-[#16B84E]/50 shadow-md";
        }
    }

    // Lazy load tab contents if first time
    if (tabId === 'advisor') {
        loadAdvisor();
    } else if (tabId === 'cleaner' && !junkData) {
        scanJunk();
    } else if (tabId === 'heavy' && !heavyScannedOnce) {
        scanHeavyFiles(false);
    } else if (tabId === 'apps' && installedAppsData.length === 0) {
        loadInstalledApps();
    } else if (tabId === 'organizer') {
        scanOrganizer();
    } else if (tabId === 'startup') {
        loadStartupAndProcs();
    }

    lucide.createIcons();
}

function switchGuideTab(subTab) {
    const secManual = document.getElementById('guide-section-manual');
    const secLegal = document.getElementById('guide-section-legal');
    const btnManual = document.getElementById('btn-guide-manual');
    const btnLegal = document.getElementById('btn-guide-legal');

    if (subTab === 'manual') {
        if (secManual) secManual.classList.remove('hidden');
        if (secLegal) secLegal.classList.add('hidden');
        if (btnManual) {
            btnManual.className = "px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all bg-white text-[#087A45] shadow-sm border border-slate-200 cursor-pointer";
        }
        if (btnLegal) {
            btnLegal.className = "px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all text-[#64748B] hover:text-[#102D25] cursor-pointer";
        }
    } else {
        if (secManual) secManual.classList.add('hidden');
        if (secLegal) secLegal.classList.remove('hidden');
        if (btnManual) {
            btnManual.className = "px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all text-[#64748B] hover:text-[#102D25] cursor-pointer";
        }
        if (btnLegal) {
            btnLegal.className = "px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all bg-white text-[#087A45] shadow-sm border border-slate-200 cursor-pointer";
        }
    }
    lucide.createIcons();
}

function refreshCurrentTab() {
    const icon = document.getElementById('refresh-icon');
    if (icon) {
        icon.style.transition = 'transform 0.6s ease';
        icon.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            const el = document.getElementById('refresh-icon');
            if (el) {
                el.style.transition = 'none';
                el.style.transform = '';
            }
        }, 600);
    }

    if (currentTab === 'advisor') loadAdvisor();
    else if (currentTab === 'overview') loadOverview();
    else if (currentTab === 'cleaner') scanJunk(true);
    else if (currentTab === 'heavy') scanHeavyFiles();
    else if (currentTab === 'apps') loadInstalledApps();
    else if (currentTab === 'organizer') scanOrganizer();
    else if (currentTab === 'startup') loadStartupAndProcs();
}

// ======================== API HELPERS ========================
async function apiGet(endpoint) {
    try {
        const res = await fetch(endpoint);
        if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
        return await res.json();
    } catch (err) {
        console.warn('API error:', err);
        return null;
    }
}

async function apiPost(endpoint, data = {}) {
    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.detail || 'Error en la operación');
        return json;
    } catch (err) {
        showToast(err.message, 'error');
        return null;
    }
}

async function loadCommonPaths() {
    const data = await apiGet('/api/storage/common-paths');
    if (data) {
        commonPaths = data;
        const heavyInput = document.getElementById('heavy-path-input');
        if (heavyInput) heavyInput.value = data.downloads || data.user_profile || '';
    }
}

// ======================== TAB: ADVISOR (CONSEJOS) ========================
async function loadAdvisor() {
    const scoreEl = document.getElementById('advisor-score');
    const statusEl = document.getElementById('advisor-status');
    const grid = document.getElementById('advisor-recommendations-grid');

    if (scoreEl) scoreEl.textContent = "...";
    if (statusEl) statusEl.textContent = "Analizando estado de tu PC...";
    
    grid.innerHTML = `
        <div class="col-span-2 text-center py-12 text-slate-400">
            <i data-lucide="loader-2" class="w-6 h-6 text-amber-400 animate-spin mx-auto mb-2"></i>
            <span>Evaluando almacenamiento, arranque y programas...</span>
        </div>
    `;
    lucide.createIcons();

    const data = await apiGet('/api/advisor/recommendations');
    if (!data) {
        grid.innerHTML = `<div class="col-span-2 text-center py-8 text-rose-400">Error al recopilar el diagnóstico. Revisa que el servidor esté activo.</div>`;
        return;
    }

    if (data.is_admin !== undefined) {
        updateAdminBadgeUI(Boolean(data.is_admin));
    }

    if (scoreEl) scoreEl.textContent = data.health_score;
    if (statusEl) statusEl.textContent = `Estado: ${data.health_status}`;

    if (!data.recommendations || data.recommendations.length === 0) {
        grid.innerHTML = `
            <div class="col-span-2 glass-card rounded-2xl p-6 text-center text-[#087A45] border border-slate-200 bg-white shadow-sm">
                <i data-lucide="check-circle" class="w-10 h-10 mx-auto mb-2 text-[#16B84E]"></i>
                <h4 class="text-base font-bold text-[#102D25]">¡Tu equipo está en óptimas condiciones!</h4>
                <p class="text-xs text-[#64748B] mt-1">No se detectaron problemas críticos de almacenamiento ni saturación de inicio.</p>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    grid.innerHTML = '';
    data.recommendations.forEach(rec => {
        const card = document.createElement('div');
        const badgeColors = {
            rose: 'bg-rose-50 text-rose-700 border-rose-200',
            amber: 'bg-amber-50 text-amber-700 border-amber-200',
            emerald: 'bg-[#16B84E]/15 text-[#087A45] border-[#16B84E]/30'
        };

        const btnColors = {
            rose: 'bg-rose-600 hover:bg-rose-500 text-white shadow-sm',
            amber: 'bg-amber-600 hover:bg-amber-500 text-white shadow-sm',
            emerald: 'bg-[#087A45] hover:bg-[#066237] text-white shadow-sm'
        };

        let actionCall = `switchTab('${rec.action_target}')`;
        if (rec.action_type === 'windows_tool') {
            actionCall = `openWindowsTool('${rec.action_target}')`;
        } else if (rec.action_type === 'admin_modal') {
            actionCall = `openAdminModal()`;
        }

        card.className = "glass-card rounded-2xl p-5 flex flex-col justify-between border border-slate-200 bg-white shadow-sm";
        card.innerHTML = `
            <div>
                <div class="flex items-center justify-between mb-2">
                    <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${badgeColors[rec.color] || badgeColors.amber}">
                        ${rec.badge}
                    </span>
                    <span class="text-[11px] uppercase font-bold text-[#64748B]">Prioridad ${rec.priority}</span>
                </div>
                <h4 class="text-base font-bold text-[#102D25] mt-1">${rec.title}</h4>
                <p class="text-xs text-[#64748B] mt-1.5 leading-relaxed">${rec.description}</p>
            </div>
            <div class="mt-4 pt-3 border-t border-slate-100 flex justify-end">
                <button onclick="${actionCall}" class="px-4 py-2 rounded-xl text-xs font-semibold shadow-sm flex items-center space-x-1.5 transition-all cursor-pointer ${btnColors[rec.color] || btnColors.amber}">
                    <span>${rec.action_label}</span>
                    <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                </button>
            </div>
        `;
        grid.appendChild(card);
    });

    lucide.createIcons();
}

// ======================== TAB 1: OVERVIEW ========================
async function loadOverview() {
    const data = await apiGet('/api/system/overview');
    if (!data) return;
    systemOverviewData = data;
    updateAdminBadgeUI(Boolean(data.is_admin || (data.os && data.os.is_admin)));

    // Header pills
    document.getElementById('pill-user').textContent = `${data.os.user} (${data.os.hostname})`;
    document.getElementById('pill-uptime').textContent = `Activo: ${data.os.uptime}`;

    // System banner
    document.getElementById('pc-hostname').textContent = `${data.os.hostname} - ${data.os.user}`;
    document.getElementById('os-badge').textContent = `${data.os.system} ${data.os.release}`;
    document.getElementById('os-arch').textContent = data.os.architecture;
    document.getElementById('os-details').textContent = `Compilación ${data.os.version} • Iniciado: ${data.os.boot_time}`;

    // CPU Card
    document.getElementById('cpu-name').textContent = data.cpu.name;
    document.getElementById('cpu-name').title = data.cpu.name;
    document.getElementById('cpu-usage').textContent = `${data.cpu.usage_percent}%`;
    document.getElementById('cpu-cores').textContent = `${data.cpu.physical_cores} núcleos / ${data.cpu.total_cores} hilos`;
    document.getElementById('cpu-bar').style.width = `${Math.min(data.cpu.usage_percent, 100)}%`;

    // RAM Card
    document.getElementById('ram-used').textContent = data.ram.used_formatted;
    document.getElementById('ram-total').textContent = `de ${data.ram.total_formatted}`;
    document.getElementById('ram-free').textContent = `Disponible: ${data.ram.free_formatted}`;
    document.getElementById('ram-bar').style.width = `${data.ram.percent_used}%`;

    // GPU Card
    if (data.gpus && data.gpus.length > 0) {
        const gpu = data.gpus[0];
        document.getElementById('gpu-name').textContent = gpu.name;
        document.getElementById('gpu-vram').textContent = `VRAM: ${gpu.vram}`;
        document.getElementById('gpu-driver').textContent = `Driver: ${gpu.driver_version}`;
    } else {
        document.getElementById('gpu-name').textContent = "Gráficos Integrados";
    }

    // Battery Card
    if (data.battery) {
        document.getElementById('battery-pct').textContent = `${data.battery.percent}%`;
        document.getElementById('battery-status').textContent = data.battery.power_plugged ? "Cargando (AC)" : "Batería";
        document.getElementById('battery-bar').style.width = `${data.battery.percent}%`;
        document.getElementById('battery-detail').textContent = data.battery.power_plugged ? "Conectado a la corriente" : "Modo Batería";
    } else {
        document.getElementById('battery-pct').textContent = "100%";
        document.getElementById('battery-status').textContent = "PC de Escritorio";
        document.getElementById('battery-detail').textContent = "Conectado a la corriente (AC)";
        document.getElementById('battery-bar').style.width = `100%`;
    }

    // Hard Drives Grid
    const drivesContainer = document.getElementById('drives-container');
    drivesContainer.innerHTML = '';
    data.drives.forEach(drive => {
        const isAlert = drive.percent_used > 85;
        const barColor = isAlert ? 'bg-rose-500' : 'bg-[#16B84E]';

        const card = document.createElement('div');
        card.className = "glass-card rounded-2xl p-5 border border-slate-200 bg-white shadow-sm";
        card.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2.5">
                    <span class="p-2 rounded-xl bg-[#F4F7F5] text-[#102D25] font-black text-sm border border-slate-200">${drive.device}</span>
                    <div>
                        <h4 class="text-sm font-bold text-[#102D25]">Disco Local (${drive.mountpoint})</h4>
                        <span class="text-xs text-[#64748B] font-mono">${drive.fstype}</span>
                    </div>
                </div>
                <span class="px-2.5 py-1 rounded-full text-xs font-bold ${isAlert ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-[#F4F7F5] text-[#102D25] border border-slate-200'}">
                    ${drive.percent_used}% Usado
                </span>
            </div>

            <div class="mt-4">
                <div class="flex justify-between text-xs text-[#64748B] mb-1.5 font-medium">
                    <span>Libre: <strong class="text-[#087A45] font-bold">${drive.free_formatted}</strong></span>
                    <span>Total: ${drive.total_formatted}</span>
                </div>
                <div class="w-full bg-[#E2E8F0] rounded-full h-3 overflow-hidden">
                    <div class="${barColor} h-3 rounded-full transition-all duration-700" style="width: ${drive.percent_used}%"></div>
                </div>
            </div>

            <div class="mt-4 pt-3 border-t border-slate-100 flex justify-end space-x-2">
                <button onclick="scanDriveInHeavy('${drive.mountpoint.replace(/\\/g, '\\\\')}')" class="px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 text-xs font-semibold text-[#102D25] border border-slate-200 flex items-center space-x-1.5 transition-colors shadow-sm cursor-pointer">
                    <i data-lucide="search" class="w-3.5 h-3.5 text-[#087A45]"></i>
                    <span>Buscar Gigantes</span>
                </button>
                <button onclick="openFolderInExplorer('${drive.mountpoint.replace(/\\/g, '\\\\')}')" class="px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 text-xs font-semibold text-[#102D25] border border-slate-200 flex items-center space-x-1.5 transition-colors shadow-sm cursor-pointer">
                    <i data-lucide="folder" class="w-3.5 h-3.5 text-[#087A45]"></i>
                    <span>Abrir en Explorer</span>
                </button>
            </div>
        `;
        drivesContainer.appendChild(card);
    });

    lucide.createIcons();
}

async function updateQuickMetrics() {
    const data = await apiGet('/api/system/overview');
    if (!data) return;
    document.getElementById('cpu-usage').textContent = `${data.cpu.usage_percent}%`;
    document.getElementById('cpu-bar').style.width = `${Math.min(data.cpu.usage_percent, 100)}%`;
    document.getElementById('ram-used').textContent = data.ram.used_formatted;
    document.getElementById('ram-free').textContent = `Disponible: ${data.ram.free_formatted}`;
    document.getElementById('ram-bar').style.width = `${data.ram.percent_used}%`;
}

// ======================== TAB 2: JUNK CLEANER ========================
async function scanJunk(force = false, silent = false) {
    const btn = document.getElementById('btn-scan-junk');
    const statusLabel = document.getElementById('junk-status-label');
    if (btn) btn.disabled = true;
    if (statusLabel) {
        statusLabel.className = "text-sm font-semibold text-[#087A45] mt-2 flex items-center space-x-1.5";
        statusLabel.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Escaneando carpetas temporales...</span>';
        lucide.createIcons();
    }

    if (force && !silent) {
        startRocketLoader({
            badge: 'ESCÁNER PROFUNDO NOSCLEAN',
            title: 'Analizando Basura y Temporales',
            steps: [
                { at: 0, text: 'Inspeccionando carpetas temporales de usuario (%TEMP%)...' },
                { at: 35, text: 'Revisando cachés de navegadores (Chrome, Edge, Brave)...' },
                { at: 68, text: 'Analizando registros de fallos, Prefetch y Windows Temp...' },
                { at: 85, text: 'Calculando espacio total recuperable...' }
            ]
        });
    }

    const data = await apiGet(`/api/junk/scan${force ? '?force=true' : ''}`);
    if (btn) btn.disabled = false;
    if (!data) {
        if (force && !silent) hideRocketLoader();
        return;
    }
    junkData = data;

    document.getElementById('junk-total-size').textContent = data.total_formatted;
    document.getElementById('junk-total-files').textContent = data.total_files.toLocaleString();
    
    if (statusLabel) {
        statusLabel.className = "text-sm font-semibold text-emerald-400 mt-2 flex items-center space-x-1.5";
        statusLabel.innerHTML = '<i data-lucide="check-circle" class="w-4 h-4"></i><span>Análisis finalizado</span>';
    }

    renderJunkCategories(data.categories);
    lucide.createIcons();

    if (force && !silent) {
        await finishRocketLoader({
            stepText: '¡Análisis de sistema completado!',
            resultTitle: 'Escaneo Finalizado al 100%',
            resultDetail: `Se detectaron ${data.total_files.toLocaleString()} archivos temporales (${data.total_formatted} recuperables).`,
            holdMs: 750
        });
    }
}

function renderJunkCategories(categories) {
    const container = document.getElementById('junk-categories-list');
    container.innerHTML = '';

    categories.forEach(cat => {
        const item = document.createElement('div');
        item.className = "flex items-center justify-between p-3.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 transition-colors shadow-sm";
        
        const hasItems = cat.size_bytes > 0 || cat.file_count > 0;
        const checked = hasItems ? 'checked' : 'disabled';
        const opacity = hasItems ? 'opacity-100' : 'opacity-40';

        const adminBadge = cat.requires_admin 
            ? '<button type="button" onclick="openAdminModal()" title="Haz clic para ejecutar como Administrador" class="ml-1.5 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 hover:bg-amber-200 text-amber-800 border border-amber-300 transition-colors cursor-pointer">Requiere Admin · Activar</button>' 
            : '';

        item.innerHTML = `
            <div class="flex items-center space-x-3 ${opacity}">
                <input type="checkbox" id="chk-junk-${cat.id}" data-id="${cat.id}" ${checked} class="w-4 h-4 text-[#087A45] rounded border-slate-300 focus:ring-[#087A45] cursor-pointer">
                <div>
                    <h4 class="text-sm font-semibold text-[#102D25] flex items-center">${cat.name}${adminBadge}</h4>
                    <p class="text-xs text-[#64748B]">${cat.description}</p>
                </div>
            </div>
            <div class="text-right">
                <span class="text-sm font-bold ${hasItems ? 'text-[#087A45]' : 'text-slate-400'}">${cat.size_formatted}</span>
                <p class="text-xs text-[#64748B]">${cat.file_count.toLocaleString()} archivos</p>
            </div>
        `;
        container.appendChild(item);
    });
}

function toggleAllJunk(select) {
    const checkboxes = document.querySelectorAll('#junk-categories-list input[type="checkbox"]:not(:disabled)');
    checkboxes.forEach(chk => chk.checked = select);
}

function confirmCleanSelected() {
    const selected = [];
    const checkboxes = document.querySelectorAll('#junk-categories-list input[type="checkbox"]:checked');
    checkboxes.forEach(chk => selected.push(chk.getAttribute('data-id')));

    if (selected.length === 0) {
        showToast('No seleccionaste ninguna categoría para limpiar', 'warning');
        return;
    }

    openConfirmModal(
        'Confirmar Limpieza de Basura',
        `Se eliminarán los archivos temporales y cachés de ${selected.length} categorías seleccionadas. Los archivos que estén abiertos o en uso serán omitidos automáticamente de forma segura.`,
        () => executeJunkClean(selected)
    );
}

async function executeJunkClean(selectedCategories) {
    const btn = document.getElementById('btn-clean-junk');
    if (btn) btn.disabled = true;

    startRocketLoader({
        badge: 'MOTOR DE LIMPIEZA NOSCLEAN',
        title: 'Eliminando Archivos Basura',
        steps: [
            { at: 0, text: 'Verificando archivos abiertos y protecciones del sistema...' },
            { at: 30, text: 'Purgando cachés de navegadores y sesiones antiguas...' },
            { at: 62, text: 'Eliminando archivos temporales y volcados de memoria...' },
            { at: 86, text: 'Liberando bloques de almacenamiento en disco...' }
        ]
    });

    const res = await apiPost('/api/junk/clean', { categories: selectedCategories });
    if (btn) btn.disabled = false;

    if (res && res.success) {
        const detailMsg = res.total_skipped > 0
            ? `Se liberaron ${res.freed_formatted} (${res.total_files_deleted.toLocaleString()} archivos eliminados). ${res.total_skipped.toLocaleString()} archivos en uso fueron protegidos.`
            : `Se liberaron ${res.freed_formatted} (${res.total_files_deleted.toLocaleString()} archivos basura eliminados).`;

        // Refrescar métricas en paralelo mientras el cohete llega al 100%
        Promise.all([
            scanJunk(true, true),
            loadOverview(),
            currentTab === 'advisor' ? loadAdvisor() : Promise.resolve()
        ]).catch(() => {});

        await finishRocketLoader({
            stepText: '¡Limpieza profunda finalizada con éxito!',
            resultTitle: `¡Espacio Liberado: ${res.freed_formatted}!`,
            resultDetail: detailMsg,
            holdMs: 1500
        });
        showToast(detailMsg, 'success');
    } else {
        hideRocketLoader();
    }
}

// ======================== TAB 3: HEAVY FILES ========================
function onHeavyPresetChange() {
    const select = document.getElementById('heavy-path-select');
    const input = document.getElementById('heavy-path-input');
    const val = select.value;

    if (val === 'custom') {
        input.focus();
    } else if (commonPaths[val]) {
        input.value = commonPaths[val];
    }
}

function scanDriveInHeavy(drivePath) {
    switchTab('heavy');
    const input = document.getElementById('heavy-path-input');
    const select = document.getElementById('heavy-path-select');
    if (input) input.value = drivePath;
    if (select) select.value = 'custom';
    scanHeavyFiles();
}

async function scanHeavyFiles(showLoader = true) {
    const pathInput = document.getElementById('heavy-path-input');
    const minSizeSelect = document.getElementById('heavy-min-size');
    const btn = document.getElementById('btn-scan-heavy');
    const tbody = document.getElementById('heavy-files-tbody');

    const targetPath = pathInput.value.trim();
    if (!targetPath) {
        showToast('Debes ingresar o seleccionar una ruta para escanear', 'warning');
        return;
    }
    heavyScannedOnce = true;

    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Buscando...</span>';
    lucide.createIcons();

    const minSize = parseInt(minSizeSelect.value) || 100;
    if (showLoader) {
        startRocketLoader({
            badge: 'RADAR DE ALMACENAMIENTO NOSCLEAN',
            title: 'Buscando Archivos Pesados',
            steps: [
                { at: 0, text: `Explorando ruta: ${targetPath}...` },
                { at: 40, text: `Filtrando archivos mayores a ${minSize} MB...` },
                { at: 78, text: 'Ordenando resultados de mayor a menor tamaño...' }
            ]
        });
    }

    tbody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center py-12 text-slate-400">
                <div class="flex flex-col items-center justify-center space-y-3">
                    <i data-lucide="loader-2" class="w-7 h-7 text-[#087A45] animate-spin"></i>
                    <span>Analizando carpetas y buscando archivos grandes... Esto puede tardar unos segundos.</span>
                </div>
            </td>
        </tr>
    `;
    lucide.createIcons();

    const url = `/api/storage/heavy-files?path=${encodeURIComponent(targetPath)}&min_size_mb=${minSize}&max_results=150`;
    const data = await apiGet(url);

    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="search" class="w-4 h-4"></i><span>Buscar Archivos</span>';
    lucide.createIcons();

    if (!data || data.error) {
        if (showLoader) hideRocketLoader();
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-8 text-rose-400">${data?.error || 'Error al buscar archivos'}</td></tr>`;
        return;
    }

    if (showLoader) {
        await finishRocketLoader({
            stepText: '¡Búsqueda de archivos gigantes completada!',
            resultTitle: `${data.found_count} Archivos Detectados`,
            resultDetail: `Espacio total acumulado en estos archivos: ${data.total_size_formatted}.`,
            holdMs: 750
        });
    }

    document.getElementById('heavy-results-badge').textContent = `${data.found_count} archivos`;
    document.getElementById('heavy-total-found-size').textContent = `Total: ${data.total_size_formatted}`;

    if (data.files.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-10 text-slate-400">No se encontraron archivos que superen los ${minSize} MB en esta ruta.</td></tr>`;
        return;
    }

    tbody.innerHTML = '';
    data.files.forEach(f => {
        const row = document.createElement('tr');
        row.className = "hover:bg-slate-50 transition-colors border-b border-slate-100";
        row.innerHTML = `
            <td class="px-4 py-3">
                <div class="flex items-center space-x-2">
                    <i data-lucide="file" class="w-4 h-4 text-[#087A45] flex-shrink-0"></i>
                    <span class="font-bold text-[#102D25] truncate max-w-xs" title="${f.name}">${f.name}</span>
                </div>
            </td>
            <td class="px-4 py-3 font-bold text-[#087A45]">${f.size_formatted}</td>
            <td class="px-4 py-3 text-xs text-slate-400 truncate max-w-sm" title="${f.path}">${f.folder}</td>
            <td class="px-4 py-3 text-xs text-[#64748B]">${f.modified}</td>
            <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end space-x-2">
                    <button onclick="openFolderInExplorer('${f.path.replace(/\\/g, '\\\\')}')" title="Mostrar en Explorador" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 transition-colors">
                        <i data-lucide="folder" class="w-4 h-4"></i>
                    </button>
                    <button onclick="confirmRecycleFile('${f.path.replace(/\\/g, '\\\\')}', '${f.name}')" title="Mover a Papelera" class="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-900/50 text-rose-400 transition-colors">
                        <i data-lucide="trash-2" class="w-4 h-4"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });

    lucide.createIcons();
}

function confirmRecycleFile(filePath, fileName) {
    openConfirmModal(
        'Mover a Papelera de Reciclaje',
        `¿Deseas enviar "${fileName}" a la Papelera de Reciclaje de Windows? Podrás restaurarlo desde la papelera si lo necesitas.`,
        async () => {
            const res = await apiPost('/api/actions/recycle', { path: filePath });
            if (res && res.success) {
                showToast(`"${fileName}" enviado a la papelera`, 'success');
                scanHeavyFiles(false);
            }
        }
    );
}

// ======================== TAB 4: INSTALLED APPS ========================
async function loadInstalledApps() {
    const tbody = document.getElementById('apps-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center py-10 text-slate-400">
                <div class="flex flex-col items-center space-y-2">
                    <i data-lucide="loader-2" class="w-6 h-6 text-[#087A45] animate-spin"></i>
                    <span class="text-[#102D25] font-bold">Analizando registro de Windows...</span>
                </div>
            </td>
        </tr>
    `;
    lucide.createIcons();

    const data = await apiGet('/api/software/installed');
    if (!data) return;
    installedAppsData = data;
    renderAppsTable(data);
}

function renderAppsTable(apps) {
    currentRenderedApps = apps || [];
    const tbody = document.getElementById('apps-tbody');
    const badge = document.getElementById('apps-count-badge');
    badge.textContent = `${currentRenderedApps.length} programas`;

    if (currentRenderedApps.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-10 text-slate-400">No se encontraron programas con ese criterio.</td></tr>`;
        return;
    }

    tbody.innerHTML = '';
    currentRenderedApps.forEach((app, idx) => {
        const row = document.createElement('tr');
        row.className = "hover:bg-slate-50 transition-colors border-b border-slate-100";
        
        const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(app.name)}`;
        const folderBtn = app.install_location
            ? `<button onclick="openAppLocation(${idx})" title="Abrir carpeta de instalación" class="p-1.5 rounded-xl bg-white hover:bg-slate-50 text-[#087A45] border border-slate-200 shadow-sm transition-colors cursor-pointer">
                   <i data-lucide="folder" class="w-3.5 h-3.5"></i>
               </button>`
            : '';

        row.innerHTML = `
            <td class="px-4 py-3">
                <div class="flex items-center space-x-2">
                    <i data-lucide="package" class="w-4 h-4 text-[#087A45] flex-shrink-0"></i>
                    <span class="font-semibold text-[#102D25] max-w-sm truncate" title="${app.name}">${app.name}</span>
                </div>
            </td>
            <td class="px-4 py-3 text-xs text-[#64748B] truncate max-w-xs" title="${app.publisher}">${app.publisher}</td>
            <td class="px-4 py-3 text-xs font-mono text-[#64748B]">${app.version}</td>
            <td class="px-4 py-3 text-xs font-bold text-[#087A45]">${app.size_formatted}</td>
            <td class="px-4 py-3 text-xs text-[#64748B]">${app.install_date}</td>
            <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end space-x-2">
                    ${folderBtn}
                    <a href="${googleSearchUrl}" target="_blank" title="Buscar información en Google" class="p-1.5 rounded-xl bg-white hover:bg-slate-50 text-[#102D25] border border-slate-200 shadow-sm transition-colors cursor-pointer">
                        <i data-lucide="globe" class="w-3.5 h-3.5"></i>
                    </a>
                    <button onclick="askUninstallApp(${idx})" title="Desinstalar programa" class="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-600/30 text-rose-400 transition-colors cursor-pointer">
                        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });

    lucide.createIcons();
}

function openAppLocation(idx) {
    const app = currentRenderedApps[idx];
    if (app && app.install_location) {
        openFolderInExplorer(app.install_location);
    }
}

function askUninstallApp(idx) {
    const app = currentRenderedApps[idx];
    if (!app) return;

    openConfirmModal(
        'Desinstalar Programa',
        `¿Deseas iniciar el desinstalador oficial de "${app.name}"? Se abrirá el asistente del programa para que completes o canceles la desinstalación.`,
        async () => {
            const res = await apiPost('/api/software/uninstall', {
                uninstall_command: app.uninstall_command || '',
                name: app.name
            });
            if (res && res.success) {
                showToast(res.message || `Desinstalador de ${app.name} iniciado`, 'info');
            }
        }
    );
}

function filterApps() {
    const q = document.getElementById('apps-search-input').value.toLowerCase().trim();
    if (!q) {
        sortApps();
        return;
    }
    const filtered = installedAppsData.filter(a => 
        a.name.toLowerCase().includes(q) || 
        a.publisher.toLowerCase().includes(q)
    );
    renderAppsTable(filtered);
}

function sortApps() {
    const sortVal = document.getElementById('apps-sort-select').value;
    const q = document.getElementById('apps-search-input').value.toLowerCase().trim();
    
    let list = [...installedAppsData];
    if (q) {
        list = list.filter(a => a.name.toLowerCase().includes(q) || a.publisher.toLowerCase().includes(q));
    }

    if (sortVal === 'size_desc') {
        list.sort((a, b) => b.size_bytes - a.size_bytes);
    } else if (sortVal === 'name_asc') {
        list.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortVal === 'date_desc') {
        list.sort((a, b) => b.install_date.localeCompare(a.install_date));
    }

    renderAppsTable(list);
}

// ======================== TAB 5: ORGANIZER ========================
function onOrganizerPresetChange() {
    scanOrganizer();
}

async function scanOrganizer() {
    const preset = document.getElementById('organizer-preset-select').value;
    const targetPath = commonPaths[preset] || commonPaths.downloads;
    const tbody = document.getElementById('organizer-tbody');
    
    tbody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center py-10 text-slate-400">
                <i data-lucide="loader-2" class="w-6 h-6 text-amber-400 animate-spin mx-auto mb-2"></i>
                <span>Escaneando archivos sueltos...</span>
            </td>
        </tr>
    `;
    lucide.createIcons();

    const data = await apiGet(`/api/organizer/scan?path=${encodeURIComponent(targetPath)}`);
    if (!data || !data.category_summary) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-8 text-rose-400">No se pudo escanear la carpeta seleccionada.</td></tr>`;
        return;
    }

    // Render categories stats grid
    const catGrid = document.getElementById('organizer-cat-grid');
    catGrid.innerHTML = '';
    
    const catIcons = {
        'Instaladores': 'package',
        'Comprimidos': 'archive',
        'Documentos': 'file-text',
        'Imágenes': 'image',
        'Videos': 'film',
        'Música y Audio': 'music',
        'Código y Scripts': 'code',
        'Otros': 'folder'
    };

    for (const [catName, catStat] of Object.entries(data.category_summary)) {
        if (catStat.count > 0 || ['Instaladores', 'Documentos', 'Comprimidos', 'Imágenes'].includes(catName)) {
            const card = document.createElement('div');
            card.className = "bg-white p-3 rounded-xl border border-slate-200 text-center shadow-sm";
            card.innerHTML = `
                <div class="flex items-center justify-center text-[#087A45] mb-1">
                    <i data-lucide="${catIcons[catName] || 'file'}" class="w-4 h-4"></i>
                </div>
                <p class="text-xs font-semibold text-[#102D25] truncate">${catName}</p>
                <p class="text-base font-extrabold text-[#087A45] mt-0.5">${catStat.count}</p>
                <p class="text-[10px] text-[#64748B]">${catStat.size_formatted}</p>
            `;
            catGrid.appendChild(card);
        }
    }

    // Render loose files
    document.getElementById('organizer-files-count').textContent = `${data.total_files} archivos sueltos (${data.total_size_formatted})`;

    if (!data.files || data.files.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-10">
            <div class="flex items-center justify-center space-x-2 text-[#087A45] font-bold text-sm">
                <i data-lucide="check-circle" class="w-5 h-5 text-[#087A45]"></i>
                <span>Carpeta limpia y ordenada. No hay archivos sueltos pendientes de organizar.</span>
            </div>
        </td></tr>`;
        lucide.createIcons();
        return;
    }

    tbody.innerHTML = '';
    data.files.forEach(f => {
        const row = document.createElement('tr');
        row.className = "hover:bg-slate-50 transition-colors border-b border-slate-100";
        
        let ageBadge = `<span class="px-2 py-0.5 rounded text-[11px] bg-[#F4F7F5] text-[#102D25] border border-slate-200">${f.age_days} días</span>`;
        if (f.age_days >= 90) {
            ageBadge = `<span class="px-2 py-0.5 rounded text-[11px] bg-rose-500/20 text-rose-700 font-semibold">${f.age_days} días (Antiguo)</span>`;
        }

        row.innerHTML = `
            <td class="px-4 py-3">
                <div class="flex items-center space-x-2">
                    <i data-lucide="file" class="w-4 h-4 text-emerald-600 flex-shrink-0"></i>
                    <span class="font-bold text-[#102D25] max-w-xs truncate" title="${f.name}">${f.name}</span>
                </div>
            </td>
            <td class="px-4 py-3">
                <span class="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-50 text-[#087A45] border border-emerald-200 inline-flex items-center space-x-1">
                    <i data-lucide="folder" class="w-3.5 h-3.5 text-[#087A45]"></i>
                    <span>${f.category}</span>
                </span>
            </td>
            <td class="px-4 py-3 text-xs font-bold text-[#102D25]">${f.size_formatted}</td>
            <td class="px-4 py-3 text-xs">${ageBadge}</td>
            <td class="px-4 py-3 text-right">
                <button onclick="openFolderInExplorer('${f.path.replace(/\\/g, '\\\\')}')" title="Ver archivo" class="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-[#087A45] border border-slate-300 transition-colors">
                    <i data-lucide="folder" class="w-4 h-4"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    lucide.createIcons();
}

async function organizeFiles(simulate) {
    const preset = document.getElementById('organizer-preset-select').value;
    const targetPath = commonPaths[preset] || commonPaths.downloads;

    if (simulate) {
        const res = await apiPost('/api/organizer/organize', { path: targetPath, simulate: true });
        if (res) {
            if (res.total_moved === 0) {
                showToast('No hay archivos sueltos para organizar en esta carpeta', 'info');
                return;
            }
            const badges = document.querySelectorAll('#organizer-tbody td:nth-child(2) span span');
            badges.forEach(span => {
                if (!span.textContent.startsWith('Mover a → ')) {
                    span.textContent = `Mover a → ${span.textContent}/`;
                }
            });
            showToast(`Simulación completada: ${res.total_moved} archivos listos para moverse a sus subcarpetas`, 'info');
        }
    } else {
        openConfirmModal(
            'Confirmar Organización Automática',
            `Los archivos sueltos se moverán a carpetas clasificadas (ej: Descargas/Instaladores, Descargas/Documentos, etc.). Tus archivos quedarán totalmente ordenados.`,
            async () => {
                startRocketLoader({
                    badge: 'ORGANIZADOR INTELIGENTE NOSCLEAN',
                    title: 'Clasificando y Ordenando Archivos',
                    steps: [
                        { at: 0, text: 'Analizando extensiones y tipos de archivo...' },
                        { at: 40, text: 'Creando subcarpetas por categoría (Documentos, Instaladores, etc.)...' },
                        { at: 75, text: 'Moviendo archivos de forma segura sin sobrescribir...' }
                    ]
                });
                const res = await apiPost('/api/organizer/organize', { path: targetPath, simulate: false });
                if (res && res.success) {
                    await scanOrganizer();
                    await finishRocketLoader({
                        stepText: '¡Carpeta ordenada al 100%!',
                        resultTitle: '¡Organización Completada!',
                        resultDetail: `Se clasificaron y movieron ${res.total_moved} archivos a sus carpetas correspondientes.`,
                        holdMs: 1300
                    });
                    showToast(`¡Excelente! Se organizaron ${res.total_moved} archivos correctamente`, 'success');
                } else {
                    hideRocketLoader();
                }
            }
        );
    }
}

// ======================== TAB 6: STARTUP & TASKS ========================
async function loadStartupAndProcs() {
    loadStartupApps();
    loadProcesses();
}

async function loadStartupApps() {
    const tbody = document.getElementById('startup-tbody');
    const badge = document.getElementById('startup-count-badge');
    
    tbody.innerHTML = `<tr><td colspan="4" class="text-center py-8 text-slate-400"><i data-lucide="loader-2" class="w-5 h-5 animate-spin mx-auto"></i></td></tr>`;
    lucide.createIcons();

    const data = await apiGet('/api/software/startup');
    if (!data) return;

    badge.textContent = `${data.length} aplicaciones`;
    tbody.innerHTML = '';

    data.forEach(item => {
        const row = document.createElement('tr');
        row.className = "hover:bg-slate-50 transition-colors border-b border-slate-100";
        row.innerHTML = `
            <td class="px-4 py-3 font-bold text-[#102D25]">
                <div class="flex items-center space-x-2">
                    <i data-lucide="zap" class="w-4 h-4 text-emerald-400 flex-shrink-0"></i>
                    <span>${item.name}</span>
                </div>
            </td>
            <td class="px-4 py-3 text-xs text-slate-400 font-medium">${item.location}</td>
            <td class="px-4 py-3 text-xs font-mono text-slate-400 truncate max-w-md" title="${item.command}">${item.command}</td>
            <td class="px-4 py-3 text-right">
                <button onclick="openWindowsTool('startup')" title="Desactivar en Windows" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-emerald-400 border border-slate-700">
                    Administrar
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    lucide.createIcons();
}

async function loadProcesses() {
    const container = document.getElementById('top-procs-grid');
    container.innerHTML = '<div class="col-span-2 text-center py-6 text-slate-400">Cargando procesos activos...</div>';

    const data = await apiGet('/api/system/processes?limit=8');
    if (!data) return;

    container.innerHTML = '';
    data.by_memory.forEach(p => {
        const card = document.createElement('div');
        card.className = "flex items-center justify-between p-3 rounded-xl bg-white border border-slate-200 shadow-sm";
        const safeName = (p.name || '').replace(/'/g, "\\'");
        const killBtn = p.can_terminate
            ? `<button onclick="askKillProcess(${p.pid}, '${safeName}')" title="Finalizar proceso (PID ${p.pid})" class="ml-2.5 p-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 transition-colors cursor-pointer">
                   <i data-lucide="x-circle" class="w-4 h-4"></i>
               </button>`
            : `<span title="Proceso protegido del sistema" class="ml-2.5 p-1.5 rounded-lg bg-slate-100 text-slate-400 border border-slate-200">
                   <i data-lucide="shield" class="w-4 h-4"></i>
               </span>`;
        card.innerHTML = `
            <div class="flex items-center space-x-2.5 min-w-0">
                <div class="p-2 rounded-lg bg-[#16B84E]/10 text-[#087A45] flex-shrink-0">
                    <i data-lucide="activity" class="w-4 h-4"></i>
                </div>
                <div class="min-w-0">
                    <h5 class="text-sm font-semibold text-[#102D25] max-w-[165px] truncate" title="${p.name}">${p.name}</h5>
                    <span class="text-[11px] text-[#64748B]">PID: ${p.pid} • CPU: ${p.cpu_percent}%</span>
                </div>
            </div>
            <div class="flex items-center flex-shrink-0">
                <div class="text-right">
                    <span class="text-sm font-bold text-[#087A45]">${p.memory_formatted}</span>
                    <p class="text-[11px] text-[#64748B]">${p.memory_percent}% RAM</p>
                </div>
                ${killBtn}
            </div>
        `;
        container.appendChild(card);
    });

    lucide.createIcons();
}

function askKillProcess(pid, procName) {
    openConfirmModal(
        'Finalizar Proceso en Memoria',
        `¿Estás seguro de que deseas cerrar "${procName}" (PID: ${pid})? Si tienes documentos sin guardar en esa aplicación, podrías perder los cambios recientes.`,
        async () => {
            const res = await apiPost('/api/system/kill-process', { pid: pid });
            if (res && res.success) {
                showToast(res.message || `Proceso ${procName} finalizado`, 'success');
                setTimeout(() => {
                    loadProcesses();
                    updateQuickMetrics();
                }, 400);
            }
        }
    );
}

// ======================== WINDOWS TOOLS & COMMON ACTIONS ========================
async function openWindowsTool(toolName) {
    const res = await apiPost('/api/actions/open-tool', { tool: toolName });
    if (res && res.success) {
        showToast(`Abriendo herramienta: ${toolName}`, 'info');
    }
}

async function openFolderInExplorer(path) {
    const res = await apiPost('/api/actions/open-explorer', { path: path });
    if (res && res.success) {
        showToast('Abierto en Explorador de Windows', 'info');
    }
}

// ======================== MODAL & TOASTS ========================
function openConfirmModal(title, message, onConfirm) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-message').textContent = message;
    pendingModalAction = onConfirm;

    const modal = document.getElementById('confirm-modal');
    modal.classList.remove('hidden');

    const confirmBtn = document.getElementById('modal-confirm-btn');
    confirmBtn.onclick = () => {
        closeConfirmModal(true);
    };
}

function closeConfirmModal(confirmed) {
    const modal = document.getElementById('confirm-modal');
    modal.classList.add('hidden');
    if (confirmed && typeof pendingModalAction === 'function') {
        pendingModalAction();
    }
    pendingModalAction = null;
}

// ======================== MODAL DE BIENVENIDA Y PERMISOS ADMIN ========================
function updateAdminBadgeUI(isAdmin) {
    isAdminMode = Boolean(isAdmin);
    adminStatusChecked = true;

    const btn = document.getElementById('btn-admin-status');
    const icon = document.getElementById('admin-status-icon');
    const label = document.getElementById('admin-status-label');
    const stdBody = document.getElementById('admin-modal-standard-body');
    const actBody = document.getElementById('admin-modal-active-body');

    if (btn && label && icon) {
        if (isAdminMode) {
            btn.className = "flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 text-[#087A45] font-bold text-xs flex-shrink-0 shadow-sm transition-all cursor-pointer";
            btn.title = "NosClean se está ejecutando con permisos completos de Administrador";
            icon.setAttribute('data-lucide', 'shield-check');
            icon.className = "w-3.5 h-3.5 text-[#087A45] flex-shrink-0";
            label.textContent = "Modo Admin Activo";
        } else {
            btn.className = "flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-amber-50 hover:bg-amber-100 border border-amber-300 text-amber-800 font-bold text-xs flex-shrink-0 shadow-sm transition-all cursor-pointer";
            btn.title = "Haz clic para ejecutar como Administrador o ver los pasos";
            icon.setAttribute('data-lucide', 'shield-alert');
            icon.className = "w-3.5 h-3.5 text-amber-600 flex-shrink-0";
            label.textContent = "Ejecutar como Admin";
        }
    }

    if (stdBody && actBody) {
        if (isAdminMode) {
            stdBody.classList.add('hidden');
            actBody.classList.remove('hidden');
        } else {
            stdBody.classList.remove('hidden');
            actBody.classList.add('hidden');
        }
    }
    lucide.createIcons();
}

function checkWelcomeModal() {
    const dismissed = localStorage.getItem('nosclean_welcome_dismissed');
    if (!dismissed) {
        setTimeout(() => {
            showWelcomeModal();
        }, 300);
    } else {
        checkAdminStartupPrompt();
    }
}

function showWelcomeModal() {
    const modal = document.getElementById('welcome-modal');
    if (modal) {
        modal.classList.remove('hidden');
        lucide.createIcons();
    }
}

function closeWelcomeModal() {
    const modal = document.getElementById('welcome-modal');
    const dontShow = document.getElementById('welcome-dont-show');
    if (dontShow && dontShow.checked) {
        localStorage.setItem('nosclean_welcome_dismissed', 'true');
    }
    if (modal) {
        modal.classList.add('hidden');
    }
    checkAdminStartupPrompt();
}

function checkAdminStartupPrompt() {
    const adminDismissed = localStorage.getItem('nosclean_admin_prompt_dismissed');
    if (adminDismissed === 'true') return;

    const tryShow = () => {
        if (!isAdminMode) {
            openAdminModal();
        }
    };

    if (adminStatusChecked) {
        setTimeout(tryShow, 250);
    } else {
        setTimeout(tryShow, 700);
    }
}

function openAdminModal() {
    const modal = document.getElementById('admin-modal');
    if (modal) {
        updateAdminBadgeUI(isAdminMode);
        modal.classList.remove('hidden');
        lucide.createIcons();
    }
}

function closeAdminModal() {
    const modal = document.getElementById('admin-modal');
    const dontShow = document.getElementById('admin-dont-show');
    if (dontShow && dontShow.checked) {
        localStorage.setItem('nosclean_admin_prompt_dismissed', 'true');
    }
    if (modal) {
        modal.classList.add('hidden');
    }
}

async function restartAsAdmin() {
    const btn = document.getElementById('btn-restart-admin-now');
    const label = document.getElementById('btn-restart-admin-label');
    if (btn) btn.disabled = true;
    if (label) label.textContent = 'Solicitando permiso a Windows...';

    try {
        const res = await fetch('/api/actions/restart-admin', { method: 'POST' });
        const json = await res.json();

        if (json && json.success) {
            if (json.data && json.data.already_admin) {
                updateAdminBadgeUI(true);
                closeAdminModal();
                showToast('NosClean ya está ejecutándose como Administrador.', 'success');
                return;
            }
            document.body.innerHTML = `
                <div class="h-screen w-screen bg-[#F4F7F5] flex flex-col items-center justify-center text-[#102D25] p-6 text-center">
                    <div class="h-16 w-16 rounded-2xl bg-[#16B84E]/15 border border-[#16B84E]/30 flex items-center justify-center text-[#087A45] mb-4 shadow-sm">
                        <i data-lucide="shield-check" class="w-8 h-8"></i>
                    </div>
                    <h1 class="text-2xl font-black text-[#102D25] mb-2">Abriendo en Modo Administrador...</h1>
                    <p class="text-[#64748B] text-sm max-w-md mb-4">Se ha iniciado la nueva ventana de <strong class="text-[#087A45]">NosClean (Administrador)</strong> con todos los permisos del sistema activados.</p>
                    <p class="text-slate-400 text-xs">Esta ventana anterior se cerrará automáticamente.</p>
                </div>
            `;
            lucide.createIcons();
        } else {
            showToast(json?.message || 'No se aceptó el permiso de Administrador. Puedes usar los pasos manuales o continuar en modo estándar.', 'warning');
        }
    } catch (err) {
        showToast(`Error al solicitar modo Administrador: ${err.message}`, 'error');
    } finally {
        if (btn) btn.disabled = false;
        if (label) label.textContent = 'Ejecutar como Administrador Ahora';
    }
}

async function shutdownFromAdminModal() {
    closeAdminModal();
    try {
        await fetch('/api/system/shutdown', { method: 'POST' });
    } catch {}
    document.body.innerHTML = `
        <div class="h-screen w-screen bg-[#F4F7F5] flex flex-col items-center justify-center text-[#102D25] p-6 text-center">
            <div class="h-16 w-16 rounded-2xl bg-[#16B84E]/10 border border-[#16B84E]/30 flex items-center justify-center text-[#087A45] mb-4 shadow-sm">
                <i data-lucide="power" class="w-8 h-8"></i>
            </div>
            <h1 class="text-2xl font-black text-[#102D25] mb-2">NosClean Cerrado (0 MB en uso)</h1>
            <p class="text-[#64748B] text-sm max-w-md mb-5">Ahora puedes abrirlo manualmente como Administrador siguiendo estos pasos:</p>
            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm text-left max-w-md w-full mb-5">
                <ol class="text-xs text-[#1E3A34] space-y-2 list-decimal list-inside leading-relaxed font-medium">
                    <li>Busca el icono de <strong class="text-[#102D25]">NosClean</strong> en tu Escritorio o carpeta.</li>
                    <li>Haz <strong class="text-[#102D25]">clic derecho</strong> sobre el icono.</li>
                    <li>Elige <strong class="text-[#087A45]">"Ejecutar como administrador"</strong> y pulsa <strong class="text-[#102D25]">"Sí"</strong>.</li>
                </ol>
            </div>
            <p class="text-slate-400 text-xs">Ya puedes cerrar esta ventana de forma segura.</p>
        </div>
    `;
    lucide.createIcons();
}

// ======================== MODAL DE QR (AMPLIADO) ========================
function openQrModal() {
    const modal = document.getElementById('qr-modal');
    if (modal) {
        modal.classList.remove('hidden');
        lucide.createIcons();
    }
}

function closeQrModal() {
    const modal = document.getElementById('qr-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// ======================== ATAJOS: ESCRITORIO Y BARRA DE TAREAS ========================
async function createShortcut(target = 'desktop') {
    const isTaskbar = target === 'taskbar';
    showToast(isTaskbar ? 'Preparando acceso oficial para la Barra de Tareas...' : 'Creando acceso directo en el Escritorio...', 'info');

    try {
        const res = await fetch('/api/actions/create-shortcut', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target: target })
        });
        const data = await res.json();

        if (res.ok && data.success) {
            if (isTaskbar) {
                openTaskbarModal();
            } else {
                showToast(data.message || 'Acceso directo oficial creado en tu Escritorio.', 'success');
            }
        } else {
            showToast(data.detail || data.message || 'No se pudo crear el acceso directo.', 'error');
        }
    } catch (err) {
        showToast(`Error al procesar acceso directo: ${err.message}`, 'error');
    }
}

function openTaskbarModal() {
    const modal = document.getElementById('pin-taskbar-modal');
    if (modal) {
        modal.classList.remove('hidden');
        lucide.createIcons();
    }
}

function closeTaskbarModal() {
    const modal = document.getElementById('pin-taskbar-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Escuchar tecla ESC para cerrar cualquier modal abierto
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const adminModal = document.getElementById('admin-modal');
        if (adminModal && !adminModal.classList.contains('hidden')) {
            closeAdminModal();
        }
        const taskbarModal = document.getElementById('pin-taskbar-modal');
        if (taskbarModal && !taskbarModal.classList.contains('hidden')) {
            closeTaskbarModal();
        }
        const qrModal = document.getElementById('qr-modal');
        if (qrModal && !qrModal.classList.contains('hidden')) {
            closeQrModal();
        }
        const welcomeModal = document.getElementById('welcome-modal');
        if (welcomeModal && !welcomeModal.classList.contains('hidden')) {
            closeWelcomeModal();
        }
        const confirmModal = document.getElementById('confirm-modal');
        if (confirmModal && !confirmModal.classList.contains('hidden')) {
            closeConfirmModal(false);
        }
    }
});

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    const colors = {
        success: 'border-[#16B84E] bg-white text-[#087A45] shadow-lg shadow-[#087A45]/10',
        error: 'border-rose-300 bg-white text-rose-700 shadow-lg shadow-rose-500/10',
        warning: 'border-amber-300 bg-white text-amber-700 shadow-lg shadow-amber-500/10',
        info: 'border-slate-300 bg-white text-[#102D25] shadow-lg'
    };

    const icons = {
        success: 'check-circle',
        error: 'alert-circle',
        warning: 'alert-triangle',
        info: 'info'
    };

    toast.className = `flex items-center space-x-2.5 px-4 py-3 rounded-xl border shadow-2xl backdrop-blur-md text-xs font-medium pointer-events-auto transition-all transform duration-300 ${colors[type] || colors.info}`;
    toast.innerHTML = `
        <i data-lucide="${icons[type] || 'info'}" class="w-4 h-4 flex-shrink-0"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
        toast.classList.add('opacity-0', 'scale-95');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ======================== PANTALLA DE CARGA COHETE CON PORCENTAJE DINÁMICO REAL ========================
let rocketInterval = null;
let rocketPollInterval = null;
let rocketCurrentPercent = 0;
let rocketTargetPercent = 0;
let rocketBackendStep = '';
let rocketStartedAt = 0;

function updateRocketUI(percent, stepText) {
    const pctEl = document.getElementById('rocket-percent-text');
    const barEl = document.getElementById('rocket-progress-bar');
    const stepEl = document.getElementById('rocket-step-text');
    const rounded = Math.max(0, Math.min(100, Math.round(percent)));
    if (pctEl) pctEl.textContent = `${rounded}%`;
    if (barEl) barEl.style.width = `${rounded}%`;
    if (stepText && stepEl) stepEl.textContent = stepText;
}

function startRocketLoader({ title = 'Optimizando tu PC', steps = [] } = {}) {
    if (rocketInterval) {
        clearInterval(rocketInterval);
        rocketInterval = null;
    }
    if (rocketPollInterval) {
        clearInterval(rocketPollInterval);
        rocketPollInterval = null;
    }

    const modal = document.getElementById('rocket-loader-modal');
    const titleEl = document.getElementById('rocket-title');
    const resultBox = document.getElementById('rocket-result-box');
    const rocketSvg = document.getElementById('rocket-svg-actor');

    rocketCurrentPercent = 1;
    rocketTargetPercent = 5;
    rocketBackendStep = '';
    rocketStartedAt = performance.now();

    if (titleEl) titleEl.textContent = title;
    if (resultBox) resultBox.classList.add('hidden');
    if (rocketSvg) {
        rocketSvg.classList.remove('rocket-launching');
        rocketSvg.classList.add('rocket-floating');
    }

    const initialStep = steps.length > 0 ? steps[0].text : 'Iniciando operación...';
    updateRocketUI(1, initialStep);

    if (modal) {
        modal.classList.remove('hidden');
        lucide.createIcons();
    }

    // Consultar el porcentaje real del backend cada 100ms
    rocketPollInterval = setInterval(async () => {
        try {
            const res = await fetch('/api/system/progress');
            if (res.ok) {
                const prog = await res.json();
                if (prog && typeof prog.percent === 'number' && prog.percent > rocketTargetPercent) {
                    rocketTargetPercent = Math.min(99, prog.percent);
                }
                if (prog && prog.step) {
                    rocketBackendStep = prog.step;
                }
            }
        } catch {}
    }, 100);

    // Animación continua grado por grado (jamás se congela en un número fijo)
    rocketInterval = setInterval(() => {
        if (rocketCurrentPercent < rocketTargetPercent) {
            const diff = rocketTargetPercent - rocketCurrentPercent;
            rocketCurrentPercent += Math.max(1, diff * 0.35);
        } else if (rocketCurrentPercent < 99) {
            // Avance dinámico continuo mientras procesa carpetas grandes
            const stepInc = rocketCurrentPercent < 60 ? 1.4 : (rocketCurrentPercent < 85 ? 0.85 : 0.45);
            rocketCurrentPercent = Math.min(99, rocketCurrentPercent + stepInc);
            rocketTargetPercent = Math.max(rocketTargetPercent, rocketCurrentPercent);
        }

        let currentStepMsg = rocketBackendStep;
        if (!currentStepMsg) {
            for (let i = steps.length - 1; i >= 0; i--) {
                if (rocketCurrentPercent >= steps[i].at) {
                    currentStepMsg = steps[i].text;
                    break;
                }
            }
        }
        updateRocketUI(rocketCurrentPercent, currentStepMsg);
    }, 65);
}

async function finishRocketLoader({ stepText = '¡Proceso completado al 100%!', resultTitle = '¡Operación Completada!', resultDetail = '', holdMs = 1250 } = {}) {
    if (rocketInterval) {
        clearInterval(rocketInterval);
        rocketInterval = null;
    }
    if (rocketPollInterval) {
        clearInterval(rocketPollInterval);
        rocketPollInterval = null;
    }

    // Si terminó súper rápido, avanzar suavemente hasta el 100% sin saltos bruscos
    if (rocketCurrentPercent < 96) {
        const frames = 8;
        const delta = (100 - rocketCurrentPercent) / frames;
        for (let i = 0; i < frames; i++) {
            rocketCurrentPercent = Math.min(99, rocketCurrentPercent + delta);
            updateRocketUI(rocketCurrentPercent);
            await new Promise(r => setTimeout(r, 30));
        }
    }

    updateRocketUI(100, stepText);

    const rocketSvg = document.getElementById('rocket-svg-actor');
    if (rocketSvg) {
        rocketSvg.classList.remove('rocket-floating');
        rocketSvg.classList.add('rocket-launching');
    }

    const resultBox = document.getElementById('rocket-result-box');
    const resTitleEl = document.getElementById('rocket-result-title');
    const resDetailEl = document.getElementById('rocket-result-detail');

    if (resultBox && resultDetail) {
        if (resTitleEl) resTitleEl.textContent = resultTitle;
        if (resDetailEl) resDetailEl.textContent = resultDetail;
        resultBox.classList.remove('hidden');
        lucide.createIcons();
    }

    await new Promise(r => setTimeout(r, holdMs));
    hideRocketLoader();
}

function hideRocketLoader() {
    if (rocketInterval) {
        clearInterval(rocketInterval);
        rocketInterval = null;
    }
    if (rocketPollInterval) {
        clearInterval(rocketPollInterval);
        rocketPollInterval = null;
    }
    const modal = document.getElementById('rocket-loader-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// ======================== OPTIMIZACIÓN RÁPIDA EN 1 CLIC ========================
async function quickOptimizePC() {
    const btn = document.getElementById('btn-quick-optimize');
    const label = document.getElementById('optimize-label');
    const icon = document.getElementById('optimize-icon');
    
    if (btn) {
        btn.disabled = true;
        btn.classList.add('opacity-75', 'cursor-wait');
    }
    if (label) label.innerText = 'Optimizando...';
    if (icon) icon.classList.add('animate-pulse');

    startRocketLoader({
        title: 'Impulsando y Optimizando tu PC',
        steps: [
            { at: 0, text: 'Analizando procesos activos en memoria RAM...' },
            { at: 32, text: 'Liberando bloques de RAM inactiva (Working Set)...' },
            { at: 64, text: 'Vaciando caché de resolución DNS de Windows...' },
            { at: 84, text: 'Depurando archivos temporales rápidos...' }
        ]
    });

    try {
        const res = await fetch('/api/system/optimize', { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            const ramText = data.ram_freed_formatted || '0 B';
            const diskText = data.disk_freed_formatted || '0 B';
            const summaryText = `RAM liberada: ${ramText} • Temporales eliminados: ${diskText}. Uso actual de RAM: ${data.new_ram_used_gb} GB (${data.new_ram_percent}%).`;
            
            // Refrescar métricas en paralelo sin frenar el 100%
            Promise.all([
                loadOverview(),
                currentTab === 'cleaner' ? scanJunk(true, true) : Promise.resolve(),
                currentTab === 'advisor' ? loadAdvisor() : Promise.resolve()
            ]).catch(() => {});

            await finishRocketLoader({
                stepText: '¡Tu PC ha sido optimizada al 100%!',
                resultTitle: '¡Aceleración Completada con Éxito!',
                resultDetail: summaryText,
                holdMs: 1500
            });

            showToast(`Optimización completada: ${ramText} de RAM y ${diskText} de disco liberados.`, 'success');
        } else {
            hideRocketLoader();
            showToast('Ocurrió un error al optimizar el equipo.', 'error');
        }
    } catch (err) {
        hideRocketLoader();
        showToast(`Error al optimizar: ${err.message}`, 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.classList.remove('opacity-75', 'cursor-wait');
        }
        if (label) label.innerText = 'Optimizar PC';
        if (icon) {
            icon.classList.remove('animate-pulse');
            icon.classList.remove('animate-spin');
        }
        lucide.createIcons();
    }
}

// ======================== APAGAR Y SALIR (0 MB DE CONSUMO - CERO VENTANAS NATIVAS) ========================
function shutdownApp() {
    openConfirmModal(
        'Apagar y Salir',
        '¿Deseas cerrar NosClean por completo? Dejará de consumir memoria y procesador en segundo plano (0 MB). Podrás volver a abrirla cuando quieras desde el acceso directo de tu Escritorio.',
        async () => {
            try {
                await fetch('/api/system/shutdown', { method: 'POST' });
            } catch {}
            document.body.innerHTML = `
                <div class="h-screen w-screen bg-[#F4F7F5] flex flex-col items-center justify-center text-[#102D25] p-6 text-center">
                    <div class="h-16 w-16 rounded-2xl bg-[#16B84E]/10 border border-[#16B84E]/30 flex items-center justify-center text-[#087A45] mb-4 shadow-sm">
                        <i data-lucide="power" class="w-8 h-8"></i>
                    </div>
                    <h1 class="text-2xl font-black text-[#102D25] mb-2">NosClean Apagado</h1>
                    <p class="text-[#64748B] text-sm max-w-md mb-6">El panel se ha cerrado por completo. Actualmente consume <span class="text-[#087A45] font-bold">0 MB de RAM y 0% de CPU</span>.</p>
                    <p class="text-slate-400 text-xs">Ya puedes cerrar esta pestaña del navegador de forma segura. Para volver a iniciar, abre el acceso directo en tu Escritorio.</p>
                </div>
            `;
            lucide.createIcons();
        }
    );
}
