class HomeBatteryControlPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  connectedCallback() {
    this.render();
  }

  render() {
    if (!this._hass) {
      this.innerHTML = `<ha-card><div class="card-content">Loading Home Battery Control...</div></ha-card>`;
      return;
    }

    this.innerHTML = `
      <ha-card>
        <div class="card-content">
          <h2>Home Battery Control</h2>
          <p>Bundled HACS dashboard panel.</p>
          <p>Sections: Setup, Overview, Strategies, PID, Charge/Sell, Timed/Dynamic, Batteries, Advanced, Diagnostics.</p>
          <p>Use integration entities for all controls. Full control remains safety-gated.</p>
        </div>
      </ha-card>`;
  }
}

customElements.define("home-battery-control-panel", HomeBatteryControlPanel);

window.customPanel = {
  type: "home-battery-control-panel",
  name: "home-battery-control-panel",
};
