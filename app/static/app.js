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

  // Tabs de configuración
  document.querySelectorAll(".config-tab").forEach(tab => {
    tab.onclick = () => {
      document.querySelectorAll(".config-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".config-tab-content").forEach(c => c.classList.add("hidden"));
      tab.classList.add("active");
      const tabName = tab.dataset.configTab;
      dom(`config-${tabName}`).classList.remove("hidden");
      if (tabName === "prompts") loadPrompts();
    };
  });
}

// BIBLIOTECA DE PROMPTS
function loadPrompts() {
  const typeFilter = dom("prompt-type-filter");
  const searchInput = dom("prompt-search");
  
  function fetchAndRender() {
    const type = typeFilter.value;
    const url = type ? `${apiBase}/api/prompts?prompt_type=${type}` : `${apiBase}/api/prompts`;
    
    fetchJson(url)
      .then(prompts => {
        const list = dom("prompts-list");
        if (searchInput.value) {
          prompts = prompts.filter(p => p.title.toLowerCase().includes(searchInput.value.toLowerCase()));
        }
        
        list.innerHTML = prompts.map(p => `
          <div class="prompt-card card" onclick="openPromptDetail(${p.id})">
            <div class="prompt-header">
              <h4>${p.title}</h4>
              <span class="badge">${p.prompt_type}</span>
            </div>
            <p class="text-small">${p.description || "Sin descripción"}</p>
            <div class="prompt-meta">
              <span><i class="fas fa-star"></i> ${p.rating.toFixed(1)}/5</span>
              <span><i class="fas fa-check-circle"></i> ${p.usage_count} usos</span>
              <span><i class="fas fa-code"></i> v${p.version}</span>
            </div>
            <div class="prompt-variables">
              ${p.variables.length > 0 ? `<strong>Variables:</strong> ${p.variables.join(", ")}` : "Sin variables"}
            </div>
          </div>
        `).join("") || "<p>No hay prompts</p>";
      });
  }
  
  typeFilter.onchange = fetchAndRender;
  searchInput.onkeyup = fetchAndRender;
  
  fetchAndRender();
}

function openPromptDetail(promptId) {
  fetchJson(`${apiBase}/api/prompts/${promptId}`)
    .then(prompt => {
      dom("prompt-detail-title").innerText = prompt.title;
      dom("prompt-detail-content").innerHTML = `
        <div class="prompt-detail">
          <p><strong>Tipo:</strong> ${prompt.prompt_type}</p>
          <p><strong>Descripción:</strong> ${prompt.description || "N/A"}</p>
          <p><strong>Versión:</strong> ${prompt.version}</p>
          <p><strong>Puntuación:</strong> ${prompt.rating.toFixed(1)}/5</p>
          <p><strong>Usos:</strong> ${prompt.usage_count}</p>
          <p><strong>Variables:</strong> ${prompt.variables.join(", ") || "Ninguna"}</p>
          <div class="prompt-content-box">
            <strong>Contenido:</strong>
            <pre>${prompt.content}</pre>
          </div>
          <div class="rating-input">
            <label>Calificar (0-5):
              <input type="number" min="0" max="5" step="0.5" id="rating-input" value="${prompt.rating}">
              <button type="button" onclick="ratePrompt(${promptId})">Guardar Calificación</button>
            </label>
          </div>
        </div>
      `;
      dom("prompt-detail-modal").showModal();
    });
}

function ratePrompt(promptId) {
  const rating = parseFloat(dom("rating-input").value);
  if (rating < 0 || rating > 5) return alert("Calificación inválida");
  
  fetchJson(`${apiBase}/api/prompts/${promptId}/rate?rating=${rating}`, { method: "POST" })
    .then(() => {
      alert("Calificación guardada");
      loadPrompts();
    });
}

dom("prompt-form").onsubmit = (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  
  fetchJson(`${apiBase}/api/prompts`, {
    method: "POST",
    body: JSON.stringify(data)
  }).then(() => {
    alert("Prompt creado exitosamente");
    dom("prompt-create-modal").close();
    loadPrompts();
  });
};

dom("prompt-form").addEventListener("input", (e) => {
  if (e.target.name === "content") {
    const content = e.target.value;
    const variables = content.match(/\{\{(\w+)\}\}/g) || [];
    const unique = [...new Set(variables.map(v => v.slice(2, -2)))];
    dom("detected-variables").innerHTML = unique.length > 0 
      ? `<strong>Variables detectadas:</strong> ${unique.join(", ")}`
      : "";
  }
});

// CANALES Y HERRAMIENTAS
let currentChannelId = null;

function loadChannels() {
  fetchJson(`${apiBase}/api/channels`)
    .then(channels => {
      dom("channel-list").innerHTML = channels.map(c => `
        <div class="item-row" style="cursor:pointer" onclick="selectChannel(${c.id})">
          <div class="flex-header">
            <img src="${apiBase}/api/channels/${c.id}/thumbnail" class="channel-img" onerror="this.src='https://via.placeholder.com/50'">
            <div>
              <strong>${c.title}</strong>
              <div class="text-small">${c.customUrl || 'Sin URL'}</div>
            </div>
          </div>
          <button onclick="event.stopPropagation(); deleteChannel(${c.id})" class="btn-outline text-danger"><i class="fas fa-trash"></i></button>
        </div>
      `).join("") || "No hay canales registrados";
    });
}

