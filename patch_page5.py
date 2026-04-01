with open('custom_components/cyd_solar_display/www/cyd-preview.js', 'r', encoding='utf-8') as f:
    code = f.read()

page5_block = '''
          <div class="tech-box" style="margin-top: 20px; border-color: #fdd835;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="color: #fdd835; margin-top: 0;">⛏️ Mining Sensoren (Seite 5)</h3>
                <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; color: #fff;">
                  <input type="checkbox" name="enable_page5" .checked="${this.editConfig.enable_page5 !== false}" @change="${this.handleFormInput}" style="width: 18px; height: 18px; accent-color: #fdd835;">
                  Aktivieren
                </label>
              </div>
              ${this.editConfig.enable_page5 !== false ? html`
              <div class="form-row">
                <div class="form-group flex-1">
                  <label>Name 1</label>
                  <input type="text" name="mining1_name" .value="${this.editConfig.mining1_name || ''}" @input="${this.handleFormInput}">
                </div>
                <div class="form-group flex-1">
                  <label>Sensor 1</label>
                  ${this.renderEntitySelect('mining1_entity', ['sensor', 'input_number'])}
                </div>
              </div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label>Name 2</label>
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
'''

target_str = '<div class="tab-content" id="tab-ota">'
if target_str in code and "Mining Sensoren" not in code:
    code = code.replace(target_str, page5_block + '\n        ' + target_str)
    with open('custom_components/cyd_solar_display/www/cyd-preview.js', 'w', encoding='utf-8') as f:
        f.write(code)
    print('Patched correctly!')
else:
    print('Already patched or not found.')
