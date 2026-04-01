import logging
import json
import asyncio
from datetime import timedelta, datetime
import aiohttp

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_SOLAR_ENTITY,
    CONF_GRID_ENTITY,
    CONF_HOUSE_ENTITY,
    CONF_BATTERY_ENTITY,
    CONF_BATTERY_SOC_ENTITY,
    CONF_YIELD_TODAY_ENTITY,
    CONF_YIELD_MONTH_ENTITY,
    CONF_YIELD_YEAR_ENTITY,
    CONF_YIELD_TOTAL_ENTITY,
    CONF_GRID_IMPORT_ENTITY,
    CONF_GRID_EXPORT_ENTITY,
    CONF_CUSTOM1_NAME,
    CONF_CUSTOM1_ENTITY,
    CONF_CUSTOM2_NAME,
    CONF_CUSTOM2_ENTITY,
    CONF_ENABLE_PAGE3,
    CONF_CUSTOM3_NAME,
    CONF_CUSTOM3_ENTITY,
    CONF_CUSTOM4_NAME,
    CONF_CUSTOM4_ENTITY,
    CONF_ENABLE_PAGE4,
    CONF_CUSTOM5_NAME,
    CONF_CUSTOM5_ENTITY,
    CONF_CUSTOM6_NAME,
    CONF_CUSTOM6_ENTITY,
    CONF_CUSTOM7_NAME,
    CONF_CUSTOM7_ENTITY,
    CONF_CUSTOM8_NAME,
    CONF_CUSTOM8_ENTITY,
    CONF_ENABLE_PAGE1,
    CONF_ENABLE_PAGE2,
    CONF_ENABLE_PAGE5,
    CONF_MINING1_NAME,
    CONF_MINING1_ENTITY,
    CONF_MINING2_NAME,
    CONF_MINING2_ENTITY,
    CONF_MINING3_NAME,
    CONF_MINING3_ENTITY,
    CONF_MINING4_NAME,
    CONF_MINING4_ENTITY,
    CONF_ENABLE_PAGE6,
    CONF_CUSTOM9_NAME,
    CONF_CUSTOM9_ENTITY,
    CONF_CUSTOM10_NAME,
    CONF_CUSTOM10_ENTITY,
    CONF_CUSTOM11_NAME,
    CONF_CUSTOM11_ENTITY,
    CONF_CUSTOM12_NAME,
    CONF_CUSTOM12_ENTITY,
    CONF_ENABLE_PAGE7,
    CONF_CUSTOM13_NAME,
    CONF_CUSTOM13_ENTITY,
    CONF_CUSTOM14_NAME,
    CONF_CUSTOM14_ENTITY,
    CONF_CUSTOM15_NAME,
    CONF_CUSTOM15_ENTITY,
    CONF_CUSTOM16_NAME,
    CONF_CUSTOM16_ENTITY,
    CONF_ENABLE_PAGE8,
    CONF_CUSTOM17_NAME,
    CONF_CUSTOM17_ENTITY,
    CONF_CUSTOM18_NAME,
    CONF_CUSTOM18_ENTITY,
    CONF_CUSTOM19_NAME,
    CONF_CUSTOM19_ENTITY,
    CONF_CUSTOM20_NAME,
    CONF_CUSTOM20_ENTITY,
    CONF_ENABLE_PAGE9,
    CONF_CUSTOM21_NAME,
    CONF_CUSTOM21_ENTITY,
    CONF_CUSTOM22_NAME,
    CONF_CUSTOM22_ENTITY,
    CONF_CUSTOM23_NAME,
    CONF_CUSTOM23_ENTITY,
    CONF_CUSTOM24_NAME,
    CONF_CUSTOM24_ENTITY,
    CONF_SHOW_KW,
    CONF_AUTO_PAGE_SWITCH,
    CONF_PAGE_INTERVAL,
    CONF_PAGE_SWITCH_MODE,
    CONF_PAGE_ROTATION_SOURCE,
    CONF_BROADCAST_MODE,
    PAGE_SWITCH_AUTO,
    PAGE_SWITCH_TOUCH,
    PAGE_SWITCH_BOTH,
)

_LOGGER = logging.getLogger(__name__)

