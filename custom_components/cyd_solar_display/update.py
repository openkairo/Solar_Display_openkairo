import aiohttp
import logging
from homeassistant.components.update import (
    UpdateEntity,
    UpdateEntityFeature,
    UpdateDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the CYD Solar update entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    main_host = entry.data.get(CONF_HOST)
    # 1. Haupt-Device hinzufügen
    entities.append(
        CYDSolarUpdateEntity(
            coordinator=coordinator, 
            entry=entry, 
            target_host=main_host, 
            unique_id=f"{entry.entry_id}_update",
            title="CYD Solar Firmware",
            device_id=entry.entry_id
        )
    )
    
    # 2. Weitere ESPHome CYD Displays suchen (falls Broadcast oder generelle Mehrfachnutzung erlaubt sein soll)
    for esphome_entry in hass.config_entries.async_entries("esphome"):
        e_host = esphome_entry.data.get("host")
        e_title = esphome_entry.title or ""
        
        # Ignoriere das Hauptgerät, das wir bereits hinzugefügt haben
        if e_host and e_host != main_host:
            # Heuristik: Handelt es sich um ein CYD Display?
            if "cyd" in e_title.lower() or "solar" in e_title.lower():
                uid = f"{entry.entry_id}_additional_{esphome_entry.entry_id}"
                entities.append(
                    CYDSolarUpdateEntity(
                        coordinator=coordinator, 
                        entry=entry, 
                        target_host=e_host, 
                        unique_id=uid,
                        title=f"{e_title} Firmware",
                        device_id=esphome_entry.entry_id
                    )
                )

    async_add_entities(entities)

class CYDSolarUpdateEntity(CoordinatorEntity, UpdateEntity):
    """Update entity for CYD Solar Display."""

    _attr_has_entity_name = True
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.INSTALL

    def __init__(self, coordinator, entry, target_host: str, unique_id: str, title: str, device_id: str):
        """Initialize."""
        super().__init__(coordinator)
        self.entry = entry
        self._target_host = target_host
        self._attr_unique_id = unique_id
        self._attr_title = title
        
        # We try to keep it under separate devices (or all in one? Separate is cleaner)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=title.replace(" Firmware", ""),
            manufacturer="OpenKairo",
            model="ESP32-2432S028",
        )

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "display_ip": self._target_host,
        }

    @property
    def installed_version(self):
        """Version currently in use."""
        try:
            from homeassistant.helpers import entity_registry as er
            ent_reg = er.async_get(self.coordinator.hass)
            
            # 1. Finde den passenden ESPHome Config Entry für dieses Display (Target Host)
            esphome_entries = self.coordinator.hass.config_entries.async_entries("esphome")
            target_esphome = next((e for e in esphome_entries if e.data.get("host") == self._target_host), None)
            
            if target_esphome:
                for entity in er.async_entries_for_config_entry(ent_reg, target_esphome.entry_id):
                    if entity.domain == "update" and entity.platform == "esphome":
                        state = self.coordinator.hass.states.get(entity.entity_id)
                        if state and "installed_version" in state.attributes:
                            v = state.attributes["installed_version"]
                            if v and v != "unknown":
                                import re
                                return re.sub(r'[^\d\.]', '', str(v))
                                
                # 3. Fallback: Suche nach einem Firmware-Version Sensor (falls kein Update-Entity vorhanden)
                for entity in er.async_entries_for_config_entry(ent_reg, target_esphome.entry_id):
                    if entity.domain == "sensor" and "firmware" in entity.entity_id:
                        state = self.coordinator.hass.states.get(entity.entity_id)
                        if state and state.state not in ["unknown", "unavailable"]:
                            import re
                            return re.sub(r'[^\d\.]', '', str(state.state))
                            
        except Exception as e:
            _LOGGER.debug("Fehler beim Ermitteln der Firmware für %s: %s", self._target_host, e)

        # 4. Letztes Fallback: Coordinator-Daten (nur als Fallback-Wert 1.2.7)
        return str(self.coordinator.data.get("installed_version", "1.2.7")).strip().lstrip("vV")

    @property
    def latest_version(self):
        """Latest version available for install."""
        v = self.coordinator.latest_version
        if v:
            import re
            return re.sub(r'[^\d\.]', '', str(v))
        return v

    @property
    def state(self):
        """Force exactly the state, bypassing any AwesomeVersion cached state bugs."""
        i_ver = self.installed_version
        l_ver = self.latest_version
        if i_ver and l_ver and str(i_ver) == str(l_ver):
            return "off"
        if i_ver != l_ver:
            return "on"
        return "off"
    @property
    def in_progress(self):
        """Update installation in progress."""
        return self.coordinator.data.get("update_in_progress", False)

    async def async_install(self, version: str, backup: bool, **kwargs):
        """Install an update using the ESPHome web server via Direct Push."""
        _LOGGER.info("USER-ACTION: Direct-Push Update gestartet für Version %s (Host: %s)", version, self._target_host)
        
        if not self._target_host:
            _LOGGER.error("FEHLER: Keine Host-IP für das Display gefunden!")
            return

        # 1. URL zur Datei auf GitHub
        update_url = "https://raw.githubusercontent.com/low-streaming/cyd_solar_display/main/cyd_solar_display.bin"
        
        try:
            # 2. Download der Binary von GitHub
            _LOGGER.info("Lade Firmware von GitHub herunter: %s", update_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(update_url) as resp:
                    if resp.status != 200:
                        _LOGGER.error("Download fehlgeschlagen (Status %s)", resp.status)
                        return
                    binary_data = await resp.read()
            
            # 3. Upload zum Display (ESPHome WebServer /update endpoint)
            upload_url = f"http://{self._target_host}/update"
            _LOGGER.info("Pushing Firmware zu Display unter: %s", upload_url)
            
            data = aiohttp.FormData()
            data.add_field('update', 
                           binary_data,
                           filename='firmware.bin',
                           content_type='application/octet-stream')
                           
            
            async with aiohttp.ClientSession() as session:
                async with session.post(upload_url, data=data) as resp:
                    if resp.status == 200:
                        _LOGGER.info("Update erfolgreich gesendet! Display startet neu.")
                    else:
                        _LOGGER.error("Push fehlgeschlagen! Status: %s. Ist der WebServer aktiv?", resp.status)

        except Exception as err:
            _LOGGER.error("Kritischer Fehler beim Update-Push: %s", err)
