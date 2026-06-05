const apiBase = "";

function dom(id) {
  return document.getElementById(id);
}

function fetchJson(path, opts = {}) {
  return fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  }).then(async (response) => {
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Error ${response.status}: ${text}`);
    }
    return response.json();
  });
}

// NAVEGACIÓN PRINCIPAL
function showSection(sectionId) {
  document.querySelectorAll(".page").forEach((section) => {
    section.classList.toggle("active", section.id === sectionId);
  });
  document.querySelectorAll("nav button").forEach((button) => {
    button.classList.toggle("active", button.dataset.section === sectionId);
  });

  switch (sectionId) {
    case "dashboard":
      loadDashboard();
      break;
    case "contenido":
      initContenido();
      break;
    case "analisis":
      initAnalisis();
      break;
    case "automatizacion":
      loadAutomation();
      loadAutomationRuns();
      break;
    case "configuracion":
      loadConfig();
      break;
    case "channels":
      loadChannels();
      break;
  }
}

// DASHBOARD
function loadDashboard() {
  const filter = dom("dashboard-channel-filter");
  const channelId = filter ? filter.value : "";
  
  if (filter && filter.options.length <= 1) {
    loadChannelSelectors();
  }

  fetchJson(`${apiBase}/api/dashboard/summary${channelId ? `?channel_id=${channelId}` : ""}`)
    .then((data) => {
      renderSummary(data);
      renderCalendar(data.publication_calendar || []);
      renderChannelsOverview(data.channels_overview || []);
    })
    .catch((err) => console.error("Error dashboard:", err));
}

function renderSummary(data) {
  const content = dom("summary-content");
  if (!content) return;
  
  content.innerHTML = `
    <div class="summary-stats">
      <p><strong>Guiones:</strong> ${Object.entries(data.scripts_by_status || {}).map(([s, c]) => `${s}: ${c}`).join(", ")}</p>
      <p><strong>Videos:</strong> ${Object.entries(data.videos_by_status || {}).map(([s, c]) => `${s}: ${c}`).join(", ")}</p>
      <p><strong>Automatizaciones activas:</strong> ${data.active_automation_runs?.length || 0}</p>
    </div>
  `;
}

function renderCalendar(events) {
  const grid = dom("calendar-grid");
  const monthYear = dom("calendar-month-year");
  if (!grid) return;

  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const today = now.getDate();
  
  const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
  monthYear.innerText = `${monthNames[month]} ${year}`;

  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  let html = "";
  for (let i = 0; i < (firstDay === 0 ? 6 : firstDay - 1); i++) {
    html += `<div class="calendar-cell empty"></div>`;
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const isToday = d === today;
    const isMarked = d <= today;
    const dayEvents = events.filter(e => {
      const ed = new Date(e.date);
      return ed.getDate() === d && ed.getMonth() === month;
    });

    html += `
      <div class="calendar-cell ${isToday ? 'today' : ''} ${isMarked ? 'marked' : ''}">
        <span class="calendar-day">${d}</span>
        ${dayEvents.map(e => `<div class="calendar-event" style="background:${e.color}">${e.title}</div>`).join("")}
      </div>
    `;
  }
  grid.innerHTML = html;
}

function renderChannelsOverview(channels) {
  const container = dom("channels-overview");
  if (!container) return;
  
  container.innerHTML = channels.map(c => `
    <div class="card channel-summary-card">
      <div class="flex-header">
        <img src="${apiBase}/api/channels/${c.channel_id}/thumbnail" class="channel-img" onerror="this.src='https://via.placeholder.com/50'">
        <div>
          <strong>${c.channel_name}</strong>
          <div class="text-small">${c.customUrl || ''}</div>
        </div>
      </div>
      <div class="mt-10">
        <span class="badge" style="background:${c.channel_color || '#eee'}">Canal</span>
        <p class="text-small">${c.description ? c.description.substring(0, 60) + '...' : 'Sin descripción'}</p>
      </div>
    </div>
  `).join("");
}

// CONTENIDO
function initContenido() {
  loadChannelSelectors();
  const filter = dom("content-channel-filter");
  filter.onchange = () => {
    if (filter.value) {
      dom("content-display").classList.remove("hidden");
      dom("content-placeholder").classList.add("hidden");
      loadChannelContent(filter.value);
    } else {
      dom("content-display").classList.add("hidden");
      dom("content-placeholder").classList.remove("hidden");
    }
  };

  document.querySelectorAll(".content-tab").forEach(tab => {
    tab.onclick = () => {
      document.querySelectorAll(".content-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      tab.classList.add("active");
      dom(`tab-${tab.dataset.tab}`).classList.add("active");
    };
  });
}

function loadChannelContent(channelId) {
  const stages = ["idea", "script", "developed", "video"];
  const containers = {
    idea: "ideas-list",
    script: "content-scripts-list",
    developed: "developed-list",
    video: "content-videos-list"
  };

  stages.forEach(stage => {
    fetchJson(`${apiBase}/api/content/${channelId}?stage=${stage}`)
      .then(items => {
        const list = dom(containers[stage]);
        if (!list) return;
        list.innerHTML = items.map(item => `
          <div class="item-row">
            <div>
              <strong>${item.title}</strong>
              <div class="text-small">${item.status} | ${new Date(item.created_at).toLocaleDateString()}</div>
            </div>
            <button onclick="openWorkflowModal(${item.id})" class="btn-outline btn-sm">Gestionar</button>
          </div>
        `).join("") || `<p class="text-muted">No hay contenido en esta etapa</p>`;
      });
  });
}

// FLUJO DE TRABAJO MANUAL
function openNewIdeaModal() {
  dom("idea-form").reset();
  dom("idea-modal").showModal();
}

dom("idea-form").onsubmit = (e) => {
  e.preventDefault();
  const channelId = dom("content-channel-filter").value;
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  data.channel_id = parseInt(channelId);
  data.stage = "idea";

  fetchJson(`${apiBase}/api/content/`, {
    method: "POST",
    body: JSON.stringify(data)
  }).then(() => {
    dom("idea-modal").close();
    loadChannelContent(channelId);
  });
};

let currentItem = null;

async function openWorkflowModal(itemId) {
  const channelId = dom("content-channel-filter").value;
  const items = await fetchJson(`${apiBase}/api/content/${channelId}`);
  currentItem = items.find(i => i.id === itemId);
  
  if (!currentItem) return;

  dom("workflow-item-id").value = itemId;
  dom("workflow-modal-title").innerText = `${currentItem.title} (${currentItem.stage})`;
  
  const fields = dom("workflow-fields");
  const genBtn = dom("btn-generate-script");
  fields.innerHTML = "";

  if (currentItem.stage === "idea") {
    fields.innerHTML = `
      <label>Título: <input type="text" name="title" value="${currentItem.title}"></label>
      <label>Notas de la Idea: <textarea name="idea_notes" rows="5">${currentItem.idea_notes || ""}</textarea></label>
    `;
    genBtn.classList.remove("hidden");
  } else if (currentItem.stage === "script") {
    fields.innerHTML = `
      <label>Título: <input type="text" name="title" value="${currentItem.title}"></label>
      <label>Contenido del Guión: <textarea name="script_content" rows="10">${currentItem.script_content || ""}</textarea></label>
      <label>Contenido del Artículo: <textarea name="article_content" rows="5">${currentItem.article_content || ""}</textarea></label>
    `;
    genBtn.classList.add("hidden");
  } else if (currentItem.stage === "developed") {
    fields.innerHTML = `
      <label>Título: <input type="text" name="title" value="${currentItem.title}"></label>
      <label>Datos de Desarrollo (JSON): <textarea name="developed_data" rows="5">${JSON.stringify(currentItem.developed_data || {}, null, 2)}</textarea></label>
    `;
    genBtn.classList.add("hidden");
  } else if (currentItem.stage === "video") {
    fields.innerHTML = `
      <label>Título: <input type="text" name="title" value="${currentItem.title}"></label>
      <p>Etapa final del video. Aquí se gestionaría la exportación.</p>
    `;
    genBtn.classList.add("hidden");
  }

  dom("workflow-modal").showModal();
}

dom("btn-generate-script").onclick = () => {
  if (!currentItem || currentItem.stage !== "idea") return;
  
  const btn = dom("btn-generate-script");
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
  
  fetchJson(`${apiBase}/api/content/${currentItem.id}/generate-script`, { method: "POST" })
    .then(result => {
      alert("Guión generado exitosamente con IA");
      loadChannelContent(dom("content-channel-filter").value);
      dom("workflow-modal").close();
    })
    .catch(err => {
      alert("Error al generar guión: " + err.message);
    })
    .finally(() => {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Generar Guión con IA';
    });
}

dom("workflow-form").onsubmit = (e) => {
  e.preventDefault();
  const itemId = dom("workflow-item-id").value;
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  
  if (data.developed_data) {
    try { data.developed_data = JSON.parse(data.developed_data); } catch(e) {}
  }

  fetchJson(`${apiBase}/api/content/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify(data)
  }).then(() => {
    alert("Cambios guardados");
    loadChannelContent(dom("content-channel-filter").value);
  });
};

