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
| 🔮 **Eigene Sensoren** | **28 frei belegbare** HA-Sensoren (Seite 3 bis 9) |
| 👆 **Touch-Seitenwechsel** | Irgendwo tippen = nächste Seite |
| 🔄 **Auto-Seitenwechsel** | HA rotiert Seiten nach konfigurierbarem Intervall |
| 🔄👆 **Hybridmodus** | Auto + Touch-Override für ~30 Sekunden |
| 🆕 **One-Click Update** | Firmware-Updates direkt im HA-Panel mit einem Klick |
| 🆕 **Web-Flasher** | Erstinstallation direkt im Browser ohne Zusatzsoftware |
| 🖥️ **HA Panel** | Interaktives Sidebar-Panel mit 1:1 Live-Preview |

---

## 🛒 Hardware

| # | Was | Details |
|---|-----|---------|
| 1 | **ESP32 CYD** | Modell **2432S028** (Cheap Yellow Display) |
| 2 | **Home Assistant** | Version 2023.4.0 oder neuer |
| 3 | **Browser** | Chrome oder Edge (für den Web-Flasher) |

> 🛒 Die Hardware gibt es **fertig geflasht (Plug & Play)** bei:  
> **[solarmodule-gladbeck.de/produkt/ok_display/](https://solarmodule-gladbeck.de/produkt/ok_display/)**

---

## ⚡ Erstinstallation (Web-Flasher)

Wenn du ein frisches Display hast, kannst du es direkt über den Browser flashen:

1. Öffne den **[CYD Web-Flasher](https://openkairo.github.io/Solar_Display_openkairo/)** (Chrome/Edge erforderlich)
2. Verbinde den ESP32 per USB mit deinem PC
3. Klicke auf **Installieren** und wähle den COM-Port aus
4. Nach dem Flash verbindet sich das Display mit deinem WLAN (Portal öffnet sich)

---

## 📦 Integration in Home Assistant (HACS)

HACS ermöglicht die einfache Steuerung des Displays **und automatische Updates**.

### Schritt 1: Repository hinzufügen
1. Öffne HACS in Home Assistant
2. Klicke auf die **3 Punkte** (oben rechts) → **Benutzerdefinierte Repositories**
3. Füge folgende URL ein: `https://github.com/openkairo/Solar_Display_openkairo`
4. Kategorie: **Integration**

### Schritt 2: Einrichten
1. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Suche nach **CYD Solar Display** und gib die IP des Displays ein
3. Öffne das neue Sidebar-Panel **CYD Monitor**
4. Verknüpfe deine Sensoren und klicke auf **Speichern**

---

## 🔄 Firmware Updates

Das System prüft automatisch auf neue Versionen.

1. Öffne das **CYD Monitor** Panel in Home Assistant
2. Wechsel zum Reiter **Hilfe & Info**
3. Wenn ein Update verfügbar ist, erscheint ganz oben eine blaue Karte
4. Klicke auf **🚀 JETZT AKTUALISIEREN** — das Display zieht sich das Update vollautomatisch

---

## 📋 Changelog

### v1.2.7 — 2026-03-28 🚀 Stabilitäts-Update
- ✅ **One-Click Firmware Update**: Neue Sektion im Hilfe-Tab
- ✅ **Web-Flasher Support**: Installation direkt im Browser (index.html/manifest.json)
- ✅ **28 Custom Sensoren**: Unterstützung für Seiten 1 bis 9 voll ausgebaut
- ✅ **Performance Boost**: Refactoring der Display-Logik für maximale Stabilität
- ✅ **Bugfix**: Fehler beim Seiten-Synchronisieren mit HA behoben

### v1.1.0 — 2026-02-28 🔧 Repository Transfer
- 🔁 Repository zu [openkairo/Solar_Display_openkairo](https://github.com/openkairo/Solar_Display_openkairo) umgezogen

---

## 🗺️ Roadmap
- [ ] Mehrere Display-Instanzen gleichzeitig
- [ ] Wetter & PV-Prognose Seite

---

## ☕ Support & Spenden

Dir gefällt das Projekt? Ich freue mich riesig über jeden Beitrag!

[![PayPal Spenden](https://img.shields.io/badge/PayPal-Spenden-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=info@low-streaming.de&currency_code=EUR)

📧 **Kontakt:** `info@low-streaming.de`

---

**Powered by [OpenKairo](https://openkairo.de) · Developed with ♥ by [openkairo](https://github.com/openkairo) for the HA Community**
