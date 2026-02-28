# CYD Solar Display — OpenKairo Edition

![Version](https://img.shields.io/github/v/release/openkairo/Solar_Display_openkairo?style=for-the-badge&color=fdd835&label=Version)
![HACS](https://img.shields.io/badge/HACS-Custom_Integration-orange?style=for-the-badge&logo=home-assistant)
![ESPHome](https://img.shields.io/badge/ESPHome-Compatible-00b4d8?style=for-the-badge)
![License](https://img.shields.io/github/license/openkairo/Solar_Display_openkairo?style=for-the-badge&color=green)

> **Ein Live-Solar-Dashboard für das ESP32 Cheap Yellow Display (CYD 2432S028) im neon-durchfluteten OpenKairo Cyberpunk Design — vollständig in Home Assistant integriert.**

---

## 🚀 Features

| Feature | Beschreibung |
|--------|-------------|
| ⚡ **Live Energiefluss** | Solar, Batterie, Haus & Netz in Echtzeit (Seite 1) |
| 📊 **Ertrags-Statistiken** | Tag, Monat, Jahr & Gesamt PV-Ertrag (Seite 2) |
| 🔮 **Eigene Sensoren** | 8 frei belegbare HA-Sensoren (Seite 3 & 4) |
| ⛏️ **Mining Sensoren** | 4 Slots für Hashrate, Temp, Ertrag etc. (Seite 5) |
| 👆 **Touch-Seitenwechsel** | Irgendwo tippen = nächste Seite |
| 🔄 **Auto-Seitenwechsel** | HA rotiert Seiten nach konfigurierbarem Intervall |
| 🔄👆 **Hybridmodus** | Auto + Touch-Override für ~30 Sekunden |
| 🎛️ **Seiten aktivierbar** | Jede Seite einzeln ein-/ausschaltbar |
| 🔢 **kW / Watt Modus** | Jederzeit zwischen W und kW umschalten |
| 🖥️ **HA Panel** | Interaktives Sidebar-Panel mit 1:1 Live-Preview |

---

## 🛒 Hardware

| # | Was | Details |
|---|-----|---------|
| 1 | **ESP32 CYD** | Modell **2432S028** (Cheap Yellow Display) |
| 2 | **Home Assistant** | Version 2023.4.0 oder neuer |
| 3 | **ESPHome Add-on** | Für die Native API Verbindung |

> 🛒 Die Hardware gibt es **fertig geflasht (Plug & Play)** bei:  
> **[solarmodule-gladbeck.de/produkt/ok_display/](https://solarmodule-gladbeck.de/produkt/ok_display/)**

### Hardware-Pinbelegung (CYD 2432S028)

> ⚠️ Das CYD 2432S028 hat **zwei separate SPI-Busse** — einen für das Display und einen für den Touchscreen!

| Komponente | Funktion | GPIO |
|-----------|---------|------|
| **Display** (ILI9341) | CLK | 14 |
| | MOSI | 13 |
| | MISO | 12 |
| | CS | 15 |
| | DC | 2 |
| **Touchscreen** (XPT2046) | CLK | **25** |
| | MOSI | **32** |
| | MISO | **39** |
| | CS | 33 |
| | IRQ | 36 |
| **Backlight** | PWM | 21 |

---

## 📦 Installation via HACS (Empfohlen)

HACS ermöglicht einfache Installation **und automatische Updates** bei neuen Versionen.

### Schritt 1: Repository hinzufügen
1. Öffne HACS in Home Assistant
2. Klicke auf die **3 Punkte** (oben rechts) → **Benutzerdefinierte Repositories**
3. Füge folgende URL ein:
   ```
   https://github.com/openkairo/Solar_Display_openkairo
   ```
4. Kategorie: **Integration**
5. Klicke **Hinzufügen**

### Schritt 2: Integration installieren
1. Suche in HACS nach **"CYD Solar Display"**
2. Klicke **Herunterladen**
3. Starte Home Assistant neu

### 🔄 Updates über HACS erhalten
Wenn eine neue Version erscheint, zeigt HACS automatisch eine Update-Benachrichtigung an.  
Einfach auf **Aktualisieren** klicken — fertig!

---

## 🔧 Manuelle Installation

1. Lade das Repository als ZIP herunter
2. Entpacke und kopiere `custom_components/cyd_solar_display` nach:
   ```
   /config/custom_components/cyd_solar_display/
   ```
3. Starte Home Assistant neu

---

## ⚙️ Einrichtung

1. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Suche nach **CYD Solar Display**
3. Gib IP-Adresse oder mDNS-Hostname des ESP32 ein (`cyd-solar-display.local`)
4. Öffne das **CYD Monitor** Sidebar-Panel
5. Verknüpfe unter **Einstellungen** deine HA-Sensoren
6. Klicke **Konfiguration Speichern & Anwenden**

---

## 👆🔄 Seitenwechsel-Modi

Unter **Einstellungen → Allgemeine Eigenschaften** kannst du den Modus wählen:

| Modus | Symbol | Verhalten |
|-------|--------|-----------|
| **Automatisch** | 🔄 | HA wechselt Seiten nach dem eingestellten Zeitintervall |
| **Nur Touch** | 👆 | Nur durch Tippen auf das Display — kein Auto-Wechsel |
| **Beides** *(empfohlen)* | 🔄👆 | Auto läuft normal, Touch übersteuert für ~30 Sekunden |

### Anzeige im Display-Footer
- **`[>` gelb** = Touch-Override aktiv (du hast gerade getippt)
- **`[>` weiß** = HA steuert automatisch
- **`< >`** blinkt kurz bei jedem Touch auf

---

## 📡 Funktionsweise

```
Home Assistant  ──(ESPHome Native API)──►  ESP32 CYD
     │                                          │
     │  push_state() alle 5s                    │  Display-Lambda
     │  (Solar, Batterie, Netz, ...)            │  rendert Seiten
     │                                          │
     │◄─────── Touch Event (Binary Sensor) ─────│
```

- **Kein MQTT, kein HTTP-Polling** — rein lokale Native API
- Der ESP32 empfängt Daten aktiv im konfigurierten Intervall
- Touch-Events werden direkt auf dem ESP32 verarbeitet (kein HA-Roundtrip nötig)

---

## 📋 Changelog

### v1.1.0 — 2026-02-28 🔧 Repository Transfer
- 🔁 Repository zu [openkairo/Solar_Display_openkairo](https://github.com/openkairo/Solar_Display_openkairo) umgezogen
- ✅ Code Owner auf @openkairo aktualisiert
- ✅ Alle internen Links und Badges auf das neue Repository angepasst

### v1.0.0 — 2026-02-28 🎉 Initial Release
- ✅ Live Energiefluss-Dashboard (Solar, Batterie, Haus, Netz)
- ✅ Ertrags-Statistiken (Tag, Monat, Jahr, Gesamt)
- ✅ Eigene Sensoren (Seite 3 & 4, je 4 Slots)
- ✅ Mining Sensoren (Seite 5, 4 Slots)
- ✅ **Touch-Seitenwechsel** — überall auf dem Display tippen
- ✅ **Auto-Seitenwechsel** — konfigurierbares Zeitintervall
- ✅ **Hybridmodus** — Auto + Touch-Override (~30 Sek.)
- ✅ Seitenwechsel-Modus wählbar im HA-Panel
- ✅ Seiten einzeln aktivierbar/deaktivierbar
- ✅ kW / Watt Umschaltung
- ✅ Interaktives HA-Sidebar-Panel mit 1:1 Live-Preview
- ✅ Durchsuchbarer Sensor-Picker (Autocomplete)
- ✅ Korrekte Dual-SPI-Konfiguration für CYD 2432S028
- ✅ HACS-kompatibel mit automatischen Updates

---

## 🗺️ Roadmap

### 🔧 Kurzfristig
- [ ] Schwellwert-Benachrichtigungen (z.B. Batterie unter 20%)
- [ ] Mehrere Display-Instanzen gleichzeitig
- [ ] Konfiguration Export/Import als JSON

### 💡 Mittelfristig
- [ ] Weitere Display-Themes (Classic, Minimal)
- [ ] Wetter & PV-Prognose Seite
- [ ] Offizielles HACS Default-Store Listing

---

## ☕ Support & Spenden

Dir gefällt das Projekt? Ich freue mich riesig über jeden Beitrag!

[![PayPal Spenden](https://img.shields.io/badge/PayPal-Spenden-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=info@low-streaming.de&currency_code=EUR)

📧 **Kontakt:** `info@low-streaming.de`

---

**Powered by [OpenKairo](https://openkairo.de) · Developed with ♥ by [openkairo](https://github.com/openkairo) for the HA Community**