dom("btn-advance-stage").onclick = () => {
  if (!currentItem) return;
  const stages = ["idea", "script", "developed", "video"];
  const currentIndex = stages.indexOf(currentItem.stage);
  
  if (currentIndex < stages.length - 1) {
    const nextStage = stages[currentIndex + 1];
    if (confirm(`¿Avanzar a la etapa de ${nextStage}?`)) {
      fetchJson(`${apiBase}/api/content/${currentItem.id}`, {
        method: "PATCH",
        body: JSON.stringify({ stage: nextStage })
      }).then(() => {
        dom("workflow-modal").close();
        loadChannelContent(dom("content-channel-filter").value);
      });
    }
  } else {
    alert("Ya está en la etapa final");
  }
};

// ANÁLISIS
function initAnalisis() {
  loadChannelSelectors();
  const filter = dom("analytics-channel-filter");
  const refreshBtn = dom("refresh-analytics");
  
  filter.onchange = () => {
    if (filter.value) {
      dom("analytics-display").classList.remove("hidden");
      dom("analytics-placeholder").classList.add("hidden");
      refreshBtn.classList.remove("hidden");
      loadChannelAnalytics(filter.value);
    } else {
      dom("analytics-display").classList.add("hidden");
      dom("analytics-placeholder").classList.remove("hidden");
      refreshBtn.classList.add("hidden");
    }
  };

  refreshBtn.onclick = () => {
    const id = filter.value;
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Actualizando...';
    fetchJson(`${apiBase}/api/analytics/import/${id}`, { method: "POST" })
      .then(() => loadChannelAnalytics(id))
      .finally(() => {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Actualizar Datos';
      });
  };
}