function selectChannel(channelId) {
  currentChannelId = channelId;
  loadChannelSchedule(channelId);
  loadChannelCalendar(channelId);
  loadUpcomingPublications(channelId);
}

function loadChannelSchedule(channelId) {
  fetchJson(`${apiBase}/api/schedules/channel/${channelId}`)
    .then(schedule => {
      dom("schedule-status").innerText = schedule.is_active ? "Programación activa" : "Programación inactiva";
      dom("schedule-status").className = schedule.is_active ? "badge-success" : "badge";
      
      // Videos largos
      dom("long-video-enabled").checked = schedule.long_video_enabled;
      dom("long-video-frequency").value = schedule.long_video_frequency;
      dom("long-video-info").innerText = schedule.long_video_enabled 
        ? `Videos largos cada ${schedule.long_video_frequency} días` 
        : "Desactivado";
      
      // Shorts
      dom("short-video-enabled").checked = schedule.short_video_enabled;
      dom("short-video-frequency").value = schedule.short_video_frequency;
      dom("short-video-info").innerText = schedule.short_video_enabled 
        ? `Shorts cada ${schedule.short_video_frequency} días` 
        : "Desactivado";
      
      // Artículos
      dom("article-enabled").checked = schedule.article_enabled;
      dom("article-frequency").value = schedule.article_frequency;
      dom("article-info").innerText = schedule.article_enabled 
        ? `Artículos cada ${schedule.article_frequency} días` 
        : "Desactivado";
      
      dom("start-date").value = schedule.start_date ? schedule.start_date.split("T")[0] : "";
    })
    .catch(err => console.error("Error cargando programación:", err));
}

function saveChannelSchedule(channelId) {
  const data = {
    long_video_enabled: dom("long-video-enabled").checked,
    long_video_frequency: parseInt(dom("long-video-frequency").value),
    short_video_enabled: dom("short-video-enabled").checked,
    short_video_frequency: parseInt(dom("short-video-frequency").value),
    article_enabled: dom("article-enabled").checked,
    article_frequency: parseInt(dom("article-frequency").value),
    start_date: dom("start-date").value + "T00:00:00",
    is_active: dom("schedule-active").checked
  };
  
  fetchJson(`${apiBase}/api/schedules/channel/${channelId}`, {
    method: "PUT",
    body: JSON.stringify(data)
  })
    .then(() => {
      alert("Programación guardada");
      loadChannelSchedule(channelId);
    })
    .catch(err => alert("Error al guardar: " + err.message));
}

function generateSchedule(channelId, year, month) {
  fetchJson(`${apiBase}/api/schedules/channel/${channelId}/generate?year=${year}&month=${month}`, {
    method: "POST"
  })
    .then(res => {
      alert(`Se crearon ${res.created} programaciones`);
      loadChannelCalendar(channelId);
    })
    .catch(err => alert("Error al generar: " + err.message));
}

function loadChannelCalendar(channelId) {
  fetchJson(`${apiBase}/api/schedules/channel/${channelId}/calendar/months`)
    .then(data => {
      renderCalendarView(channelId, data);
    })
    .catch(err => console.error("Error cargando calendario:", err));
}

