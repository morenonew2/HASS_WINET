/* WINET card - nessuna dipendenza esterna.
 * Servita e registrata automaticamente dall'integrazione WINET.
 *
 * Uso minimo:
 *   type: custom:winet-card
 *   entity: climate.winet            # opzionale: se manca usa la prima stufa WINET
 *
 * Opzioni:
 *   name: Stufa                      # titolo
 *   show_water: true|false           # forza/nasconde la temperatura acqua
 *   confirm: true|false              # conferma prima di accendere/spegnere (default true)
 *   entities:                        # solo se servisse forzare un'entita'
 *     status: sensor.xxx
 */
(() => {
  const IMG = "/winet_static/img/";
  const STATUS_IMG = {
    off: "stove_off.png",
    on: "stove_on.png",
    flame_wait: "stove_on.png",
    standby: "stove_on.png",
    final_cleaning: "stove_final.png",
    brazier_cleaning: "stove_final.png",
    alarm: "stove_alarm.png",
    unmanaged: "stove_unmanaged.png",
    unknown: "stove_unknown.png",
  };
  const TEXT = {
    it: { room: "Ambiente", target: "Impostata", power: "Potenza", flue: "Fumi", water: "Acqua", rpm: "Estrattore", on: "Accendi", off: "Spegni", confirm: "Procedo?", missing: "Nessuna stufa WINET trovata" },
    en: { room: "Room", target: "Target", power: "Power", flue: "Flue", water: "Water", rpm: "Extractor", on: "Turn on", off: "Turn off", confirm: "Proceed?", missing: "No WINET stove found" },
  };

  class WinetCard extends HTMLElement {
    static getStubConfig(hass) {
      const ents = hass.entities || {};
      const id = Object.keys(ents).find((e) => e.startsWith("climate.") && ents[e].platform === "winet");
      return { entity: id || "" };
    }

    setConfig(config) {
      this._config = config || {};
      this._map = null;
      this._built = false;
    }

    getCardSize() {
      return 6;
    }

    set hass(hass) {
      this._hass = hass;
      if (!this._config) return;
      if (!this._map) this._map = this._resolve();
      if (!this._built) this._build();
      this._update();
    }

    _t(key) {
      const lang = (this._hass.language || "en").slice(0, 2);
      return (TEXT[lang] || TEXT.en)[key];
    }

    _resolve() {
      const h = this._hass;
      const ents = h.entities || {};
      const map = { ...(this._config.entities || {}) };
      let deviceId = this._config.entity && ents[this._config.entity] && ents[this._config.entity].device_id;
      if (!deviceId) {
        const climate = Object.keys(ents).find((e) => e.startsWith("climate.") && ents[e].platform === "winet");
        deviceId = climate && ents[climate].device_id;
      }
      if (!deviceId) return map;
      for (const [id, e] of Object.entries(ents)) {
        if (e.device_id === deviceId && e.platform === "winet" && e.translation_key && !map[e.translation_key]) {
          map[e.translation_key] = id;
        }
      }
      return map;
    }

    _st(role) {
      const id = this._map[role];
      return id ? this._hass.states[id] : undefined;
    }

    _num(stateObj) {
      if (!stateObj) return null;
      const n = parseFloat(stateObj.state);
      return Number.isFinite(n) ? n : null;
    }

    _build() {
      this._built = true;
      if (!this._root) this._root = this.attachShadow({ mode: "open" });
      this._root.innerHTML = `
        <style>
          ha-card { padding: 16px; }
          .title { font-size: 1.2em; font-weight: 500; margin-bottom: 8px; }
          .top { display: flex; gap: 16px; align-items: center; }
          .img { flex: 0 0 38%; max-width: 160px; }
          .img img { width: 100%; display: block; border-radius: 8px; }
          .info { flex: 1; text-align: center; }
          .status { font-weight: 500; margin-bottom: 4px; }
          .status.alarm { color: var(--error-color, #db4437); }
          .big { font-size: 2.6em; line-height: 1.1; cursor: pointer; }
          .sub { color: var(--secondary-text-color); font-size: .85em; }
          .row { display: flex; align-items: center; justify-content: space-between; margin-top: 14px; }
          .lbl { color: var(--secondary-text-color); }
          .ctl { display: flex; align-items: center; gap: 10px; }
          .val { min-width: 3.5em; text-align: center; font-size: 1.3em; font-weight: 500; cursor: pointer; }
          button { all: unset; cursor: pointer; width: 38px; height: 38px; border-radius: 50%; text-align: center;
                   background: var(--secondary-background-color); color: var(--primary-text-color); display: flex;
                   align-items: center; justify-content: center; }
          button:active { filter: brightness(.85); }
          button:disabled { opacity: .4; cursor: default; }
          .stats { display: flex; justify-content: space-around; margin-top: 14px; flex-wrap: wrap; gap: 8px; }
          .stat { text-align: center; cursor: pointer; }
          .stat b { display: block; font-size: 1.1em; }
          .pwr { width: 100%; margin-top: 16px; height: 44px; border-radius: 22px; background: var(--primary-color);
                 color: var(--text-primary-color, #fff); font-weight: 500; gap: 8px; }
          .pwr.is-on { background: var(--error-color, #db4437); }
          .msg { padding: 16px; text-align: center; color: var(--secondary-text-color); }
        </style>
        <ha-card>
          <div class="msg" id="msg" hidden></div>
          <div id="main">
            <div class="title" id="title"></div>
            <div class="top">
              <div class="img"><img id="img" alt=""></div>
              <div class="info">
                <div class="status" id="status"></div>
                <div class="big" id="air"></div>
                <div class="sub" id="airlbl"></div>
              </div>
            </div>
            <div class="row"><span class="lbl" id="tlbl"></span>
              <span class="ctl"><button id="tm"><ha-icon icon="mdi:minus"></ha-icon></button>
              <span class="val" id="tval"></span>
              <button id="tp"><ha-icon icon="mdi:plus"></ha-icon></button></span></div>
            <div class="row"><span class="lbl" id="plbl"></span>
              <span class="ctl"><button id="pm"><ha-icon icon="mdi:minus"></ha-icon></button>
              <span class="val" id="pval"></span>
              <button id="pp"><ha-icon icon="mdi:plus"></ha-icon></button></span></div>
            <div class="stats" id="stats"></div>
            <button class="pwr" id="pwr"><ha-icon icon="mdi:power"></ha-icon><span id="pwrtxt"></span></button>
          </div>
        </ha-card>`;
      const $ = (id) => this._root.getElementById(id);
      this._el = {};
      ["msg", "main", "title", "img", "status", "air", "airlbl", "tlbl", "tval", "tm", "tp", "plbl", "pval", "pm", "pp", "stats", "pwr", "pwrtxt"].forEach((i) => (this._el[i] = $(i)));
      this._el.tm.onclick = () => this._bump("temp", -1);
      this._el.tp.onclick = () => this._bump("temp", 1);
      this._el.pm.onclick = () => this._bump("power", -1);
      this._el.pp.onclick = () => this._bump("power", 1);
      this._el.air.onclick = () => this._more("air_temp");
      this._el.tval.onclick = () => this._more("air_setpoint");
      this._el.pval.onclick = () => this._more("power");
      this._el.status.onclick = () => this._more("status");
      this._el.pwr.onclick = () => this._toggle();
    }

    _more(role) {
      const entityId = this._map[role];
      if (entityId) this.dispatchEvent(new CustomEvent("hass-more-info", { detail: { entityId }, bubbles: true, composed: true }));
    }

    _toggle() {
      const id = this._map.power_switch;
      if (!id) return;
      const on = this._hass.states[id]?.state === "on";
      if (this._config.confirm !== false && !window.confirm(`${this._t(on ? "off" : "on")}? ${this._t("confirm")}`)) return;
      this._hass.callService("switch", on ? "turn_off" : "turn_on", { entity_id: id });
    }

    // Modifica con anteprima immediata e invio ritardato (si possono premere piu' volte + / -)
    _bump(kind, delta) {
      this._pending = this._pending || {};
      const clim = this._st("stove");
      const powerNum = this._st("power_level");
      let current;
      let min;
      let max;
      let step;
      if (kind === "temp") {
        if (!clim) return;
        current = this._pending.temp ?? clim.attributes.temperature;
        min = clim.attributes.min_temp ?? 10;
        max = clim.attributes.max_temp ?? 40;
        step = clim.attributes.target_temp_step ?? 1;
      } else {
        if (!powerNum) return;
        current = this._pending.power ?? this._num(powerNum) ?? 1;
        min = powerNum.attributes.min ?? 1;
        max = powerNum.attributes.max ?? 4;
        step = powerNum.attributes.step ?? 1;
      }
      const value = Math.min(max, Math.max(min, Number(current) + delta * step));
      this._pending[kind] = value;
      this._update();
      clearTimeout(this._timers?.[kind]);
      this._timers = this._timers || {};
      this._timers[kind] = setTimeout(() => {
        if (kind === "temp") this._hass.callService("climate", "set_temperature", { entity_id: this._map.stove, temperature: value });
        else this._hass.callService("number", "set_value", { entity_id: this._map.power_level, value });
        setTimeout(() => { delete this._pending[kind]; this._update(); }, 4000);
      }, 700);
    }

    _fmt(stateObj, fallbackUnit) {
      if (!stateObj || ["unknown", "unavailable"].includes(stateObj.state)) return "—";
      if (this._hass.formatEntityState) return this._hass.formatEntityState(stateObj);
      return `${stateObj.state}${fallbackUnit ? " " + fallbackUnit : ""}`;
    }

    _update() {
      if (!this._el) return;
      const m = this._map || {};
      if (!m.stove && !m.status) {
        this._el.msg.hidden = false;
        this._el.main.hidden = true;
        this._el.msg.textContent = this._t("missing");
        return;
      }
      this._el.msg.hidden = true;
      this._el.main.hidden = false;

      const status = this._st("status");
      const code = status ? status.state : "unknown";
      this._el.title.textContent = this._config.name || (this._st("stove")?.attributes.friendly_name) || "WINET";
      this._el.title.hidden = false;
      this._el.img.src = IMG + (STATUS_IMG[code] || STATUS_IMG.unknown);
      this._el.status.textContent = this._fmt(status);
      this._el.status.className = "status" + (code === "alarm" ? " alarm" : "");

      const air = this._st("air_temp");
      this._el.air.textContent = air ? this._fmt(air, "°C") : "—";
      this._el.airlbl.textContent = this._t("room");

      const clim = this._st("stove");
      const target = this._pending?.temp ?? clim?.attributes.temperature ?? this._num(this._st("air_setpoint"));
      this._el.tlbl.textContent = this._t("target");
      this._el.tval.textContent = target == null ? "—" : `${target} °C`;
      this._el.tm.disabled = this._el.tp.disabled = !clim;

      const power = this._pending?.power ?? this._num(this._st("power_level")) ?? this._num(this._st("power"));
      this._el.plbl.textContent = this._t("power");
      this._el.pval.textContent = power == null ? "—" : String(power);
      this._el.pm.disabled = this._el.pp.disabled = !this._st("power_level");

      const stats = [];
      const add = (label, role, unit) => {
        const s = this._st(role);
        if (s && !["unknown", "unavailable"].includes(s.state)) stats.push({ label, role, text: this._fmt(s, unit) });
      };
      add(this._t("flue"), "flue_temp", "°C");
      if (this._config.show_water !== false) add(this._t("water"), "water_temp", "°C");
      add(this._t("rpm"), "extractor_rpm", "rpm");
      this._el.stats.replaceChildren(
        ...stats.map((s) => {
          const d = document.createElement("div");
          d.className = "stat";
          const b = document.createElement("b");
          b.textContent = s.text;
          d.append(b, s.label);
          d.onclick = () => this._more(s.role);
          return d;
        })
      );

      const sw = this._st("power_switch");
      const isOn = sw?.state === "on";
      this._el.pwr.hidden = !sw;
      this._el.pwr.classList.toggle("is-on", isOn);
      this._el.pwrtxt.textContent = this._t(isOn ? "off" : "on");
    }
  }

  if (!customElements.get("winet-card")) customElements.define("winet-card", WinetCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "winet-card",
    name: "WINET",
    description: "Scheda per stufe WINET / Stufasmart, senza dipendenze",
  });
})();