class CYDSolarCoordinator(DataUpdateCoordinator):
    """Coordinator to manage solar data and push to CYD."""

    def __init__(self, hass, entry):
        """Initialize."""
        self.entry = entry
        self.last_page_switch = datetime.now()
        self.latest_version = "0.0.0"
        self.last_version_check = None
        self.version_url = "https://raw.githubusercontent.com/low-streaming/cyd_solar_display/main/version.txt"
        
        # Restore last page from options
        self.current_page = entry.options.get("last_page", 1)
        
        update_interval = entry.options.get("update_interval", 5)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=int(entry.options.get("update_interval", 5))),
        )
        
        # VERY IMPORTANT: DataUpdateCoordinator stops polling natively if there are no listeners.
        # Since this integration only PUSHES data to ESPHome and has no HA entities, we must attach
        # a dummy listener so it runs forever in the background.
        self._unsub_dummy = self.async_add_listener(self._dummy_listener)

    def _dummy_listener(self):
        """Dummy listener to keep DataUpdateCoordinator polling active."""
        pass

    async def _async_update_data(self):
        """Fetch data from entities and push to ESP32."""
        data = {}
        
        def get_value(entity_id):
            if not entity_id:
                return None
            state = self.hass.states.get(entity_id)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                return None
            try:
                return round(float(state.state), 1)
            except (ValueError, TypeError):
                return None

        # --- Discover ESPHome Entity ---
        esphome_update_id = None
        ota_service_name = None
        installed_ver = "1.2.7"
        
        target_host = self.entry.data.get(CONF_HOST)
        _LOGGER.debug("Suche nach ESPHome-Gerät für Host %s", target_host)

        # 1. Finde den Config Entry von ESPHome für diese IP
        esphome_entry = next((e for e in self.hass.config_entries.async_entries("esphome") if e.data.get("host") == target_host), None)
        
        if esphome_entry:
            device_name = esphome_entry.title.lower().replace(" ", "_").replace("-", "_")
            ota_service_name = f"{device_name}_trigger_ota_update"
            _LOGGER.debug("ESPHome Eintrag gefunden: %s, Dienst: %s", esphome_entry.title, ota_service_name)
            
            # 2. Durchsuche alle Entitäten nach einer Update-Entität für diesen Eintrag
            from homeassistant.helpers import entity_registry as er
            ent_reg = er.async_get(self.hass)
            
            for entity in er.async_entries_for_config_entry(ent_reg, esphome_entry.entry_id):
                if entity.domain == "update":
                    esphome_update_id = entity.entity_id
                    _LOGGER.info("Gefundene Ziel-Entität für Updates: %s", esphome_update_id)
                    
                    state = self.hass.states.get(esphome_update_id)
                    if state:
                        installed_ver = state.attributes.get("installed_version", "1.2.7")
                    break
        else:
            _LOGGER.warning("Kein ESPHome-Gerät für Host %s gefunden. Update-Funktion eingeschränkt.", target_host)

        # --- Version Check Logic ---
        await self.async_check_version()
        # ---------------------------

        data = {
            "latest_version": self.latest_version,
            "installed_version": installed_ver,
            "firmware_update_entity_id": f"update.{self.entry.entry_id}_update",
            "esphome_update_entity": esphome_update_id,
            "ota_service": ota_service_name
        }
        def get_custom_val(entity_id):
            if not entity_id:
                return ""
            state = self.hass.states.get(entity_id)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                return "--"
            val = state.state
            try:
                fval = float(val)
                if fval.is_integer():
                    val = f"{int(fval)}"
                else:
                    val = f"{round(fval, 2)}"
            except ValueError:
                pass
            unit = state.attributes.get("unit_of_measurement", "")
            return f"{val} {unit}".strip()

        # Gather data
        payload = {
            "solar_w": get_value(self.entry.options.get(CONF_SOLAR_ENTITY)),
            "grid_w": get_value(self.entry.options.get(CONF_GRID_ENTITY)),
            "house_w": get_value(self.entry.options.get(CONF_HOUSE_ENTITY)),
            "battery_w": get_value(self.entry.options.get(CONF_BATTERY_ENTITY)),
            "battery_soc": get_value(self.entry.options.get(CONF_BATTERY_SOC_ENTITY)),
            "yield_today_kwh": get_value(self.entry.options.get(CONF_YIELD_TODAY_ENTITY)),
            "yield_month_kwh": get_value(self.entry.options.get(CONF_YIELD_MONTH_ENTITY)),
            "yield_year_kwh": get_value(self.entry.options.get(CONF_YIELD_YEAR_ENTITY)),
            "yield_total_kwh": get_value(self.entry.options.get(CONF_YIELD_TOTAL_ENTITY)),
            "grid_import_kwh": get_value(self.entry.options.get(CONF_GRID_IMPORT_ENTITY)),
            "grid_export_kwh": get_value(self.entry.options.get(CONF_GRID_EXPORT_ENTITY)),
            "timestamp": datetime.now().isoformat(),
            
            "c1_n": self.entry.options.get(CONF_CUSTOM1_NAME, "Custom 1"),
            "c1_v": get_custom_val(self.entry.options.get(CONF_CUSTOM1_ENTITY)),
            "c2_n": self.entry.options.get(CONF_CUSTOM2_NAME, "Custom 2"),
            "c2_v": get_custom_val(self.entry.options.get(CONF_CUSTOM2_ENTITY)),
            "c3_n": self.entry.options.get(CONF_CUSTOM3_NAME, "Custom 3"),
            "c3_v": get_custom_val(self.entry.options.get(CONF_CUSTOM3_ENTITY)),
            "c4_n": self.entry.options.get(CONF_CUSTOM4_NAME, "Custom 4"),
            "c4_v": get_custom_val(self.entry.options.get(CONF_CUSTOM4_ENTITY)),
            
            "c5_n": self.entry.options.get(CONF_CUSTOM5_NAME, "Custom 5"),
            "c5_v": get_custom_val(self.entry.options.get(CONF_CUSTOM5_ENTITY)),
            "c6_n": self.entry.options.get(CONF_CUSTOM6_NAME, "Custom 6"),
            "c6_v": get_custom_val(self.entry.options.get(CONF_CUSTOM6_ENTITY)),
            "c7_n": self.entry.options.get(CONF_CUSTOM7_NAME, "Custom 7"),
            "c7_v": get_custom_val(self.entry.options.get(CONF_CUSTOM7_ENTITY)),
            "c8_n": self.entry.options.get(CONF_CUSTOM8_NAME, "Custom 8"),
            "c8_v": get_custom_val(self.entry.options.get(CONF_CUSTOM8_ENTITY)),
            
            "c9_n": self.entry.options.get(CONF_MINING1_NAME, "Mining 1"),
            "c9_v": get_custom_val(self.entry.options.get(CONF_MINING1_ENTITY)),
            "c10_n": self.entry.options.get(CONF_MINING2_NAME, "Mining 2"),
            "c10_v": get_custom_val(self.entry.options.get(CONF_MINING2_ENTITY)),
            "c11_n": self.entry.options.get(CONF_MINING3_NAME, "Mining 3"),
            "c11_v": get_custom_val(self.entry.options.get(CONF_MINING3_ENTITY)),
            "c12_n": self.entry.options.get(CONF_MINING4_NAME, "Mining 4"),
            "c12_v": get_custom_val(self.entry.options.get(CONF_MINING4_ENTITY)),

            "c13_n": self.entry.options.get(CONF_CUSTOM9_NAME, "Custom 9"),
            "c13_v": get_custom_val(self.entry.options.get(CONF_CUSTOM9_ENTITY)),
            "c14_n": self.entry.options.get(CONF_CUSTOM10_NAME, "Custom 10"),
            "c14_v": get_custom_val(self.entry.options.get(CONF_CUSTOM10_ENTITY)),
            "c15_n": self.entry.options.get(CONF_CUSTOM11_NAME, "Custom 11"),
            "c15_v": get_custom_val(self.entry.options.get(CONF_CUSTOM11_ENTITY)),
            "c16_n": self.entry.options.get(CONF_CUSTOM12_NAME, "Custom 12"),
            "c16_v": get_custom_val(self.entry.options.get(CONF_CUSTOM12_ENTITY)),

            "c17_n": self.entry.options.get(CONF_CUSTOM13_NAME, "Custom 13"),
            "c17_v": get_custom_val(self.entry.options.get(CONF_CUSTOM13_ENTITY)),
            "c18_n": self.entry.options.get(CONF_CUSTOM14_NAME, "Custom 14"),
            "c18_v": get_custom_val(self.entry.options.get(CONF_CUSTOM14_ENTITY)),
            "c19_n": self.entry.options.get(CONF_CUSTOM15_NAME, "Custom 15"),
            "c19_v": get_custom_val(self.entry.options.get(CONF_CUSTOM15_ENTITY)),
            "c20_n": self.entry.options.get(CONF_CUSTOM16_NAME, "Custom 16"),
            "c20_v": get_custom_val(self.entry.options.get(CONF_CUSTOM16_ENTITY)),

            "c21_n": self.entry.options.get(CONF_CUSTOM17_NAME, "Custom 17"),
            "c21_v": get_custom_val(self.entry.options.get(CONF_CUSTOM17_ENTITY)),
            "c22_n": self.entry.options.get(CONF_CUSTOM18_NAME, "Custom 18"),
            "c22_v": get_custom_val(self.entry.options.get(CONF_CUSTOM18_ENTITY)),
            "c23_n": self.entry.options.get(CONF_CUSTOM19_NAME, "Custom 19"),
            "c23_v": get_custom_val(self.entry.options.get(CONF_CUSTOM19_ENTITY)),
            "c24_n": self.entry.options.get(CONF_CUSTOM20_NAME, "Custom 20"),
            "c24_v": get_custom_val(self.entry.options.get(CONF_CUSTOM20_ENTITY)),

            "c25_n": self.entry.options.get(CONF_CUSTOM21_NAME, "Custom 21"),
            "c25_v": get_custom_val(self.entry.options.get(CONF_CUSTOM21_ENTITY)),
            "c26_n": self.entry.options.get(CONF_CUSTOM22_NAME, "Custom 22"),
            "c26_v": get_custom_val(self.entry.options.get(CONF_CUSTOM22_ENTITY)),
            "c27_n": self.entry.options.get(CONF_CUSTOM23_NAME, "Custom 23"),
            "c27_v": get_custom_val(self.entry.options.get(CONF_CUSTOM23_ENTITY)),
            "c28_n": self.entry.options.get(CONF_CUSTOM24_NAME, "Custom 24"),
            "c28_v": get_custom_val(self.entry.options.get(CONF_CUSTOM24_ENTITY)),
        }

        # Handle Page Switching
        enable_p1 = self.entry.options.get(CONF_ENABLE_PAGE1, True)
        enable_p2 = self.entry.options.get(CONF_ENABLE_PAGE2, True)
        enable_p3 = self.entry.options.get(CONF_ENABLE_PAGE3, True)
        enable_p4 = self.entry.options.get(CONF_ENABLE_PAGE4, True)
        enable_p5 = self.entry.options.get(CONF_ENABLE_PAGE5, True)
        enable_p6 = self.entry.options.get(CONF_ENABLE_PAGE6, False)
        enable_p7 = self.entry.options.get(CONF_ENABLE_PAGE7, False)
        enable_p8 = self.entry.options.get(CONF_ENABLE_PAGE8, False)
        enable_p9 = self.entry.options.get(CONF_ENABLE_PAGE9, False)
        
        enabled_pages = []
        if enable_p1: enabled_pages.append(1)
        if enable_p2: enabled_pages.append(2)
        if enable_p3: enabled_pages.append(3)
        if enable_p4: enabled_pages.append(4)
        if enable_p5: enabled_pages.append(5)
        if enable_p6: enabled_pages.append(6)
        if enable_p7: enabled_pages.append(7)
        if enable_p8: enabled_pages.append(8)
        if enable_p9: enabled_pages.append(9)
        
        if not enabled_pages: enabled_pages = [1]
        
        # Seitenwechsel-Modus auslesen
        switch_mode = self.entry.options.get(CONF_PAGE_SWITCH_MODE, PAGE_SWITCH_AUTO)
        rotation_source = self.entry.options.get(CONF_PAGE_ROTATION_SOURCE, "ha")
        
        try:
            interval = int(self.entry.options.get("page_interval", 10))
        except (ValueError, TypeError):
            interval = 10
        
        # Ensure our current page is valid
        # Ensure our current page is valid, and handle first-boot injection
        if self.current_page not in enabled_pages:
            self.current_page = enabled_pages[0]
            
        if switch_mode == PAGE_SWITCH_TOUCH:
            # Nur Touch-Modus: HA rotiert nicht automatisch.
            # Wenn die Seite noch nicht gesetzt wurde, nimm die erste.
            if self.current_page is None:
                self.current_page = enabled_pages[0]
            self.last_page_switch = datetime.now()  # Intervall-Timer zuruecksetzen
        elif rotation_source == "ha":
            # Auto oder Both, und HA ist Master: HA rotiert Seiten nach Intervall
            # Check if first launch OR time has passed
            time_since = (datetime.now() - self.last_page_switch).total_seconds()
            
            if time_since >= interval:
                idx = enabled_pages.index(self.current_page)
                self.current_page = enabled_pages[(idx + 1) % len(enabled_pages)]
                self.last_page_switch = datetime.now()
                
                # Persist page in options
                if self.entry.options.get("last_page") != self.current_page:
                    new_options = dict(self.entry.options)
                    new_options["last_page"] = self.current_page
                    new_options["_last_sync"] = datetime.now().timestamp() # Trigger update
                    self.hass.config_entries.async_update_entry(self.entry, options=new_options)
            
        page_idx = enabled_pages.index(self.current_page) + 1
        page_total = len(enabled_pages)
        
        # Data for Service Call
        service_data = {
            "solar": float(payload["solar_w"] or 0.0),
            "grid": float(payload["grid_w"] or 0.0),
            "house": float(payload["house_w"] or 0.0),
            "bat_w": float(payload["battery_w"] or 0.0),
            "bat_soc": float(payload["battery_soc"] or 0.0),
            "val_yield": float(payload["yield_today_kwh"] or 0.0),
            "val_yield_month": float(payload["yield_month_kwh"] or 0.0),
            "val_yield_year": float(payload["yield_year_kwh"] or 0.0),
            "val_yield_total": float(payload["yield_total_kwh"] or 0.0),
            "grid_in": float(payload["grid_import_kwh"] or 0.0),
            "grid_out": float(payload["grid_export_kwh"] or 0.0),
            "page_num": int(self.current_page),
            "auto_rotate": bool(rotation_source == "display" and switch_mode != PAGE_SWITCH_TOUCH),
            "page_idx": int(page_idx),
            "page_total": int(page_total),
            "show_kw": bool(self.entry.options.get(CONF_SHOW_KW, False)),
            "c1_n": str(payload["c1_n"] or " "),
            "c1_v": str(payload["c1_v"] or " "),
            "c2_n": str(payload["c2_n"] or " "),
            "c2_v": str(payload["c2_v"] or " "),
            "c3_n": str(payload["c3_n"] or " "),
            "c3_v": str(payload["c3_v"] or " "),
            "c4_n": str(payload["c4_n"] or " "),
            "c4_v": str(payload["c4_v"] or " "),
            "c5_n": str(payload["c5_n"] or " "),
            "c5_v": str(payload["c5_v"] or " "),
            "c6_n": str(payload["c6_n"] or " "),
            "c6_v": str(payload["c6_v"] or " "),
            "c7_n": str(payload["c7_n"] or " "),
            "c7_v": str(payload["c7_v"] or " "),
            "c8_n": str(payload["c8_n"] or " "),
            "c8_v": str(payload["c8_v"] or " "),
            "c9_n": str(payload["c9_n"] or " "),
            "c9_v": str(payload["c9_v"] or " "),
            "c10_n": str(payload["c10_n"] or " "),
            "c10_v": str(payload["c10_v"] or " "),
            "c11_n": str(payload["c11_n"] or " "),
            "c11_v": str(payload["c11_v"] or " "),
            "c12_n": str(payload["c12_n"] or " "),
            "c12_v": str(payload["c12_v"] or " "),
            "c13_n": str(payload["c13_n"] or " "),
            "c13_v": str(payload["c13_v"] or " "),
            "c14_n": str(payload["c14_n"] or " "),
            "c14_v": str(payload["c14_v"] or " "),
            "c15_n": str(payload["c15_n"] or " "),
            "c15_v": str(payload["c15_v"] or " "),
            "c16_n": str(payload["c16_n"] or " "),
            "c16_v": str(payload["c16_v"] or " "),
            "c17_n": str(payload["c17_n"] or " "),
            "c17_v": str(payload["c17_v"] or " "),
            "c18_n": str(payload["c18_n"] or " "),
            "c18_v": str(payload["c18_v"] or " "),
            "c19_n": str(payload["c19_n"] or " "),
            "c19_v": str(payload["c19_v"] or " "),
            "c20_n": str(payload["c20_n"] or " "),
            "c20_v": str(payload["c20_v"] or " "),
            "c21_n": str(payload["c21_n"] or " "),
            "c21_v": str(payload["c21_v"] or " "),
            "c22_n": str(payload["c22_n"] or " "),
            "c22_v": str(payload["c22_v"] or " "),
            "c23_n": str(payload["c23_n"] or " "),
            "c23_v": str(payload["c23_v"] or " "),
            "c24_n": str(payload["c24_n"] or " "),
            "c24_v": str(payload["c24_v"] or " "),
            "c25_n": str(payload["c25_n"] or " "),
            "c25_v": str(payload["c25_v"] or " "),
            "c26_n": str(payload["c26_n"] or " "),
            "c26_v": str(payload["c26_v"] or " "),
            "c27_n": str(payload["c27_n"] or " "),
            "c27_v": str(payload["c27_v"] or " "),
            "c28_n": str(payload["c28_n"] or " "),
            "c28_v": str(payload["c28_v"] or " "),
            "dim_start": int(self.entry.options.get("dim_start_time", 22)),
            "dim_end": int(self.entry.options.get("dim_end_time", 6)),
            "dim_brt": float(self.entry.options.get("dim_brightness", 20.0)),
            "p1_en": bool(enable_p1),
            "p2_en": bool(enable_p2),
            "p3_en": bool(enable_p3),
            "p4_en": bool(enable_p4),
            "p5_en": bool(enable_p5),
            "p6_en": bool(enable_p6),
            "p7_en": bool(enable_p7),
            "p8_en": bool(enable_p8),
            "p9_en": bool(enable_p9),
        }
        
        # Call the ESPHome Service(s)
        all_services = self.hass.services.async_services()
        esphome_services = all_services.get("esphome", {})
        
        target_services = []
        broadcast = self.entry.options.get(CONF_BROADCAST_MODE, False)
        
        # 1. Collect all potential services
        all_solar_services = [s for s in esphome_services if s.startswith("cyd_solar_display_") and s.endswith("_update_display")]
        if "cyd_solar_display_update_display" in esphome_services and "cyd_solar_display_update_display" not in all_solar_services:
            all_solar_services.append("cyd_solar_display_update_display")

        if broadcast:
            target_services = all_solar_services
        else:
            # Specific Mode: Target only the display matching the configured IP (host)
            target_host = self.entry.data.get(CONF_HOST)
            for entry in self.hass.config_entries.async_entries("esphome"):
                if entry.data.get("host") == target_host:
                    name_data = entry.data.get("name", "")
                    title_data = entry.title
                    
                    possible_names = [name_data, title_data]
                    for d_name in possible_names:
                        if d_name:
                            srv = f"{str(d_name).lower().replace('-', '_').replace(' ', '_')}_update_display"
                            if srv in esphome_services:
                                target_services = [srv]
                                break
                if target_services:
                    break
        
        # Fallback: If specific targeting fails but only one generic service exists, use it!
        if not target_services and len(all_solar_services) == 1:
            target_services = all_solar_services
            _LOGGER.debug(f"Calling only service {target_services[0]} as specific match failed but 1 display exists")
        elif not target_services and len(all_solar_services) > 1:
            _LOGGER.error("MEHRERE DISPLAYS gefunden, aber IP/Host '%s' passt zu keinem ESPHome-Gerät! Aus Sicherheitsgründen wird nichts gesendet.", target_host)
            return payload

        if not target_services:
            _LOGGER.warning(
                "Kein CYD Solar Display in ESPHome gefunden (oder noch 'entdeckt' aber nicht hinzugefügt). "
                "Bitte klicke in der ESPHome Integration bei den Displays auf 'Hinzufügen'."
            )
            return payload
                
        for srv in target_services:
            try:
                await self.hass.services.async_call("esphome", srv, service_data)
            except Exception as err:
                _LOGGER.error("Could not call ESPHome service '%s': %s", srv, err)

        return payload

    async def async_check_version(self, force=False):
        """Fetch latest version from GitHub."""
        now = datetime.now()
        if force or self.latest_version == "0.0.0" or self.last_version_check is None or (now - self.last_version_check).total_seconds() > 60:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.version_url, timeout=5) as response:
                        if response.status == 200:
                            self.latest_version = (await response.text()).strip()
                            self.last_version_check = now
                            _LOGGER.debug("Latest GitHub version: %s", self.latest_version)
                            return True
            except Exception as e:
                _LOGGER.warning("Failed to fetch version from GitHub: %s", e)
        return False
