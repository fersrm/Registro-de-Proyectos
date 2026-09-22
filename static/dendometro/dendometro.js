/* Gráficos y sincronización sin exponer claves de ThingSpeak. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const csrf = () => document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  async function request(url, method = 'GET') {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 60000);
    try {
      const response = await fetch(url, {method, credentials: 'same-origin', signal: controller.signal,
        headers: {'X-CSRFToken': csrf(), 'Accept': 'application/json'}});
      if (!response.headers.get('content-type')?.includes('application/json')) {
        throw new Error('La sesión pudo haber expirado. Vuelve a iniciar sesión e intenta nuevamente.');
      }
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || body.message || 'No se pudo completar la solicitud.');
      return body;
    } catch (error) {
      if (error.name === 'AbortError') throw new Error('La consulta tardó demasiado. Puedes volver a intentar para reanudar la carga.');
      throw error;
    } finally {clearTimeout(timeout);}
  }
  function feedback(text, bad = false) {
    const el = $('d-feedback');
    if (el) {el.hidden = false; el.textContent = text; el.className = bad ? 'd-warning' : 'd-notice';}
  }
  document.querySelectorAll('[data-test-url]').forEach(button => button.addEventListener('click', async () => {
    button.disabled = true;
    feedback('Probando conexión…');
    try {const result = await request(button.dataset.testUrl, 'POST'); feedback(result.message, !result.ok);}
    catch (error) {feedback(error.message, true);}
    finally {button.disabled = false;}
  }));
  $('d-esp32-profile')?.addEventListener('click', () => {
    const values = {input_mode: 'millimeters', sensor_range_um: 11000, scale_factor: 1,
      offset_um: 0, aggregate_minutes: 30, aggregate_method: 'median', rolling_window: 3,
      trend_window_hours: 24, session_gap_minutes: 90, daily_min_coverage_hours: 12, trend_min_coverage_hours: 18};
    Object.entries(values).forEach(([key, value]) => {if ($(`id_${key}`)) $(`id_${key}`).value = value;});
    $('d-esp32-profile').textContent = 'Perfil cargado · guarda para aplicar';
  });
  document.querySelectorAll('[data-maintenance]').forEach(button => button.addEventListener('click', () => {
    const flag = $('id_sensor_in_maintenance');
    if (!flag) return;
    flag.checked = button.dataset.maintenance === 'start';
    button.textContent = flag.checked ? 'Inicio marcado · guarda para aplicar' : 'Fin marcado · guarda para aplicar';
  }));
  const monitor = $('d-monitor');
  if (!monitor) return;
  let busy = false, data = null, timer = null, requestVersion = 0, selectedSession = '', audio = null, lastSound = '', soundEnabled = false;
  const charts = {};
  const modal = $('d-loading');
  const formatter = new Intl.NumberFormat('es-CL', {maximumFractionDigits: 1, minimumFractionDigits: 1});
  const formatted = value => value == null ? '—' : formatter.format(value);
  const date = (value, compact = false) => value ? new Intl.DateTimeFormat('es-CL', {timeZone: data?.sensor.timezone || 'America/Santiago',
    day: '2-digit', month: 'short', ...(compact ? {} : {year: 'numeric'}), hour: '2-digit', minute: '2-digit', hourCycle: 'h23'}).format(new Date(value)) : 'Sin dato';
  const colors = {raw: '#8bbbe5', smooth: '#f7ac62', envelope: '#76d7a8', trend: '#ceb1ff', excluded: '#8a97a4'};
  function dataset(label, points, color, dash = []) {
    return {label, data: points, borderColor: color, backgroundColor: color, borderWidth: 1.7,
      pointRadius: points.length < 100 ? 2 : 0, pointHoverRadius: 5, borderDash: dash, spanGaps: false, tension: 0};
  }
  function chart(id, sets, unit) {
    if (typeof Chart === 'undefined') {feedback('No se pudo cargar la biblioteca de gráficos. Revisa los archivos estáticos.', true); return;}
    if (charts[id]) {charts[id].data.datasets = sets; charts[id].update('none'); return;}
    charts[id] = new Chart($(id), {type: 'line', data: {datasets: sets}, options: {
      responsive: true, maintainAspectRatio: false, animation: false, parsing: false,
      interaction: {mode: 'nearest', intersect: false},
      plugins: {legend: {labels: {color: '#dce7ef', boxWidth: 18, font: {size: 11}}},
        tooltip: {callbacks: {title: items => date(items[0]?.parsed.x), label: item => `${item.dataset.label}: ${formatted(item.parsed.y)} ${unit}`}}},
      scales: {x: {type: 'linear', grid: {color: '#ffffff0c'}, ticks: {color: '#b5c8d6', maxTicksLimit: 6, callback: value => date(value, true)}, title: {display: true, text: `Fecha y hora · ${data.sensor.timezone}`, color: '#b5c8d6'}},
        y: {grid: {color: '#ffffff10'}, ticks: {color: '#b5c8d6'}, title: {display: true, text: unit, color: '#b5c8d6'}}}
    }});
  }
  function drawHistory() {
    if (!data) return;
    const days = Number($('d-history-window').value);
    const cutoff = days ? Date.now() - days * 86400000 : -Infinity;
    const sets = data.historic.map((session, index) => {
      const series = dataset('Posición por intervalo', session.points.filter(p => Date.parse(p.created_at) >= cutoff).map(p => ({x: Date.parse(p.created_at), y: p.um / 1000})), colors.raw);
      // Una leyenda común y trazos independientes para cada sesión.
      series.label = index === 0 ? 'Posición por intervalo' : '';
      return series;
    });
    const finalSession = data.historic[data.historic.length - 1];
    const latest = finalSession?.points[finalSession.points.length - 1];
    if (latest && Date.parse(latest.created_at) >= cutoff) sets.push({...dataset('Último intervalo operativo', [{x: Date.parse(latest.created_at), y: latest.um / 1000}], colors.smooth), pointRadius: 5});
    chart('d-history-chart', sets, 'mm');
    if (charts['d-history-chart']) {
      charts['d-history-chart'].options.plugins.legend.labels.filter = item => Boolean(item.text);
      charts['d-history-chart'].update('none');
    }
  }
  function drawDetail() {
    const points = key => data.detail.map(p => ({x: Date.parse(p.created_at), y: p[key]}));
    const sets = [dataset(`Intervalos ${data.sensor.intervalo} min`, points('aggregate_relative_um'), colors.raw), dataset('Curva dendrométrica', points('relative_um'), colors.smooth)];
    if (data.sensor.show_envelope) sets.push(dataset('Máximo de la sesión', points('growth_envelope_um'), colors.envelope, [6, 4]));
    if (data.sensor.show_trend) sets.push(dataset('Tendencia lenta', points('trend_um'), colors.trend, [3, 3]));
    if (data.detail.length > 1) {
      for (const [name, threshold] of [['Umbral bajo acumulado', data.sensor.warn_low_um], ['Umbral alto acumulado', data.sensor.warn_high_um]]) {
        if (threshold) sets.push(dataset(name, [data.detail[0], data.detail[data.detail.length - 1]].map(p => ({x: Date.parse(p.created_at), y: threshold})), '#cf8f96', [2, 5]));
      }
    }
    chart('d-detail-chart', sets, 'µm');
  }
  function drawRealtime() {
    // Cortar el trazo al superar un intervalo de análisis, conservando los puntos crudos.
    const points = []; let previous = null;
    for (const row of data.realtime) {
      const x = Date.parse(row.created_at);
      if (previous != null && x - previous > data.sensor.intervalo * 60000) points.push({x: previous + 1, y: null});
      points.push({x, y: row.um}); previous = x;
    }
    const excluded = data.realtime.filter(p => p.analysis_excluded).map(p => ({x: Date.parse(p.created_at), y: p.um}));
    chart('d-realtime-chart', [dataset('Señal recibida', points, colors.raw), dataset('Mediana 1 min', data.minute_median.map(p => ({x: Date.parse(p.created_at), y: p.um})), colors.smooth), {...dataset('Excluido del análisis', excluded, colors.excluded), showLine: false, pointRadius: 3}], 'µm');
  }
  function render() {
    const m = data.metrics;
    document.querySelectorAll('[data-metric]').forEach(el => {
      const key = el.dataset.metric;
      const value = data.sensor.maintenance && key === 'latest_um' ? m.last_operational_raw_um : m[key];
      el.textContent = value == null ? '—' : `${formatted(value)} ${key === 'trend_rate_um_day' ? 'µm/día' : 'µm'}`;
    });
    $('d-last-received').textContent = date(data.last_received);
    $('d-last-valid-label').textContent = data.sensor.maintenance ? 'Última lectura operativa' : 'Último intervalo analizado';
    $('d-last-valid').textContent = date(data.sensor.maintenance ? m.last_operational_raw_timestamp : m.last_valid_timestamp);
    $('d-summary').textContent = `${data.raw_count.toLocaleString('es-CL')} lecturas guardadas en la ventana · ${m.valid_analysis_points} puntos de análisis · ${m.session_count} sesiones · última descarga: ${date(data.sensor.ultima_sincronizacion)}`;
    $('d-logical').textContent = data.logical_state;
    $('d-alert-level').textContent = m.alert_level;
    $('d-alert-message').textContent = m.alert_message;
    $('d-alert').dataset.level = m.alert_level === 'NORMAL' ? 'normal' : data.sensor.maintenance || m.alert_level === 'SIN DATOS' ? 'info' : 'warning';
    $('d-reduced').hidden = !data.reduced;
    $('d-partial').hidden = !data.partial_interval;
    const select = $('d-session'); select.replaceChildren();
    if (!data.sessions.length) select.add(new Option('Sin sesiones', ''));
    for (const s of data.sessions) select.add(new Option(`#${s.id} · ${date(s.inicio)} · ${s.puntos} puntos`, s.id, false, s.id === data.selected_session));
    const note = $('d-session-note');
    note.hidden = !data.sessions.length || data.selected_session === data.latest_session;
    note.textContent = 'Estás viendo una sesión anterior. Las tarjetas superiores corresponden a la última sesión operativa.';
    drawHistory(); drawDetail(); drawRealtime();
    if (soundEnabled && !data.sensor.maintenance && $('d-alert').dataset.level === 'warning') {
      const signature = `${m.alert_level}:${data.last_received}`;
      if (signature !== lastSound) {
        lastSound = signature;
        const osc = audio.createOscillator(), gain = audio.createGain();
        osc.connect(gain); gain.connect(audio.destination); osc.frequency.value = 660; gain.gain.value = 0.07;
        osc.start(); osc.stop(audio.currentTime + 0.3);
      }
    }
  }
  async function load() {
    const version = ++requestVersion;
    const value = await request(monitor.dataset.dataUrl + (selectedSession ? `?sesion=${selectedSession}` : ''));
    if (version !== requestVersion) return;
    data = value; render();
  }
  function schedule() {
    clearTimeout(timer);
    if ($('d-auto').checked && monitor.dataset.active === 'true') timer = setTimeout(() => synchronize(false), Math.max(15, Number(data?.sensor.refresh_seconds || monitor.dataset.refresh)) * 1000);
  }
  function progress(result) {
    $('d-progress').value = result.progreso || 0;
    $('d-progress-text').textContent = `${result.progreso || 0}% · ${result.registros || 0} registros procesados · ${result.pendientes || 0} tramos pendientes`;
  }
  async function synchronize(blocking = true) {
    if (busy) return;
    busy = true; clearTimeout(timer); $('d-sync').disabled = true;
    if (blocking) {progress({}); modal.showModal();}
    try {
      let result = await request(monitor.dataset.syncUrl, 'POST'); progress(result);
      while (result.estado === 'pendiente') {
        result = await request(`${monitor.dataset.syncUrl}${result.id}/`, 'POST'); progress(result);
        if (result.estado === 'pendiente') await new Promise(resolve => setTimeout(resolve, 250));
      }
      if (result.estado !== 'completa') throw new Error(result.error || 'La carga se interrumpió. Puedes volver a intentar.');
      await load();
      if (blocking) feedback(`✓ Carga finalizada correctamente. ${result.registros || 0} registros procesados (incluye coincidencias ya guardadas).${result.omitidos ? ` Se omitieron ${result.omitidos} entradas sin señal numérica válida.` : ''}`);
      else if ($('d-feedback').classList.contains('d-warning')) feedback('Conexión restablecida. Lecturas actualizadas.');
    } catch (error) {
      feedback(error.message + ' Se conservan los datos descargados.', true);
      try {await load();} catch (_) { /* Se conserva la gráfica anterior. */ }
    } finally {
      if (modal.open) modal.close(); busy = false; $('d-sync').disabled = monitor.dataset.active !== 'true'; schedule();
    }
  }
  modal.addEventListener('cancel', event => {if (busy) event.preventDefault();});
  window.addEventListener('beforeunload', event => {if (busy) {event.preventDefault(); event.returnValue = '';}});
  $('d-sync').addEventListener('click', () => synchronize(true));
  $('d-auto').addEventListener('change', schedule);
  $('d-sensor-picker').addEventListener('change', event => {window.location.href = event.target.value;});
  $('d-history-window').addEventListener('change', drawHistory);
  $('d-session').addEventListener('change', async event => {
    selectedSession = event.target.value;
    try {await load();} catch (error) {feedback(error.message, true);}
  });
  document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-mode]').forEach(tab => tab.setAttribute('aria-selected', String(tab === button)));
    $('d-analysis').hidden = button.dataset.mode !== 'analysis'; $('d-realtime').hidden = button.dataset.mode !== 'realtime';
    Object.values(charts).forEach(c => c.resize());
  }));
  $('d-sound').addEventListener('click', async () => {
    try {
      if (!audio) audio = new (window.AudioContext || window.webkitAudioContext)();
      await audio.resume(); soundEnabled = !soundEnabled;
      $('d-sound').textContent = soundEnabled ? 'Silenciar avisos' : 'Activar sonido';
    } catch (_) {feedback('Este navegador no permite activar el sonido.', true);}
  });
  load().catch(error => feedback(error.message, true)).finally(() => {
    if (monitor.dataset.active === 'true') synchronize(!data?.sensor.ultima_sincronizacion);
  });
})();
