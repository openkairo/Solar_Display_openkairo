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
    CONF_SHOW_KW,
    CONF_AUTO_PAGE_SWITCH,
    CONF_PAGE_INTERVAL,
    CONF_PAGE_SWITCH_MODE,
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
        self.host = entry.data[CONF_HOST]
        self.port = entry.data.get(CONF_PORT, 80)
        self.current_page = 1
        self.last_page_switch = datetime.now()
        
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
        self.async_add_listener(self._dummy_listener)

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
        }

        # Handle Page Switching
        enable_p1 = self.entry.options.get(CONF_ENABLE_PAGE1, True)
        enable_p2 = self.entry.options.get(CONF_ENABLE_PAGE2, True)
        enable_p3 = self.entry.options.get(CONF_ENABLE_PAGE3, True)
        enable_p4 = self.entry.options.get(CONF_ENABLE_PAGE4, True)
        enable_p5 = self.entry.options.get(CONF_ENABLE_PAGE5, True)
        
        enabled_pages = []
        if enable_p1: enabled_pages.append(1)
        if enable_p2: enabled_pages.append(2)
        if enable_p3: enabled_pages.append(3)
        if enable_p4: enabled_pages.append(4)
        if enable_p5: enabled_pages.append(5)
        
        if not enabled_pages: enabled_pages = [1]
        
        # Seitenwechsel-Modus auslesen
        switch_mode = self.entry.options.get(CONF_PAGE_SWITCH_MODE, PAGE_SWITCH_AUTO)
        
        try:
            interval = int(self.entry.options.get("page_interval", 10))
        except (ValueError, TypeError):
            interval = 10
        
        # Ensure our current page is valid
        # Ensure our current page is valid, and handle first-boot injection
        if self.current_page not in enabled_pages:
            self.current_page = enabled_pages[0]
            
        if switch_mode == PAGE_SWITCH_TOUCH:
            # Nur Touch-Modus: HA haelt Seite 1 fest
            # Der ESP32 steuert Seitenwechsel vollstaendig per Touch-Override
            self.current_page = enabled_pages[0]
            self.last_page_switch = datetime.now()  # Intervall-Timer zuruecksetzen
        else:
            # Auto oder Both: HA rotiert Seiten nach Intervall
            # Check if first launch OR time has passed
            time_since = (datetime.now() - self.last_page_switch).total_seconds()
            
            if time_since >= interval or time_since > 31536000: # Over an interval, or last_switch was epoch
                idx = enabled_pages.index(self.current_page)
                # Only advance the page if this wasn't the very first call
                if time_since < 31536000:
                    self.current_page = enabled_pages[(idx + 1) % len(enabled_pages)]
                    
                self.last_page_switch = datetime.now()
            
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
            "dim_start": int(self.entry.options.get("dim_start_time", 22)),
            "dim_end": int(self.entry.options.get("dim_end_time", 6)),
            "dim_brt": float(self.entry.options.get("dim_brightness", 20.0)),
            "p1_en": bool(enable_p1),
            "p2_en": bool(enable_p2),
            "p3_en": bool(enable_p3),
            "p4_en": bool(enable_p4),
            "p5_en": bool(enable_p5),
        }
        
        # Call the ESPHome Service
        # We assume the device name is 'cyd_solar_display' as per YAML,
        # but HA might append strings like 'cyd_solar_display_2' or 'cyd_solar_display_495ec4'
        esphome_services = self.hass.services.async_services().get("esphome", {})
        service_name = "cyd_solar_display_update_display"
        
        if service_name not in esphome_services:
            possible_services = [s for s in esphome_services if s.endswith("_update_display")]
            if possible_services:
                service_name = possible_services[0]
                
        try:
            await self.hass.services.async_call(
                "esphome", 
                service_name, 
                service_data
            )
        except Exception as err:
            _LOGGER.error("Could not call ESPHome service '%s': %s", service_name, err)

        return payload