function loadChannelAnalytics(channelId) {
  fetchJson(`${apiBase}/api/analytics/daily-stats/${channelId}`)
    .then(stats => {
      if (stats.length > 0) {
        const last = stats[stats.length - 1];
        dom("stat-subscribers").innerText = last.subscriber_count.toLocaleString();
        dom("stat-views").innerText = last.view_count.toLocaleString();
        dom("stat-video-count").innerText = last.video_count.toLocaleString();
        
        dom("views-chart").innerHTML = `
          <div class="chart-mock">
            ${stats.slice(-7).map(s => `
              <div class="chart-bar" style="height: ${(s.view_count % 100)}px" title="${s.stat_date}: ${s.view_count}"></div>
            `).join("")}
          </div>
          <p class="text-center text-small">Vistas en los últimos 7 registros</p>
        `;
      }
    });

  fetchJson(`${apiBase}/api/analytics/publications-history/${channelId}`)
    .then(history => {
      dom("publications-history-list").innerHTML = history.map(h => `
        <div class="item-row">
          <span>${new Date(h.date).toLocaleDateString()}</span>
          <strong>${h.title}</strong>
          <span class="badge">${h.platform}</span>
        </div>
      `).join("") || "Sin historial de publicaciones";
    });
}

// CONFIGURACIÓN
function loadConfig() {
  fetchJson(`${apiBase}/api/config`)
    .then(configs => {
      configs.forEach(c => {
        const input = dom(c.key);
        if (input) input.value = c.value;
      });
    });

  dom("config-form").onsubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const promises = [];
    
    for (let [key, value] of formData.entries()) {
      promises.push(fetchJson(`${apiBase}/api/config`, {
        method: "POST",
        body: JSON.stringify({ key, value })
      }));
    }

    Promise.all(promises)
      .then(() => alert("Configuración guardada"))
      .catch(err => alert("Error al guardar: " + err.message));
  };
}

// CANALES Y HERRAMIENTAS
function loadChannels() {
  fetchJson(`${apiBase}/api/channels`)
    .then(channels => {
      dom("channel-list").innerHTML = channels.map(c => `
        <div class="item-row">
          <div class="flex-header">
            <img src="${apiBase}/api/channels/${c.id}/thumbnail" class="channel-img" onerror="this.src='https://via.placeholder.com/50'">
            <div>
              <strong>${c.title}</strong>
              <div class="text-small">${c.customUrl || 'Sin URL'}</div>
            </div>
          </div>
          <button onclick="deleteChannel(${c.id})" class="btn-outline text-danger"><i class="fas fa-trash"></i></button>
        </div>
      `).join("") || "No hay canales registrados";
    });
}

