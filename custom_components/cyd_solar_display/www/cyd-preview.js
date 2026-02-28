import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";
import { unsafeHTML } from "https://unpkg.com/lit-html@1.4.1/directives/unsafe-html.js?module";

class CYDPreview extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      panel: { type: Object },
      page: { type: Number },
      activeTab: { type: String },
      editConfig: { type: Object },
      _pickerSearch: { type: Object }
    };
  }

  constructor() {
    super();
    this.page = 1;
    this.activeTab = 'overview';
    this.editConfig = {};
    this._pickerSearch = {};
  }

  firstUpdated() {
    this.loadConfig();
  }

  async loadConfig() {
    if (!this.panel || !this.panel.config || !this.panel.config.entry_id) return;
    const entryId = this.panel.config.entry_id;
    try {
      const data = await this.hass.callApi('GET', `cyd_solar_display/config/${entryId}`);
      this.editConfig = data.options || {};
      this.requestUpdate();
    } catch (e) { console.error("Failed to load config", e); }
  }

  updated() {
    // Attach change listeners to selects rendered via unsafeHTML (they lose Lit event bindings)
    const root = this.shadowRoot;
    if (!root) return;
    root.querySelectorAll('select[data-key]').forEach(sel => {
      if (!sel._listenerAttached) {
        sel._listenerAttached = true;
        sel.addEventListener('change', (e) => {
          const key = e.target.getAttribute('data-key');
          if (key) this.handleSelectChange(e, key);
        });
      }
    });
  }

  async saveConfig() {
    if (!this.panel || !this.panel.config || !this.panel.config.entry_id) return;
    const entryId = this.panel.config.entry_id;
    try {
      await this.hass.callApi('POST', `cyd_solar_display/config/${entryId}`, this.editConfig);
      alert("✅ Einstellungen wurden erfolgreich gespeichert!");
    } catch (e) {
      console.error(e);
      alert("❌ Fehler beim Speichern der Einstellungen.");
    }
  }

  getEntitiesByDomain(domainPrefix) {
    if (!this.hass) return [];
    const prefixes = Array.isArray(domainPrefix) ? domainPrefix : [domainPrefix];
    return Object.keys(this.hass.states)
      .filter(entityId => prefixes.some(prefix => entityId.startsWith(prefix + '.')))
      .sort()
      .map(entityId => {
        const stateObj = this.hass.states[entityId];
        return {
          id: entityId,
          name: stateObj.attributes.friendly_name ? `${stateObj.attributes.friendly_name} (${entityId})` : entityId
        };
      });
  }

  handlePickerInput(e, name) {
    this.editConfig = { ...this.editConfig, [name]: e.detail.value };
    this.requestUpdate();
  }

  handleSelectChange(e, name) {
    this.editConfig = { ...this.editConfig, [name]: e.target.value };
    this.requestUpdate();
  }

  renderEntitySelect(configKey, domains) {
    if (!this.hass) return html`<span style="color:#888;font-size:12px">Lade...</span>`;
    const domainList = Array.isArray(domains) ? domains : [domains];
    const entities = this.getEntitiesByDomain(domainList);
    const currentVal = (this.editConfig && this.editConfig[configKey]) ? this.editConfig[configKey] : '';
    const currentEnt = entities.find(e => e.id === currentVal);
    const displayName = currentEnt ? currentEnt.name : currentVal;
    const searchTerm = (this._pickerSearch[configKey] !== undefined) ? this._pickerSearch[configKey] : null;
    const isOpen = searchTerm !== null;

    const filtered = isOpen
      ? entities.filter(e =>
        e.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        e.id.toLowerCase().includes(searchTerm.toLowerCase())
      ).slice(0, 50)
      : [];

    return html`
      <div class="entity-picker" style="position:relative;">
        <input
          type="text"
          class="picker-input"
          placeholder="${displayName || '-- Sensor wählen --'}"
          .value=${isOpen ? searchTerm : ''}
          @focus=${() => { this._pickerSearch = { ...this._pickerSearch, [configKey]: '' }; this.requestUpdate(); }}
          @input=${(e) => { this._pickerSearch = { ...this._pickerSearch, [configKey]: e.target.value }; this.requestUpdate(); }}
          @blur=${() => setTimeout(() => { const s = { ...this._pickerSearch }; delete s[configKey]; this._pickerSearch = s; this.requestUpdate(); }, 200)}
          style="background:#111;color:#fff;border:1px solid ${currentVal ? '#fdd835' : '#444'};padding:10px;border-radius:6px;font-size:0.9em;width:100%;box-sizing:border-box;cursor:text;"
        />
        ${isOpen ? html`
          <div class="picker-dropdown" style="position:absolute;z-index:100;background:#1a1a1a;border:1px solid #555;border-radius:6px;width:100%;max-height:220px;overflow-y:auto;box-shadow:0 4px 20px rgba(0,0,0,0.6);">
            ${filtered.length === 0 ? html`
              <div style="padding:10px;color:#888;font-size:0.85em;">Kein Sensor gefunden</div>
            ` : filtered.map(ent => html`
              <div
                class="picker-item"
                style="padding:10px 12px;cursor:pointer;border-bottom:1px solid #333;font-size:0.85em;color:${ent.id === currentVal ? '#fdd835' : '#eee'};"
                @mousedown=${(e) => {
        e.preventDefault();
        this.editConfig = { ...this.editConfig, [configKey]: ent.id };
        const s = { ...this._pickerSearch }; delete s[configKey]; this._pickerSearch = s;
        this.requestUpdate();
      }}
              >
                <div style="font-weight:500">${ent.name.replace(/ \(.*\)$/, '')}</div>
                <div style="color:#888;font-size:0.8em;">${ent.id}</div>
              </div>
            `)}
          </div>
        ` : ''}
        ${currentVal ? html`
          <div style="margin-top:8px;background:linear-gradient(135deg,rgba(253,216,53,0.12) 0%,rgba(253,216,53,0.05) 100%);border:1px solid rgba(253,216,53,0.4);border-radius:8px;padding:8px 12px;display:flex;align-items:center;justify-content:space-between;gap:8px;">
            <div style="display:flex;align-items:center;gap:10px;min-width:0;">
              <div style="width:10px;height:10px;border-radius:50%;background:#4caf50;box-shadow:0 0 6px #4caf50;flex-shrink:0;"></div>
              <div style="min-width:0;">
                <div style="font-size:0.9em;font-weight:600;color:#fdd835;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${currentEnt ? currentEnt.name.replace(/ \(.*\)$/, '') : currentVal}</div>
                <div style="font-size:0.72em;color:#888;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px;">${currentVal}</div>
              </div>
            </div>
            <div title="Auswahl entfernen" style="cursor:pointer;color:#888;font-size:1.1em;flex-shrink:0;padding:2px 6px;border-radius:4px;" @click=${() => { this.editConfig = { ...this.editConfig, [configKey]: '' }; this.requestUpdate(); }}>✕</div>
          </div>
        ` : ''}
      </div>
    `;
  }

  handleFormInput(e) {
    const { name, value, type, checked } = e.target;
    this.editConfig = { ...this.editConfig, [name]: type === 'checkbox' ? checked : (type === 'number' ? Number(value) : value) };
    this.requestUpdate();
  }

  getLiveValue(entityId, defaultVal) {
    if (!this.hass || !entityId || !this.hass.states[entityId]) return defaultVal;
    const state = this.hass.states[entityId].state;
    if (state === 'unavailable' || state === 'unknown') return defaultVal;
    const parsed = parseFloat(state);
    return isNaN(parsed) ? defaultVal : parsed;
  }

  render() {
    return html`
      <div class="main-wrapper">
          <div class="header-main">
            <h1>☀️ CYD Solar Display ✨</h1>
            <p class="subtitle">Live Preview & ESP32 Konfiguration</p>
          </div>

          <div class="tabs">
            <div class="tab ${this.activeTab === 'overview' ? 'active' : ''}" @click="${() => this.activeTab = 'overview'}">Dashboard</div>
            <div class="tab ${this.activeTab === 'settings' ? 'active' : ''}" @click="${() => this.activeTab = 'settings'}">Einstellungen</div>
            <div class="tab ${this.activeTab === 'info' ? 'active' : ''}" @click="${() => this.activeTab = 'info'}">Hilfe & Info</div>
          </div>

          <div class="content">
            ${this.activeTab === 'overview' ? this.renderOverview() : ''}
            ${this.activeTab === 'settings' ? this.renderSettings() : ''}
            ${this.activeTab === 'info' ? this.renderInfo() : ''}
          </div>
          
          <div style="text-align: center; margin-top: 40px; margin-bottom: 20px;">
            <span style="font-size: 10px; color: #666; text-transform: uppercase; letter-spacing: 2px;">powered by</span><br>
            <a href="https://openkairo.de" target="_blank" style="display: inline-block; margin-top: 8px; font-size: 14px; font-weight: 900; color: #fff; text-decoration: none; text-transform: uppercase; letter-spacing: 3px; border: 1px solid rgba(0, 243, 255, 0.3); padding: 8px 20px; border-radius: 6px; background: linear-gradient(90deg, rgba(0,243,255,0.05) 0%, rgba(176,38,255,0.05) 100%); box-shadow: 0 0 15px rgba(0, 243, 255, 0.15), inset 0 0 10px rgba(176, 38, 255, 0.1); text-shadow: 0 0 8px rgba(0, 243, 255, 0.6); transition: all 0.3s ease;">
              OPEN<span style="color: #00f3ff;">KAIRO</span>
            </a>
          </div>
      </div>
    `;
  }

  renderOverview() {
    const solar_w = this.getLiveValue(this.editConfig.solar_entity, 4500);
    const grid_w = this.getLiveValue(this.editConfig.grid_entity, -1200);
    const house_w = this.getLiveValue(this.editConfig.house_entity, 2800);
    const battery_w = this.getLiveValue(this.editConfig.battery_entity, 500);
    const battery_soc = this.getLiveValue(this.editConfig.battery_soc_entity, 85);

    const yield_today = this.getLiveValue(this.editConfig.yield_today_entity, 12.4);
    const yield_month = this.getLiveValue(this.editConfig.yield_month_entity, 114.2);
    const yield_year = this.getLiveValue(this.editConfig.yield_year_entity, 1054.8);
    const yield_total = this.getLiveValue(this.editConfig.yield_total_entity, 3450.5);

    const c1_n = this.editConfig.custom1_name || "Custom 1";
    const c1_v = this.getLiveValue(this.editConfig.custom1_entity, 21.5) + " °C";
    const c2_n = this.editConfig.custom2_name || "Custom 2";
    const c2_v = this.getLiveValue(this.editConfig.custom2_entity, 48.0) + " %";
    const c3_n = this.editConfig.custom3_name || "Custom 3";
    const c3_v = this.getLiveValue(this.editConfig.custom3_entity, 1120.0) + " kWh";
    const c4_n = this.editConfig.custom4_name || "Custom 4";
    const c4_v = this.getLiveValue(this.editConfig.custom4_entity, 1.0) + " bar";

    const c5_n = this.editConfig.custom5_name || "Custom 5";
    const c5_v = this.getLiveValue(this.editConfig.custom5_entity, 21.5) + " °C";
    const c6_n = this.editConfig.custom6_name || "Custom 6";
    const c6_v = this.getLiveValue(this.editConfig.custom6_entity, 48.0) + " %";
    const c7_n = this.editConfig.custom7_name || "Custom 7";
    const c7_v = this.getLiveValue(this.editConfig.custom7_entity, 1120.0) + " kWh";
    const c8_n = this.editConfig.custom8_name || "Custom 8";
    const c8_v = this.getLiveValue(this.editConfig.custom8_entity, 1.0) + " bar";

    const m1_n = this.editConfig.mining1_name || "Mining 1";
    const m1_v = this.getLiveValue(this.editConfig.mining1_entity, 120.0) + " TH/s";
    const m2_n = this.editConfig.mining2_name || "Mining 2";
    const m2_v = this.getLiveValue(this.editConfig.mining2_entity, 65.0) + " °C";
    const m3_n = this.editConfig.mining3_name || "Mining 3";
    const m3_v = this.getLiveValue(this.editConfig.mining3_entity, 3500.0) + " W";
    const m4_n = this.editConfig.mining4_name || "Mining 4";
    const m4_v = this.getLiveValue(this.editConfig.mining4_entity, 1.0) + " BTC";

    const hasPage1 = this.editConfig.enable_page1 !== false;
    const hasPage2 = this.editConfig.enable_page2 !== false;
    const hasPage3 = this.editConfig.enable_page3 !== false;
    const hasPage4 = this.editConfig.enable_page4 !== false;
    const hasPage5 = this.editConfig.enable_page5 !== false;

    const isNegative = grid_w < 0;
    const pVal = (w) => this.editConfig.show_kw ? (w / 1000).toFixed(2) : Math.round(w);
    const pUnit = this.editConfig.show_kw ? "kW" : "W";

    return html`
      <div class="card">
          <div class="cyd-info">
            <h3>CYD Display Live Preview</h3>
            <p>1:1 Simulation mit den Livedaten deines Home Assistants.</p>
          </div>
          
          <div class="cyd-container">
            <div class="cyd-frame">
              <div class="cyd-screen">
                <div class="header">
                  <span class="title">Solar Monitor</span>
                  <span class="time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                
                ${this.page === 1 ? html`
                  <div class="page page1">
                    <div class="quad-grid">
                      <div class="quad-box q-solar">
                        <div class="q-label">SOLAR</div>
                        <div class="q-value">${pVal(solar_w)}<span>${pUnit}</span></div>
                      </div>
                      <div class="quad-box q-house">
                        <div class="q-label">HAUSVERBRAUCH</div>
                        <div class="q-value">${pVal(house_w)}<span>${pUnit}</span></div>
                      </div>
                      <div class="quad-box q-batt">
                        <div class="q-label">BATTERIE</div>
                        <div class="q-batt-val">${battery_soc}%</div>
                        <div class="q-batt-bar">
                          <div style="width: ${battery_soc}%; background: ${battery_soc <= 20 ? '#ef5350' : (battery_soc <= 50 ? '#ff9800' : '#4caf50')}"></div>
                        </div>
                        <div class="q-batt-w">${pVal(battery_w)} ${pUnit}</div>
                      </div>
                      <div class="quad-box q-grid ${isNegative ? 'export' : 'import'}">
                        <div class="q-label">${isNegative ? 'EINSPEISUNG' : 'NETZBEZUG'}</div>
                        <div class="q-value">${pVal(Math.abs(grid_w))}<span>${pUnit}</span></div>
                      </div>
                    </div>
                  </div>
                ` : this.page === 2 ? html`
                  <div class="page page2">
                    <div class="stats-grid">
                      <div class="stat-item" style="border-left: 4px solid #fdd835;">
                          <div class="label" style="color: #fdd835;">Ertrag Tag</div>
                          <div class="value">${yield_today} <span>kWh</span></div>
                      </div>
                      <div class="stat-item" style="border-left: 4px solid #fdd835;">
                          <div class="label" style="color: #fdd835;">Ertrag Monat</div>
                          <div class="value">${yield_month} <span>kWh</span></div>
                      </div>
                      <div class="stat-item" style="border-left: 4px solid #fdd835;">
                          <div class="label" style="color: #fdd835;">Ertrag Jahr</div>
                          <div class="value">${yield_year} <span>kWh</span></div>
                      </div>
                      <div class="stat-item" style="border-left: 4px solid #fdd835;">
                          <div class="label" style="color: #fdd835;">Gesamtertrag</div>
                          <div class="value">${yield_total} <span>kWh</span></div>
                      </div>
                    </div>
                  </div>
                ` : this.page === 3 ? html`
                  <div class="page page3">
                    <div class="stats-grid">
                      ${this.editConfig.custom1_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #00f3ff;">
                          <div class="label" style="color: #00f3ff;">${c1_n}</div>
                          <div class="value">${c1_v}</div>
                      </div>` : ''}
                      ${this.editConfig.custom2_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #00ff73;">
                          <div class="label" style="color: #00ff73;">${c2_n}</div>
                          <div class="value">${c2_v}</div>
                      </div>` : ''}
                      ${this.editConfig.custom3_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #b026ff;">
                          <div class="label" style="color: #b026ff;">${c3_n}</div>
                          <div class="value">${c3_v}</div>
                      </div>` : ''}
                      ${this.editConfig.custom4_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #ff003c;">
                          <div class="label" style="color: #ff003c;">${c4_n}</div>
                          <div class="value">${c4_v}</div>
                      </div>` : ''}
                    </div>
                  </div>
                ` : this.page === 4 ? html`
                  <div class="page page4">
                    <div class="stats-grid">
                      ${this.editConfig.custom5_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #00f3ff;">
                          <div class="label" style="color: #00f3ff;">${c5_n}</div>
                          <div class="value">${c5_v}</div>
                      </div>` : ''}
                      ${this.editConfig.custom6_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #00ff73;">
                          <div class="label" style="color: #00ff73;">${c6_n}</div>
                          <div class="value">${c6_v}</div>
                      </div>` : ''}
                      ${this.editConfig.custom7_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #b026ff;">
                          <div class="label" style="color: #b026ff;">${c7_n}</div>
                          <div class="value">${c7_v}</div>
                      </div>` : ''}
                      ${this.editConfig.custom8_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #ff003c;">
                          <div class="label" style="color: #ff003c;">${c8_n}</div>
                          <div class="value">${c8_v}</div>
                      </div>` : ''}
                    </div>
                  </div>
                ` : html`
                  <div class="page page5">
                    <div class="stats-grid">
                      ${this.editConfig.mining1_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #ff9800;">
                          <div class="label" style="color: #ff9800;">${m1_n}</div>
                          <div class="value">${m1_v}</div>
                      </div>` : ''}
                      ${this.editConfig.mining2_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #ff9800;">
                          <div class="label" style="color: #ff9800;">${m2_n}</div>
                          <div class="value">${m2_v}</div>
                      </div>` : ''}
                      ${this.editConfig.mining3_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #ff9800;">
                          <div class="label" style="color: #ff9800;">${m3_n}</div>
                          <div class="value">${m3_v}</div>
                      </div>` : ''}
                      ${this.editConfig.mining4_entity ? html`
                      <div class="stat-item" style="border-left: 4px solid #ff9800;">
                          <div class="label" style="color: #ff9800;">${m4_n}</div>
                          <div class="value">${m4_v}</div>
                      </div>` : ''}
                    </div>
                  </div>
                `}

                <div class="footer">
                  <div class="dots">
                    ${hasPage1 ? html`<div class="dot ${this.page === 1 ? 'active' : ''}"></div>` : ''}
                    ${hasPage2 ? html`<div class="dot ${this.page === 2 ? 'active' : ''}"></div>` : ''}
                    ${hasPage3 ? html`<div class="dot ${this.page === 3 ? 'active' : ''}"></div>` : ''}
                    ${hasPage4 ? html`<div class="dot ${this.page === 4 ? 'active' : ''}"></div>` : ''}
                    ${hasPage5 ? html`<div class="dot ${this.page === 5 ? 'active' : ''}"></div>` : ''}
                  </div>
                </div>
              </div>
              <div class="cyd-controls">
                ${hasPage1 ? html`<button @click="${() => this.page = 1}">P1</button>` : ''}
                ${hasPage2 ? html`<button @click="${() => this.page = 2}">P2</button>` : ''}
                ${hasPage3 ? html`<button @click="${() => this.page = 3}">P3</button>` : ''}
                ${hasPage4 ? html`<button @click="${() => this.page = 4}">P4</button>` : ''}
                ${hasPage5 ? html`<button @click="${() => this.page = 5}">P5</button>` : ''}
              </div>
            </div>
          </div>
      </div>
    `;
  }

  renderSettings() {
    return html`
  <div class="card edit-card" >
        <h2>🛠️ Sensoren & Konfiguration</h2>
        <p style="color:#aaa; font-size:14px; margin-bottom: 25px;">Verknüpfe hier deine Home Assistant Sensoren, die auf dem ESP32 Display angezeigt werden sollen.</p>
        
        <div class="tech-box">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="color: #fdd835; margin-top: 0;">⚡ Kern-Sensoren (Live) - Seite 1</h3>
                <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; color: #fff;">
                    <input type="checkbox" name="enable_page1" .checked="${this.editConfig.enable_page1 !== false}" @change="${this.handleFormInput}" style="width: 18px; height: 18px; accent-color: #fdd835;">
                    Aktivieren
                </label>
            </div>
            
            <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; color: #fff; margin-bottom: 15px; background: rgba(255,255,255,0.05); padding: 5px 10px; border-radius: 4px; width: fit-content;">
                <input type="checkbox" name="show_kw" .checked="${this.editConfig.show_kw === true}" @change="${this.handleFormInput}" style="width: 16px; height: 16px; accent-color: #fdd835;">
                Leistung in Kilowatt (kW) anzeigen anstatt in Watt (W)
            </label>

            <div class="form-row">
                <div class="form-group flex-1">
                  <label style="display: flex; align-items: center;">
                    Solar Leistung (W)
                    <span class="tooltip" data-tooltip="Dein aktueller PV-Ertrag. Das sollte ein Sensor sein, der die momentane Leistung ausgibt (in Watt).">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z"/></svg>
                    </span>
                  </label>
                  ${this.renderEntitySelect('solar_entity', ['sensor', 'input_number'])}
                </div>
                <div class="form-group flex-1">
                  <label style="display: flex; align-items: center;">
                    Netz Leistung (W)
                    <span class="tooltip" data-tooltip="Dein Momentanverbrauch vom Stromzähler (meist in Watt). Achtung: Die Einspeisung ins Netz muss als negativer Wert vom Sensor kommen!">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z"/></svg>
                    </span>
                  </label>
                  ${this.renderEntitySelect('grid_entity', ['sensor', 'input_number'])}
                </div>
            </div>

  <div class="form-row">
    <div class="form-group flex-1">
      <label>Hausverbrauch (W)</label>
      ${this.renderEntitySelect('house_entity', ['sensor', 'input_number'])}
                </div>
  <div class="form-group flex-1">
    <label>Batterie Leistung (W)</label>
    ${this.renderEntitySelect('battery_entity', ['sensor', 'input_number'])}
                </div>
            </div>

  <div class="form-group" style="width: 50%;">
    <label>Batterie Füllstand (%)</label>
    ${this.renderEntitySelect('battery_soc_entity', ['sensor', 'input_number'])}
            </div>
        </div>

        <div class="tech-box" style="margin-top: 20px; border-color: rgba(52, 152, 219, 0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="color: #3498db; margin-top: 0;">📊 Statistik-Sensoren (kWh) - Seite 2</h3>
                <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; color: #fff;">
                    <input type="checkbox" name="enable_page2" .checked="${this.editConfig.enable_page2 !== false}" @change="${this.handleFormInput}" style="width: 18px; height: 18px; accent-color: #3498db;">
                    Aktivieren
                </label>
            </div>
            <div class="form-row">
                <div class="form-group flex-1">
                  <label>Ertrag Heute (kWh)</label>
                  ${this.renderEntitySelect('yield_today_entity', ['sensor', 'input_number'])}
                </div>
                <div class="form-group flex-1">
                  <label>Ertrag Laufender Monat (kWh)</label>
                  ${this.renderEntitySelect('yield_month_entity', ['sensor', 'input_number'])}
                </div>
            </div>
  <div class="form-row">
    <div class="form-group flex-1">
      <label>Ertrag Laufendes Jahr (kWh)</label>
      ${this.renderEntitySelect('yield_year_entity', ['sensor', 'input_number'])}
                </div>
  <div class="form-group flex-1">
    <label>Gesamtertrag (Lifelime) (kWh)</label>
    ${this.renderEntitySelect('yield_total_entity', ['sensor', 'input_number'])}
                </div>
            </div>
        </div>

  <div class="tech-box" style="margin-top: 20px; border-color: #00f3ff;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3 style="color: #00f3ff; margin-top: 0;">🔮 Eigene Sensoren (Seite 3)</h3>
      <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; color: #fff;">
          <input type="checkbox" name="enable_page3" .checked="${this.editConfig.enable_page3 !== false}" @change="${this.handleFormInput}" style="width: 18px; height: 18px; accent-color: #00f3ff;">
          Aktivieren
      </label>
    </div>
    
    ${this.editConfig.enable_page3 !== false ? html`
    <p style="color:#aaa; font-size: 12px; margin-top:-10px; margin-bottom: 15px;">Füge bis zu 4 eigene Sensoren hinzu, welche auf der dritten Seite angezeigt werden.</p>

    <div class="form-row">
      <div class="form-group flex-1">
        <label>Name 1 (z.B. Temperatur)</label>
        <input type="text" name="custom1_name" .value="${this.editConfig.custom1_name || ''}" @input="${this.handleFormInput}">
      </div>
      <div class="form-group flex-1">
        <label>Sensor 1</label>
        ${this.renderEntitySelect('custom1_entity', ['sensor', 'input_number'])}
  </div>
            </div>

  <div class="form-row">
    <div class="form-group flex-1">
      <label>Name 2 (z.B. Luftfeuchte)</label>
      <input type="text" name="custom2_name" .value="${this.editConfig.custom2_name || ''}" @input="${this.handleFormInput}">
    </div>
    <div class="form-group flex-1">
      <label>Sensor 2</label>
      ${this.renderEntitySelect('custom2_entity', ['sensor', 'input_number'])}
                </div>
            </div>

  <div class="form-row">
    <div class="form-group flex-1">
      <label>Name 3</label>
      <input type="text" name="custom3_name" .value="${this.editConfig.custom3_name || ''}" @input="${this.handleFormInput}">
    </div>
    <div class="form-group flex-1">
      <label>Sensor 3</label>
      ${this.renderEntitySelect('custom3_entity', ['sensor', 'input_number'])}
                </div>
            </div>

  <div class="form-row">
    <div class="form-group flex-1">
      <label>Name 4</label>
      <input type="text" name="custom4_name" .value="${this.editConfig.custom4_name || ''}" @input="${this.handleFormInput}">
    </div>
    <div class="form-group flex-1">
      <label>Sensor 4</label>
      ${this.renderEntitySelect('custom4_entity', ['sensor', 'input_number'])}
                </div>
            </div>
            ` : ''}
        </div>

        <div class="tech-box" style="margin-top: 20px; border-color: #fdd835;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <h3 style="color: #fdd835; margin-top: 0;">🔮 Eigene Sensoren (Seite 4)</h3>
              <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; color: #fff;">
                  <input type="checkbox" name="enable_page4" .checked="${this.editConfig.enable_page4 !== false}" @change="${this.handleFormInput}" style="width: 18px; height: 18px; accent-color: #fdd835;">
                  Aktivieren
              </label>
            </div>
            
            ${this.editConfig.enable_page4 !== false ? html`
            <div class="form-row">
              <div class="form-group flex-1">
                <label>Name 5</label>
                <input type="text" name="custom5_name" .value="${this.editConfig.custom5_name || ''}" @input="${this.handleFormInput}">
              </div>
              <div class="form-group flex-1">
                <label>Sensor 5</label>
                ${this.renderEntitySelect('custom5_entity', ['sensor', 'input_number'])}
              </div>
            </div>

            <div class="form-row">
              <div class="form-group flex-1">
                <label>Name 6</label>
                <input type="text" name="custom6_name" .value="${this.editConfig.custom6_name || ''}" @input="${this.handleFormInput}">
              </div>
              <div class="form-group flex-1">
                <label>Sensor 6</label>
                ${this.renderEntitySelect('custom6_entity', ['sensor', 'input_number'])}
              </div>
            </div>

            <div class="form-row">
              <div class="form-group flex-1">
                <label>Name 7</label>
                <input type="text" name="custom7_name" .value="${this.editConfig.custom7_name || ''}" @input="${this.handleFormInput}">
              </div>
              <div class="form-group flex-1">
                <label>Sensor 7</label>
                ${this.renderEntitySelect('custom7_entity', ['sensor', 'input_number'])}
              </div>
            </div>

            <div class="form-row">
              <div class="form-group flex-1">
                <label>Name 8</label>
                <input type="text" name="custom8_name" .value="${this.editConfig.custom8_name || ''}" @input="${this.handleFormInput}">
              </div>
              <div class="form-group flex-1">
                <label>Sensor 8</label>
                ${this.renderEntitySelect('custom8_entity', ['sensor', 'input_number'])}
              </div>
            </div>
            ` : ''}
        </div>
        
        <div class="tech-box" style="margin-top: 20px; border-color: #ff9800;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <h3 style="color: #ff9800; margin-top: 0;">⛏️ Mining Sensoren (Seite 5)</h3>
              <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; color: #fff;">
                  <input type="checkbox" name="enable_page5" .checked="${this.editConfig.enable_page5 !== false}" @change="${this.handleFormInput}" style="width: 18px; height: 18px; accent-color: #ff9800;">
                  Aktivieren
              </label>
            </div>
            
            ${this.editConfig.enable_page5 !== false ? html`
            <div class="form-row">
              <div class="form-group flex-1">
                <label>Name 1 (z.B. Hashrate)</label>
                <input type="text" name="mining1_name" .value="${this.editConfig.mining1_name || ''}" @input="${this.handleFormInput}">
              </div>
              <div class="form-group flex-1">
                <label>Sensor 1</label>
                ${this.renderEntitySelect('mining1_entity', ['sensor', 'input_number'])}
              </div>
            </div>

            <div class="form-row">
              <div class="form-group flex-1">
                <label>Name 2 (z.B. Temp)</label>
                <input type="text" name="mining2_name" .value="${this.editConfig.mining2_name || ''}" @input="${this.handleFormInput}">
              </div>
              <div class="form-group flex-1">
                <label>Sensor 2</label>
                ${this.renderEntitySelect('mining2_entity', ['sensor', 'input_number'])}
              </div>
            </div>

            <div class="form-row">
              <div class="form-group flex-1">
                <label>Name 3</label>
                <input type="text" name="mining3_name" .value="${this.editConfig.mining3_name || ''}" @input="${this.handleFormInput}">
              </div>
              <div class="form-group flex-1">
                <label>Sensor 3</label>
                ${this.renderEntitySelect('mining3_entity', ['sensor', 'input_number'])}
              </div>
            </div>

            <div class="form-row">
              <div class="form-group flex-1">
                <label>Name 4</label>
                <input type="text" name="mining4_name" .value="${this.editConfig.mining4_name || ''}" @input="${this.handleFormInput}">
              </div>
              <div class="form-group flex-1">
                <label>Sensor 4</label>
                ${this.renderEntitySelect('mining4_entity', ['sensor', 'input_number'])}
              </div>
            </div>
            ` : ''}
        </div>

        <div class="tech-box" style="margin-top: 20px; border-color: rgba(155, 89, 182, 0.4);">
            <h3 style="color: #9b59b6; margin-top: 0;">⚙️ Allgemeine Eigenschaften</h3>
            
            <!-- Seitenwechsel-Modus -->
            <div style="margin-bottom: 20px;">
              <label style="display:block; margin-bottom: 10px; font-weight: 600; color: #ccc;">Seitenwechsel-Modus</label>
              <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                ${['auto', 'touch', 'both'].map(mode => {
      const labels = {
        auto: { icon: '🔄', title: 'Automatisch', desc: 'HA wechselt Seiten nach Zeitintervall' },
        touch: { icon: '👆', title: 'Nur Touch', desc: 'Manuell durch Tippen auf das Display' },
        both: { icon: '🔄👆', title: 'Beides', desc: 'Auto + Touch-Override (empfohlen)' },
      }[mode];
      const isActive = (this.editConfig.page_switch_mode || 'auto') === mode;
      return html`
                    <div
                      @click=${() => { this.editConfig = { ...this.editConfig, page_switch_mode: mode }; this.requestUpdate(); }}
                      style="
                        flex: 1; min-width: 130px; cursor: pointer; padding: 14px 12px;
                        border-radius: 10px; border: 2px solid ${isActive ? '#9b59b6' : 'rgba(155,89,182,0.25)'};
                        background: ${isActive ? 'rgba(155,89,182,0.18)' : 'rgba(255,255,255,0.03)'};
                        transition: all 0.2s ease;
                        box-shadow: ${isActive ? '0 0 15px rgba(155,89,182,0.35)' : 'none'};
                        text-align: center;
                      "
                    >
                      <div style="font-size: 1.8em; margin-bottom: 6px;">${labels.icon}</div>
                      <div style="font-weight: 700; color: ${isActive ? '#b26ef7' : '#ddd'}; font-size: 0.95em;">${labels.title}</div>
                      <div style="font-size: 0.72em; color: #888; margin-top: 4px; line-height: 1.4;">${labels.desc}</div>
                    </div>
                  `;
    })}
              </div>
            </div>

            <div class="form-row">
                <div class="form-group flex-1">
                  <label>Update Intervall (Sekunden)</label>
                  <input type="number" name="update_interval" min="1" .value="${this.editConfig.update_interval || 5}" @input="${this.handleFormInput}">
                  <small>Wie oft sollen Daten zum ESP32 gesendet werden?</small>
                </div>
                ${(this.editConfig.page_switch_mode || 'auto') !== 'touch' ? html`
                <div class="form-group flex-1">
                  <label>Seitenwechsel Intervall (Sekunden)</label>
                  <input type="number" name="page_interval" min="5" .value="${this.editConfig.page_interval || 10}" @input="${this.handleFormInput}">
                  <small>Wie lange eine Seite auf dem LCD angezeigt wird.</small>
                </div>
                ` : html`
                <div class="form-group flex-1" style="opacity:0.4; pointer-events:none;">
                  <label>Seitenwechsel Intervall (Sekunden)</label>
                  <input type="number" value="${this.editConfig.page_interval || 10}" disabled>
                  <small>⚠️ Nicht aktiv im Touch-Modus</small>
                </div>
                `}
            </div>
        </div>

        <div class="form-actions" style="margin-top: 30px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; text-align: right;">
            <button class="btn-save" @click="${this.saveConfig}">💾 Konfiguration Speichern & Anwenden</button>
        </div>
      </div>
  `;
  }

  renderInfo() {
    return html`
  <div class="card" >
        <h2>ℹ️ Informationen & Ersteinrichtung</h2>
        <p>Willkommen beim <strong>CYD Solar Display</strong> Panel.</p>
        
        <div class="tech-box">
          <h3 style="margin-top:0; color:#F7931A;">☀️ Was ist das CYD Solar Display?</h3>
          <p style="color:#bbb; line-height:1.6; margin-top: 5px;">Dieses Projekt verbindet deinen Home Assistant mit einem <strong>ESP32 Cheap Yellow Display (CYD) 2432S028</strong>, um deine Solar-, Batterie- und Netzwerte hochauflösend und in Echtzeit in deinem Wohnraum zu visualisieren.</p>
        </div>

        <div class="tech-box" style="margin-top: 15px;">
          <h3 style="margin-top:0; color:#4fc3f7;">🚀 Einrichtung</h3>
          <ul style="color:#bbb; line-height:1.6; padding-left:20px;">
            <li><strong style="color:#ddd;">1. Hardware:</strong> Du benötigst das fertig geflashte ESP32 CYD (Modell 2432S028).
              <div style="margin: 12px 0 15px 0;">
                <a href="https://solarmodule-gladbeck.de/produkt/ok_display/" target="_blank" style="display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #00f3ff 0%, #0084ff 100%); color: #000; padding: 12px 22px; border-radius: 8px; text-decoration: none; font-size: 15px; font-weight: 900; box-shadow: 0 4px 20px rgba(0, 243, 255, 0.4); transition: transform 0.2s, box-shadow 0.2s; text-transform: uppercase; letter-spacing: 0.5px;" onmouseover="this.style.transform='scale(1.03)'; this.style.boxShadow='0 6px 25px rgba(0, 243, 255, 0.6)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 20px rgba(0, 243, 255, 0.4)';">
                  <svg viewBox="0 0 24 24" width="22" height="22" style="margin-right: 10px; fill: #000;"><path d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z"/></svg>
                  Hardware fertig geflasht kaufen (Plug & Play)
                </a>
              </div>
            </li>
            <li><strong style="color:#ddd;">2. WLAN & mDNS:</strong> Das Display verbindet sich mit deinem Netzwerk. Home Assistant sollte es automatisch über mDNS finden.</li>
            <li><strong style="color:#ddd;">3. Konfiguration:</strong> Sobald der ESP32 in HA als Gerät "cyd_solar_display" registriert ist, verknüpfe unter "Einstellungen" (in diesem Panel) deine Sensoren.</li>
            <li><strong style="color:#ddd;">4. Optionen:</strong> Aktiviere oder deaktiviere einzelne Seiten (z.B. Mining Sensoren) oder die kW-Anzeige ganz nach deinem Geschmack.</li>
            <li><strong style="color:#ddd;">5. Automatisierung:</strong> Das System arbeitet passiv. Die ausgewählten Sensordaten werden nun vom Panel aus im Intervall (z.B. 5s) intelligent an das Display gepusht! Viel Spaß.</li>
          </ul>
        </div>

        <div class="tech-box faq-box" style="margin-top: 15px; border-color: rgba(255, 152, 0, 0.3);">
          <h3 style="margin-top:0; color:#ff9800;">❓ Häufige Fragen (FAQ)</h3>
          
          <details class="faq-item">
            <summary>Mein Display wird nicht von Home Assistant (mDNS) gefunden, was tun?</summary>
            <div class="faq-content">
              Prüfe, ob du beim Setup im WLAN-Portal des Displays dein richtiges 2,4 GHz WLAN und Passwort eingegeben hast. Manchmal blockieren Router mDNS (Bonjour). In diesem Fall kannst du die IP-Adresse des Displays in deinem Router auslesen und manuell über "Integration hinzufügen -> ESPHome" in Home Assistant eintragen.
            </div>
          </details>
          
          <details class="faq-item" open>
            <summary>Meine Sensoren auf dem Display zeigen nur 0 an</summary>
            <div class="faq-content">
              Stelle sicher, dass du unter "Einstellungen" (in diesem Panel) Sensoren ausgewählt und gespeichert hast. Es dauert nach dem Speichern bis zu 10 Sekunden (je nach eingestelltem Update Intervall), bis der ESP32 die ersten neuen Werte empfängt.
            </div>
          </details>

          <details class="faq-item">
            <summary>Was ist der Unterschied zwischen Watt (W) und Kilowatt (kW)?</summary>
            <div class="faq-content">
              Wähle als Sensoren nach Möglichkeit immer die <strong>Watt-Werte</strong> aus deinem System. Wenn dir die angezeigten Zahlen auf dem Display zu groß sind, setze den Haken bei "Leistung in Kilowatt (kW) anzeigen". Das Display konvertiert die originalen Watt-Werte dann für dich automatisch auf dem Bildschirm in kW (z.B. 2400W -> 2.4kW).
            </div>
          </details>

          <details class="faq-item">
            <summary>Wie funktioniert der Touch-Seitenwechsel?</summary>
            <div class="faq-content">
              Das CYD-Display hat einen eingebauten Touchscreen. Tippe <strong>irgendwo auf das Display</strong>, um zur nächsten Seite zu wechseln. Der Wechsel erfolgt sofort – du musst nicht auf eine bestimmte Stelle tippen. Im Footer des Displays erscheint kurz ein <strong style="color:#fdd835;">[&gt;</strong> Symbol in Gelb, das bestätigt, dass dein Touch erkannt wurde.
            </div>
          </details>

          <details class="faq-item">
            <summary>Was ist der Seitenwechsel-Modus "Beides" – und warum ist er empfohlen?</summary>
            <div class="faq-content">
              Im Modus <strong>"Beides"</strong> läuft der automatische Seitenwechsel wie gewohnt. Wenn du aber den Bildschirm antippst, übernimmt der ESP32 für ca. <strong>30 Sekunden</strong> die Kontrolle – HA pausiert in dieser Zeit die Rotation. Danach kehrt der automatische Wechsel zurück.<br><br>
              Das ist ideal, wenn du zwischendurch schnell eine bestimmte Seite prüfen möchtest, ohne den Automodus dauerhaft zu deaktivieren.
            </div>
          </details>
        </div>

        <!-- SEITENWECHSEL-MODUS ERKLAERUNG -->
        <div class="tech-box" style="margin-top: 15px; border-color: rgba(155, 89, 182, 0.4);">
          <h3 style="margin-top:0; color:#9b59b6;">🔄👆 Seitenwechsel-Modi im Überblick</h3>
          <p style="color:#bbb; font-size:14px; margin-bottom: 18px; line-height:1.6;">
            Du kannst unter <strong>Einstellungen → Allgemeine Eigenschaften</strong> wählen, wie das Display zwischen den Seiten wechselt.
          </p>

          <!-- Modus-Karten -->
          <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px;">
            <div style="flex:1; min-width:160px; background:rgba(255,255,255,0.04); border:1px solid rgba(155,89,182,0.3); border-radius:10px; padding:16px;">
              <div style="font-size:2em; text-align:center; margin-bottom:8px;">🔄</div>
              <div style="font-weight:700; color:#b26ef7; text-align:center; margin-bottom:8px;">Automatisch</div>
              <ul style="color:#bbb; font-size:0.82em; line-height:1.7; padding-left:16px; margin:0;">
                <li>Home Assistant wechselt Seiten nach dem eingestellten Zeitintervall</li>
                <li>Touch am Display hat <strong style="color:#fff;">keinen Effekt</strong></li>
                <li>Ideal für reine Schau-Displays</li>
              </ul>
            </div>
            <div style="flex:1; min-width:160px; background:rgba(255,255,255,0.04); border:1px solid rgba(155,89,182,0.3); border-radius:10px; padding:16px;">
              <div style="font-size:2em; text-align:center; margin-bottom:8px;">👆</div>
              <div style="font-weight:700; color:#b26ef7; text-align:center; margin-bottom:8px;">Nur Touch</div>
              <ul style="color:#bbb; font-size:0.82em; line-height:1.7; padding-left:16px; margin:0;">
                <li>Seiten wechseln <strong style="color:#fff;">nur</strong> durch Tippen auf das Display</li>
                <li>Kein automatischer Wechsel</li>
                <li>Das Intervall-Feld wird ignoriert</li>
                <li>Ideal wenn du selbst bestimmst, was angezeigt wird</li>
              </ul>
            </div>
            <div style="flex:1; min-width:160px; background:rgba(155,89,182,0.12); border:2px solid rgba(155,89,182,0.5); border-radius:10px; padding:16px; position:relative;">
              <div style="position:absolute; top:-10px; right:12px; background:#9b59b6; color:#fff; font-size:0.65em; font-weight:700; padding:2px 8px; border-radius:10px; letter-spacing:1px;">EMPFOHLEN</div>
              <div style="font-size:2em; text-align:center; margin-bottom:8px;">🔄👆</div>
              <div style="font-weight:700; color:#b26ef7; text-align:center; margin-bottom:8px;">Beides</div>
              <ul style="color:#bbb; font-size:0.82em; line-height:1.7; padding-left:16px; margin:0;">
                <li>Auto-Rotation läuft wie normal</li>
                <li>Tippen stoppt Auto für <strong style="color:#fff;">~30 Sek.</strong></li>
                <li>Danach kehrt Auto automatisch zurück</li>
                <li>Bestes aus beiden Welten ✨</li>
              </ul>
            </div>
          </div>

          <!-- Visueller Footer-Indikator -->
          <div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:14px 16px; border:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:0.85em; font-weight:600; color:#ccc; margin-bottom:10px;">📺 Anzeige auf dem Display (Footer)</div>
            <div style="display:flex; gap:16px; flex-wrap:wrap;">
              <div style="display:flex; align-items:center; gap:10px;">
                <div style="background:#111; border:1px solid #333; border-radius:6px; padding:4px 10px; font-family:monospace; font-size:0.9em; color:#fdd835;">[&gt;</div>
                <span style="color:#888; font-size:0.82em;">Gelb = Touch-Override aktiv (du hast gerade getippt)</span>
              </div>
              <div style="display:flex; align-items:center; gap:10px;">
                <div style="background:#111; border:1px solid #333; border-radius:6px; padding:4px 10px; font-family:monospace; font-size:0.9em; color:#aaa;">[&gt;</div>
                <span style="color:#888; font-size:0.82em;">Weiß/Grau = HA steuert automatisch</span>
              </div>
              <div style="display:flex; align-items:center; gap:10px;">
                <div style="background:#111; border:1px solid #333; border-radius:6px; padding:4px 10px; font-family:monospace; font-size:0.9em; color:#fdd835;">&lt; &gt;</div>
                <span style="color:#888; font-size:0.82em;">Blinkt kurz auf bei jedem Touch</span>
              </div>
            </div>
          </div>
        </div>

        <div class="tech-box" style="margin-top: 15px; border-color: rgba(0, 168, 255, 0.3); background: rgba(0, 69, 124, 0.1);">
          <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
            <div style="flex: 1; min-width: 300px;">
              <h3 style="margin-top:0; color:#00a8ff;">☕ Support & Spenden</h3>
              <p style="color:#bbb; line-height:1.6; margin-top: 5px;">Dir gefällt das Projekt und du möchtest die Weiterentwicklung unterstützen? Ich freue mich riesig über jeden noch so kleinen Betrag für die nächste Tasse Kaffee!</p>
              <p style="color:#888; font-size: 12px; margin-top: 5px;">📧 info@low-streaming.de</p>
            </div>
            <div>
              <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=info@low-streaming.de&currency_code=EUR" target="_blank" style="display: inline-flex; align-items: center; justify-content: center; background: #00457C; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-size: 16px; font-weight: bold; border: 1px solid #00569c; box-shadow: 0 4px 15px rgba(0, 69, 124, 0.4); transition: transform 0.2s, background 0.2s;">
                <svg viewBox="0 0 24 24" width="22" height="22" style="margin-right: 10px; fill: white;"><path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944.901C5.026.382 5.474 0 5.998 0h7.46c2.57 0 4.578.543 5.69 1.81 1.01 1.15 1.304 2.42 1.012 4.287-.023.143-.047.288-.077.437-.983 5.05-4.349 6.797-8.647 6.797h-2.19c-.524 0-.968.382-1.05.9l-1.12 7.106zm14.146-14.42a3.35 3.35 0 0 0-.607-.541c-.013.076-.026.175-.041.254-.93 4.778-4.005 7.201-9.138 7.201h-2.19a2.058 2.058 0 0 0-2.029 1.737l-1.36 8.617h3.336c.451 0 .835-.333.905-.78l.412-2.613a1.144 1.144 0 0 1 1.128-.964h.473c4.14 0 7.37-1.554 8.24-6.024.34-1.748.156-3.136-.5-4.102-.271-.4-.68-.847-1.164-1.298l.535-1.487z"/></svg>
                Spenden via PayPal
              </a>
            </div>
          </div>
        </div>
      </div>
  `;
  }

  static get styles() {
    return css`
      :host {
  display: block;
  color: #e1e1e1;
  font-family: 'Roboto', 'Inter', sans-serif;
  background-color: #0d0d12;
  background-image: 
    radial-gradient(circle at 15% 0%, rgba(90, 40, 120, 0.35) 0%, transparent 50%),
    radial-gradient(circle at 85% 100%, rgba(20, 130, 140, 0.25) 0%, transparent 50%);
  background-attachment: fixed;
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}
      
      .main-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

      .header-main {
  text-align: center;
  margin-bottom: 30px;
}
      .header-main h1 {
  margin: 0;
  font-size: 2.5em;
  color: #fff;
  text-shadow: 0 0 20px rgba(253, 216, 53, 0.4);
}
      .header-main.subtitle {
  color: #888;
  font-size: 1.1em;
  margin: 5px 0 0;
}

      /* TABS */
      .tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #333;
  padding-bottom: 10px;
}
      .tab {
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  background: #222;
  color: #aaa;
  font-weight: 600;
  transition: all 0.2s ease-in-out;
}
      .tab:hover {
  background: #333;
  color: #fff;
}
      .tab.active {
  background: #fdd835;
  color: #000;
  box-shadow: 0 4px 15px rgba(253, 216, 53, 0.3);
}

      .card {
  background: rgba(26, 26, 28, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255,255,255,0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
      
      .card h2 {
  margin-top: 0;
  color: #fff;
}

      /* CYD PREVIEW LAYOUT */
      .cyd-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
      .cyd-frame {
  width: 340px;
  height: 260px;
  background: #2b2b2b;
  border-radius: 12px;
  padding: 10px;
  position: relative;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 1), 0 10px 30px rgba(0, 0, 0, 0.5);
  border: 2px solid #444;
}
      .cyd-screen {
  width: 320px;
  height: 240px;
  background: #000;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}
      .header {
  display: flex;
  justify-content: space-between;
  padding: 5px 10px;
  font-size: 10px;
  background: #222;
  color: #aaa;
}
      .footer {
  position: absolute;
  bottom: 5px;
  width: 100%;
  display: flex;
  justify-content: center;
}
      .dots { display: flex; gap: 5px; }
      .dot { width: 4px; height: 4px; border-radius: 50%; background: #555; }
      .dot.active { background: #fdd835; }

      .page { flex: 1; padding: 10px; display: flex; flex-direction: column; }
      
      .quad-grid {
        display: grid;
        grid-template-columns: 145px 145px;
        grid-template-rows: 80px 80px;
        gap: 10px;
        justify-content: center;
        align-content: center;
      }
      .quad-box {
        background: #111;
        border-radius: 4px;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
      }
      .quad-box.q-solar { border-left: 4px solid #fdd835; color: #fdd835; }
      .quad-box.q-house { border-left: 4px solid #4fc3f7; color: #4fc3f7; }
      .quad-box.q-batt { border-left: 4px solid #4caf50; color: #4caf50; }
      .quad-box.q-grid.export { border-left: 4px solid #66bb6a; color: #66bb6a; }
      .quad-box.q-grid.import { border-left: 4px solid #ef5350; color: #ef5350; }
      
      .q-label {
        position: absolute;
        top: 6px;
        left: 8px;
        font-size: 8px;
        font-weight: bold;
        letter-spacing: 0.5px;
      }
      .q-value {
        font-size: 20px;
        font-weight: bold;
        color: #fff;
        margin-top: 5px;
        line-height: 1.2;
      }
      .q-value span { font-size: 10px; margin-left: 2px; }
      
      .q-batt-val { font-size: 20px; font-weight: bold; color: #fff; margin-top: 10px; line-height: 1; }
      .q-batt-bar {
        width: 75px;
        height: 10px;
        border: 1px solid #777;
        margin-top: 5px;
        padding: 1px;
        border-radius: 2px;
      }
      .q-batt-bar div { height: 100%; border-radius: 1px; }
      .q-batt-w {
        position: absolute;
        bottom: 8px;
        left: 65px;
        font-size: 10px;
        color: #fff;
      }

      .stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  height: 100%;
}
      .stat-item {
  background: #111;
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border: 1px solid #333;
}
      .stat-item .label { font-size: 10px; color: #888; text-transform: uppercase; }
      .stat-item .value { font-size: 20px; font-weight: bold; line-height: 1.2; margin-top: 5px; }
      .stat-item .value span { font-size: 10px; margin-left: 2px; }
      
      .cyd-controls {
  position: absolute;
  right: -55px;
  top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
      .cyd-controls button {
  background: #444;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}
      .cyd-controls button:hover { background: #555; }
      
      .cyd-info { margin-bottom: 25px; text-align: center; color: #aaa; }
      .cyd-info h3 { margin: 0; color: #4fc3f7; font-size: 16px; }
      .cyd-info p { margin: 5px 0 0; font-size: 12px; }

      /* FORMS & SETTINGS */
      .tech-box {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #333;
  border-radius: 10px;
  padding: 20px;
}
      .form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}
      .flex-1 { flex: 1; }
      
      .form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}
      .form-group label {
  font-size: 0.9em;
  color: #bbb;
  margin-bottom: 6px;
  font-weight: 500;
}
      .form-group select, .form-group input[type="text"], .form-group input[type="number"], .entity-select {
  background: #111;
  color: #fff;
  border: 1px solid #444;
  padding: 10px;
  border-radius: 6px;
  font-size: 1em;
  outline: none;
  width: 100%;
  box-sizing: border-box;
}
      .form-group select:focus, .form-group input:focus {
  border-color: #fdd835;
}
      .form-group small {
  color: #aaa;
  margin-top: 5px;
  font-size: 0.85em;
}

      .btn-save {
  background: #4caf50;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}
      .btn-save:hover {
  background: #43a047;
}

      /* TOOLTIPS */
      .tooltip {
        position: relative;
        display: inline-flex;
        align-items: center;
        margin-left: 6px;
        color: #888;
        cursor: help;
        vertical-align: middle;
      }
      .tooltip:hover {
        color: #4fc3f7;
      }
      .tooltip::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(20, 20, 25, 0.98);
        color: #fff;
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: normal;
        white-space: pre-wrap;
        width: max-content;
        max-width: 280px;
        text-align: center;
        border: 1px solid rgba(79, 195, 247, 0.4);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.8);
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Bouncy pop-in */
        z-index: 100;
        pointer-events: none;
      }
      .tooltip:hover::after {
        opacity: 1;
        visibility: visible;
        bottom: 140%;
      }

      /* FAQ ACCORDION */
      .faq-item {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        margin-bottom: 10px;
        overflow: hidden;
      }
      .faq-item summary {
        padding: 12px 15px;
        cursor: pointer;
        font-weight: 500;
        color: #ddd;
        outline: none;
        transition: background 0.2s;
        display: flex;
        justify-content: space-between;
        align-items: center;
        list-style: none; /* Hide default arrow */
      }
      .faq-item summary::-webkit-details-marker {
        display: none;
      }
      .faq-item summary::after {
        content: '▼';
        font-size: 10px;
        color: #888;
        transition: transform 0.2s;
      }
      .faq-item[open] summary::after {
        transform: rotate(180deg);
        color: #ff9800;
      }
      .faq-item summary:hover {
        background: rgba(255, 255, 255, 0.05);
      }
      .faq-content {
        padding: 15px;
        color: #bbb;
        font-size: 14px;
        line-height: 1.5;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        background: rgba(0, 0, 0, 0.2);
      }
`;
  }
}

customElements.define("cyd-preview", CYDPreview);