function renderCalendarView(channelId, data) {
  const container = dom("channel-calendar-container");
  if (!container) return;
  
  const scheduleInfo = data.schedule_info;
  let html = '<div class="schedule-info-box">';
  
  if (scheduleInfo) {
    html += `
      <div class="flex-header" style="margin-bottom: 10px;">
        <strong>Programación actual:</strong>
        <span class="${scheduleInfo.is_active ? 'badge-success' : 'badge'}">${scheduleInfo.is_active ? 'Activa' : 'Inactiva'}</span>
      </div>
      <div class="text-small">
        ${scheduleInfo.long_video_enabled ? `🎬 Videos largos: cada ${scheduleInfo.long_video_frequency} días | ` : ''}
        ${scheduleInfo.short_video_enabled ? `📱 Shorts: cada ${scheduleInfo.short_video_frequency} días | ` : ''}
        ${scheduleInfo.article_enabled ? `📄 Artículos: cada ${scheduleInfo.article_frequency} días` : ''}
      </div>
    `;
  }
  html += '</div>';
  
  // Mes actual
  html += '<h4>📅 Mes Actual</h4>';
  html += '<div class="calendar-grid">';
  const currentMonth = data.current_month;
  const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
  html += `<div class="calendar-header">${monthNames[currentMonth.month - 1]} ${currentMonth.year}</div>`;
  
  // Días de la semana
  html += '<div class="calendar-weekdays"><div>Lu</div><div>Ma</div><div>Mi</div><div>Ju</div><div>Vu</div><div>Sá</div><div>Do</div></div>';
  
  // Eventos del mes actual
  const eventsCurrent = currentMonth.events || [];
  const daysInMonth = new Date(currentMonth.year, currentMonth.month, 0).getDate();
  const firstDay = (new Date(currentMonth.year, currentMonth.month - 1, 1).getDay() + 6) % 7;
  
  let currentDay = 1;
  for (let i = 0; i < 42; i++) {
    if (i < firstDay || currentDay > daysInMonth) {
      html += '<div class="calendar-cell empty"></div>';
    } else {
      const dayEvents = eventsCurrent.filter(e => new Date(e.date).getDate() === currentDay);
      const isToday = currentDay === new Date().getDate() && currentMonth.month === new Date().getMonth() + 1;
      
      html += `<div class="calendar-cell ${isToday ? 'today' : ''}">`;
      html += `<span class="calendar-day">${currentDay}</span>`;
      dayEvents.forEach(e => {
        const icon = e.content_type === 'long_video' ? '🎬' : e.content_type === 'short' ? '📱' : '📄';
        const statusColor = e.status === 'published' ? '#10b981' : e.status === 'cancelled' ? '#ef4444' : '#3b82f6';
        html += `<div class="calendar-event" style="background:${statusColor}; font-size: 10px;" title="${e.content_type} - ${e.notes || ''}">${icon}</div>`;
      });
      html += '</div>';
      currentDay++;
    }
  }
  html += '</div>';
  
  // Mes siguiente
  html += '<h4>📅 Mes Siguiente</h4>';
  html += '<div class="calendar-grid">';
  const nextMonth = data.next_month;
  html += `<div class="calendar-header">${monthNames[nextMonth.month - 1]} ${nextMonth.year}</div>`;
  html += '<div class="calendar-weekdays"><div>Lu</div><div>Ma</div><div>Mi</div><div>Ju</div><div>Vu</div><div>Sá</div><div>Do</div></div>';
  
  const eventsNext = nextMonth.events || [];
  const daysInNextMonth = new Date(nextMonth.year, nextMonth.month, 0).getDate();
  const firstDayNext = (new Date(nextMonth.year, nextMonth.month - 1, 1).getDay() + 6) % 7;
  
  let nextDay = 1;
  for (let i = 0; i < 42; i++) {
    if (i < firstDayNext || nextDay > daysInNextMonth) {
      html += '<div class="calendar-cell empty"></div>';
    } else {
      const dayEvents = eventsNext.filter(e => new Date(e.date).getDate() === nextDay);
      
      html += `<div class="calendar-cell">`;
      html += `<span class="calendar-day">${nextDay}</span>`;
      dayEvents.forEach(e => {
        const icon = e.content_type === 'long_video' ? '🎬' : e.content_type === 'short' ? '📱' : '📄';
        const statusColor = e.status === 'published' ? '#10b981' : e.status === 'cancelled' ? '#ef4444' : '#3b82f6';
        html += `<div class="calendar-event" style="background:${statusColor}; font-size: 10px;" title="${e.content_type}">${icon}</div>`;
      });
      html += '</div>';
      nextDay++;
    }
  }
  html += '</div>';
  
  // Botón para generar programaciones
  html += `
    <div style="margin-top: 15px;">
      <button onclick="generateSchedule(${channelId}, ${currentMonth.year}, ${currentMonth.month})" class="btn-outline">
        📅 Generar Mes Actual
      </button>
      <button onclick="generateSchedule(${channelId}, ${nextMonth.year}, ${nextMonth.month})" class="btn-outline">
        📅 Generar Mes Siguiente
      </button>
    </div>
  `;
  
  container.innerHTML = html;
}

function loadUpcomingPublications(channelId) {
  fetchJson(`${apiBase}/api/schedules/channel/${channelId}/upcoming?limit=10`)
    .then(publications => {
      const container = dom("upcoming-publications");
      if (!container) return;
      
      container.innerHTML = publications.map(p => {
        const icon = p.content_type === 'long_video' ? '🎬' : p.content_type === 'short' ? '📱' : '📄';
        return `
          <div class="item-row">
            <span>${icon} ${new Date(p.date).toLocaleDateString()}</span>
            <span class="badge">${p.content_type}</span>
            <span class="badge ${p.status === 'published' ? 'badge-success' : ''}">${p.status}</span>
            ${p.has_script ? '<span class="badge" style="background:#10b981">✓ Guión</span>' : '<span class="badge" style="background:#f59e0b">Sin guión</span>'}
          </div>
        `;
      }).join("") || "<p class='text-muted'>No hay publicaciones próximas</p>";
    })
    .catch(err => console.error("Error cargando publicaciones:", err));
}

function assignScriptToPublication(publicationId, scriptId) {
  fetchJson(`${apiBase}/api/schedules/publication/${publicationId}/assign-script?script_id=${scriptId}`, {
    method: "POST"
  })
    .then(() => {
      alert("Guión asociado correctamente");
      if (currentChannelId) loadUpcomingPublications(currentChannelId);
    })
    .catch(err => alert("Error al asociar: " + err.message));
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
