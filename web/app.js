const $ = (selector) => document.querySelector(selector);
let mode = 'integrated', report = null, batchReport = null;
let busy = false;
const money = (value) => new Intl.NumberFormat('en-TZ', {maximumFractionDigits: 0}).format(value);
const titles = {integrated: 'The whole farm. One assessment.', credit: 'Understand the financial picture.', yield: 'Explore your next harvest.', batch: 'One portfolio. A wider perspective.', about: 'A clear view behind every result.'};
const message = (text = '') => { $('#message').textContent = text; $('#message').hidden = !text; };
function clearResults() { $('#results').hidden = true; report = null; }
function updateRange(input) {
  const output = document.querySelector(`output[for="${input.id}"]`);
  output.replaceChildren(document.createTextNode(input.value + ' '));
  const unit = document.createElement('small'); unit.textContent = input.dataset.unit; output.append(unit);
}
document.querySelectorAll('input[type=range]').forEach(input => input.addEventListener('input', () => updateRange(input)));
document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => {
  if (busy) return;
  mode = button.dataset.mode;
  document.querySelectorAll('[data-mode]').forEach(item => { item.classList.toggle('active', item === button); item.setAttribute('aria-pressed', String(item === button)); });
  $('#page-title').textContent = titles[mode];
  $('#page-caption').textContent = mode.toUpperCase() + ' / FARMER INTELLIGENCE';
  $('#assessment').hidden = ['batch', 'about'].includes(mode);
  $('#batch').hidden = mode !== 'batch'; $('#about').hidden = mode !== 'about';
  $('#conditions-panel').hidden = mode === 'credit';
  // Farm size is shared with yield, so keep its field available in that view.
  $('#profile-panel').querySelectorAll('label').forEach(label => {
    const field = label.querySelector('input,select');
    const hide = mode === 'yield' && field.name !== 'farm_size_hectares';
    label.hidden = hide; field.disabled = hide;
  });
  $('#conditions-panel').querySelectorAll('input').forEach(input => { input.disabled = mode === 'credit'; });
  $('#analyze').innerHTML = `${mode === 'yield' ? 'Estimate yield' : mode === 'credit' ? 'Score farmer' : 'Run assessment'} <span>↗</span>`;
  message(); clearResults();
}));
async function request(path, body, contentType = 'application/json') {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120000);
  try {
    const response = await fetch(path, {method: 'POST', headers: {'Content-Type': contentType}, body, signal: controller.signal});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The request could not be completed.');
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('The request timed out. Please try a smaller batch or check the server.');
    if (error instanceof TypeError) throw new Error('Cannot reach the prediction server. Start python web_app.py and try again.');
    throw error;
  } finally { clearTimeout(timeout); }
}
function setBusy(value) {
  busy = value;
  document.querySelectorAll('button,input,select').forEach(element => {
    if (value) { element.dataset.wasDisabled = String(element.disabled); element.disabled = true; }
    else element.disabled = element.dataset.wasDisabled === 'true';
  });
}
function metric(label, value, unit) {
  const card = document.createElement('article'); card.className = 'glass metric';
  for (const [tag, text] of [['p', label], ['strong', value], ['small', unit]]) { const element = document.createElement(tag); element.textContent = text; card.append(element); }
  return card;
}
$('#farmer-form').addEventListener('input', () => { clearResults(); message(); });
$('#farmer-form').addEventListener('reset', () => { clearResults(); message(); setTimeout(() => document.querySelectorAll('input[type=range]').forEach(updateRange), 0); });
$('#farmer-form').addEventListener('submit', async event => {
  event.preventDefault(); if (busy) return;
  const inputs = Object.fromEntries(new FormData(event.currentTarget));
  clearResults(); setBusy(true); message('Analyzing your farm…');
  try {
    const result = await request('/api/' + mode, JSON.stringify(inputs));
    report = {mode, inputs, result, created_at: new Date().toISOString()};
    $('#result-context').textContent = `${inputs.farmer_id || 'Farm'} · ${inputs.region || 'Yield estimate'} · ${inputs.farm_size_hectares} hectares`;
    const cards = [];
    if (mode !== 'credit') cards.push(metric('Estimated yield', result.predicted_yield.toFixed(2), 'tonnes / hectare · formula estimate'), metric('Estimated gross income', money(result.farm_income), 'TZS / harvest'));
    if (mode !== 'yield') cards.push(metric('Probability of default', result.pd_pct.toFixed(1) + '%', result.risk_category.replaceAll('_', ' ') + ' RISK'));
    if (mode === 'integrated') cards.push(metric('Recommended loan', money(result.recommended_loan), 'TZS · subject to review'));
    if (mode === 'credit') cards.push(metric('Expected loss', money(result.expected_loss), 'TZS · 45% loss given default'), metric('Risk category', result.risk_category.replaceAll('_', ' '), 'model classification'), metric('Requested loan', money(+inputs.loan_amount_requested), 'TZS'));
    if (mode === 'yield') cards.push(metric('Total production', result.production.toFixed(2), 'tonnes / harvest'), metric('Repayment capacity', money(result.repayment_capacity), 'TZS · 35% of gross income'));
    $('#metrics').replaceChildren(...cards);
    const box = $('#recommendation'); box.replaceChildren(); box.hidden = mode !== 'integrated';
    if (mode === 'integrated') {
      const heading = document.createElement('h3'); heading.textContent = result.decision;
      const detail = document.createElement('p'); detail.textContent = `Indicative collateral: TZS ${money(result.collateral)}. Estimated repayment capacity: TZS ${money(result.repayment_capacity)}.`;
      box.append(heading, detail);
    }
    message(); $('#results').hidden = false; $('#results').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'nearest'});
  } catch (error) { message(error.message); }
  finally { setBusy(false); }
});
function download(text, name, type) {
  const url = URL.createObjectURL(new Blob([text], {type})); const link = document.createElement('a');
  link.href = url; link.download = name; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
$('#download').addEventListener('click', () => { if (report) download(JSON.stringify(report, null, 2), 'farm-assessment.json', 'application/json'); });
$('#template').addEventListener('click', () => download('region,coop_member,farm_size_hectares,primary_crop,mobile_money_inflow,subsidy_status,loan_amount_requested\nDodoma,Yes,5,Maize,500000,Pending,2000000\n', 'farmer-template.csv', 'text/csv'));
$('#csv-file').addEventListener('change', () => { $('#batch-results').replaceChildren(); batchReport = null; message(); });
$('#batch-form').addEventListener('submit', async event => {
  event.preventDefault(); if (busy) return;
  const file = $('#csv-file').files[0]; if (!file) return;
  if (file.size > 2000000) { message('Please upload a CSV smaller than 2 MB.'); return; }
  $('#batch-results').replaceChildren(); batchReport = null; setBusy(true); message('Scoring your portfolio…');
  try {
    const data = await request('/api/batch', await file.text(), 'text/csv'); batchReport = data.results;
    const valid = data.results.filter(row => !row.error).length;
    message(`${valid} farmers scored; ${data.results.length - valid} rows need correction. CSV row numbers include the header.`);
    const wrap = document.createElement('div'); wrap.className = 'table-wrap';
    const table = document.createElement('table'); const head = table.createTHead().insertRow();
    ['CSV row', 'Default probability', 'Risk category', 'Expected loss (TZS)', 'Issue'].forEach(label => { const th = document.createElement('th'); th.textContent = label; head.append(th); });
    const body = table.createTBody();
    data.results.forEach(row => { const tr = body.insertRow(); [row.row, row.error ? '—' : row.pd_pct.toFixed(1) + '%', row.risk_category || '—', row.error ? '—' : money(row.expected_loss), row.error || '—'].forEach(value => { tr.insertCell().textContent = value; }); });
    wrap.append(table); const save = document.createElement('button'); save.type = 'button'; save.className = 'reset'; save.textContent = '↓ Download scores';
    save.addEventListener('click', () => {
      const columns = ['row', 'pd_pct', 'risk_category', 'expected_loss', 'error'];
      const csv = [columns.join(','), ...batchReport.map(row => columns.map(key => '"' + String(row[key] ?? '').replaceAll('"', '""') + '"').join(','))].join('\n');
      download(csv, 'batch-scores.csv', 'text/csv');
    }); $('#batch-results').append(wrap, save);
  } catch (error) { message(error.message); }
  finally { setBusy(false); }
});
fetch('/api/health').then(async response => { const data = await response.json(); $('#model-status').textContent = data.ready ? 'Credit model connected' : 'Credit model unavailable'; $('#model-status').classList.toggle('ready', data.ready); }).catch(() => { $('#model-status').textContent = 'Server offline'; });