function deleteChannel(id) {
  if (!confirm("¿Eliminar canal?")) return;
  fetchJson(`${apiBase}/api/channels/${id}`, { method: "DELETE" })
    .then(() => loadChannels());
}

dom("btn-create-files").onclick = () => {
  const name = dom("channel-name").value;
  if (!name) return alert("Introduce el nombre del canal");
  
  const status = dom("creation-status");
  const btn = dom("btn-create-files");
  const saveBtn = dom("btn-save-channel");
  
  status.classList.remove("hidden", "status-success", "status-error");
  status.innerText = "Ejecutando script de creación...";
  btn.disabled = true;

  fetchJson(`${apiBase}/api/channels/tools/create-files?name=${encodeURIComponent(name)}`, { method: "POST" })
    .then(res => {
      status.classList.add("status-success");
      status.innerText = "¡Correcto! Ficheros generados en channels_data. Ahora puedes guardar en la BD.";
      saveBtn.disabled = false;
    })
    .catch(err => {
      status.classList.add("status-error");
      status.innerText = "Error: " + err.message;
    })
    .finally(() => btn.disabled = false);
};

dom("channel-form").onsubmit = (e) => {
  e.preventDefault();
  const name = dom("channel-name").value;
  const color = dom("channel-color").value;
  
  fetchJson(`${apiBase}/api/channels`, {
    method: "POST",
    body: JSON.stringify({ title: name, color: color })
  })
    .then(() => {
      alert("Canal guardado en base de datos");
      dom("channel-form").reset();
      dom("btn-save-channel").disabled = true;
      dom("creation-status").classList.add("hidden");
      loadChannels();
    })
    .catch(err => alert("Error al guardar: " + err.message));
};

// HELPERS
function loadChannelSelectors() {
  fetchJson(`${apiBase}/api/channels`)
    .then(channels => {
      const selectors = ["dashboard-channel-filter", "content-channel-filter", "analytics-channel-filter", "modal-automation-channel-id"];
      selectors.forEach(id => {
        const el = dom(id);
        if (!el) return;
        const currentVal = el.value;
        el.innerHTML = (id.includes("modal") ? "" : '<option value="">Selecciona un canal</option>') + 
          channels.map(c => `<option value="${c.id}">${c.title}</option>`).join("");
        el.value = currentVal;
      });
    });
}

// AUTOMATIZACIÓN
function loadAutomation() {
  fetchJson(`${apiBase}/api/automation/tasks`)
    .then(tasks => {
      dom("automation-list").innerHTML = tasks.map(t => `
        <div class="item-row">
          <div>
            <strong>${t.name}</strong>
            <div class="text-small">${t.schedule_expression || 'Manual'} | ${t.is_active ? 'Activa' : 'Inactiva'}</div>
          </div>
          <button onclick="runAutomation(${t.id})" class="btn-primary btn-sm">Ejecutar</button>
        </div>
      `).join("") || "No hay tareas";
    });
}

function loadAutomationRuns() {
  fetchJson(`${apiBase}/api/automation/runs`)
    .then(runs => {
      dom("automation-runs-list").innerHTML = runs.slice(0, 5).map(r => `
        <div class="item-row">
          <span>${new Date(r.started_at).toLocaleString()}</span>
          <span class="badge">${r.status}</span>
        </div>
      `).join("") || "No hay ejecuciones";
    });
}

function runAutomation(id) {
  fetchJson(`${apiBase}/api/automation/tasks/${id}/run`, { method: "POST" })
    .then(() => {
      alert("Ejecución lanzada");
      loadAutomationRuns();
    });
}

// INICIALIZACIÓN
document.querySelectorAll("nav button").forEach(btn => {
  btn.onclick = () => showSection(btn.dataset.section);
});

dom("automation-form").onsubmit = (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  data.channel_id = parseInt(data.channel_id);
  data.workflow_definition = JSON.parse(data.workflow_definition);
  
  fetchJson(`${apiBase}/api/automation/tasks`, {
    method: "POST",
    body: JSON.stringify(data)
  }).then(() => {
    dom("automation-modal").close();
    loadAutomation();
  });
};

showSection("dashboard");
