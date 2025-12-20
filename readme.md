# E-Paper Weather Station

**Raspberry Pi 3B + Waveshare 4.26" E-Paper HAT (800×480px)**

## Project Overview

A weather station with E-Paper display that combines local Netatmo sensors with SMHI weather data, SMHI Observations, and precise sun times. The system uses a dynamic module system with trigger-based modules, high-quality Weather Icons, and an intelligent rendering pipeline.

### Key Features

- **Dynamic Module System**: Modules activate automatically based on weather conditions
- **SMHI Observations**: Real-time precipitation data from weather station 98230 (Stockholm-Observatoriekullen)
- **Netatmo Integration**: Local temperature, pressure, and rain gauge measurements
- **UV Index**: Current UV levels from CurrentUVIndex.com
- **Intelligent Fallbacks**: Graceful degradation when APIs fail

### Netatmo Compatibility

**This project works with Netatmo Weather Station Gen 1.** While Gen 2 introduced native UV measurements, this implementation uses external UV data from CurrentUVIndex.com API, making it compatible with both Gen 1 and Gen 2 stations. The system requires:
- Netatmo Base Station (indoor module)
- Outdoor Module (NAModule1) for temperature/humidity
- Rain Gauge (NAModule3) for precipitation - optional but recommended

## Hardware Requirements

### Components
- **Raspberry Pi 3B** (or newer)
- **Waveshare 4.26" E-Paper HAT** (800×480px, black & white)
- **SPI enabled** (`lsmod | grep spi` should show spi modules)
- **Internet connection** for API calls

### E-Paper Specifications
- **Resolution**: 800×480 pixels
- **Colors**: 1-bit black & white (optimized for E-Paper)
- **Refresh time**: ~10 seconds per render
- **Power consumption**: Very low (E-Paper retains image without power)

## Data Sources

### Netatmo (Priority for Local Measurements)
- 🌡️ **Outdoor Temperature** (from outdoor module NAModule1)
- 📊 **Air Pressure** (from indoor module, more accurate than SMHI)
- 🌧️ **Precipitation** (from rain gauge NAModule3) - 5-minute delay
- 💨 **Humidity** (outdoor + indoor)
- 📈 **3-hour Pressure Trend** (meteorological standard)
- 🔋 **Battery Status** (outdoor module and rain gauge)

### SMHI Forecasts
- 🌤️ **Current Weather** (27 SMHI symbols with day/night variants)
- 🌦️ **Tomorrow's Forecast** (temperature + weather)
- 💨 **Wind and Precipitation** (including cycling weather analysis)
- 📍 **Geographic Data**

### SMHI Observations (Real-time Precipitation)
- 🌧️ **Current Precipitation** (last hour from Observatorielunden)
- 📊 **Station 98230** (Stockholm-Observatoriekullen A)
- ✅ **Quality Codes** (G=Approved, Y=Preliminary, R=Poor)
- ⏰ **Hourly Data** (updated every full hour)
- 🔄 **Fallback to Arlanda** (station 97390) on error

### CurrentUVIndex.com (UV Data)
- ☀️ **Current UV Index** (real-time measurement)
- 📈 **Daily Peak UV** (forecast maximum)
- 🎯 **Risk Classification** (Low/Moderate/High/Very High/Extreme)
- 🆓 **Free API** (no key required, 500 calls/day)
- ⏱️ **6-hour Cache** (balances freshness with API limits)

### ipgeolocation.io API (Sun Times)
- ☀️ **Sunrise/Sunset** (precise times for coordinates)
- ⏰ **Daylight Duration** (automatic calculation)
- 🌅 **Day/Night Logic** for weather icons

## Data Priority System

The app uses intelligent prioritization:

### Precipitation Priority
1. **Netatmo Rain Gauge** (5-min delay) - highest priority
2. **SMHI Observations** (10-60 min delay) - fallback
3. **SMHI Forecasts** - last fallback

### Temperature/Pressure Priority
1. **Netatmo** local measurements
2. **SMHI** forecasts

### UV Priority
1. **CurrentUVIndex.com** (6-hour cache)
2. **No fallback** (displays only when available)

## Dynamic Module System

The system automatically switches between different modules based on:
- 🌧️ **Weather Conditions** (precipitation triggers warnings)
- 👤 **User Settings** (switch between barometer/sun module)
- ⏰ **Time/Season** (potential for UV index in summer, dark month layouts)
- 🎯 **Trigger Conditions** (customizable conditions)

### Trigger-Based Modules

```json
{
  "triggers": {
    "precipitation_trigger": {
      "condition": "precipitation > 0 OR forecast_precipitation_2h > 0.2",
      "target_section": "bottom_section",
      "activate_group": "precipitation_active",
      "priority": 100
    }
  }
}
```

**Example: Dynamic Switching**
- **Normal layout**: Clock + Status at bottom
- **Precipitation detected (>0mm/h)**: Automatic switch to precipitation warning
- **Forecast rain >0.2mm/h**: Switch to forecast warning
- **After rain**: Automatic return to normal layout

## Architecture and Modules

### Dual System Approach

**`main_daemon.py`** - Active dynamic daemon system:
- Continuous process (systemd service)
- Trigger-based module switching
- 60-second update interval
- 30-minute watchdog for forced updates

**`main.py`** - Legacy cron-based system (backup):
- Single execution
- Manual module control
- Simpler architecture

### Module Structure

```
epaper_weather/
├── main_daemon.py          # Active daemon (dynamic system)
├── main.py                 # Legacy backup
├── config.json             # Configuration + triggers + modules
├── modules/
│   ├── weather_client.py   # API integration (SMHI, Netatmo, UV, ipgeolocation.io)
│   ├── icon_manager.py     # Weather Icons PNG management
│   ├── sun_calculator.py   # Sunrise/sunset calculations
│   └── renderers/          # Dynamic Module System
│       ├── base_renderer.py
│       ├── module_factory.py
│       ├── precipitation_renderer.py
│       └── wind_renderer.py
├── tools/
│   ├── restart.py
│   └── test_precipitation_trigger.py
└── install_daemon.sh
```

### Dynamic Module Components

**DynamicModuleManager**: Evaluates triggers and manages module groups
**TriggerEvaluator**: Safe condition evaluation (whitelisted functions only)
**ModuleFactory**: Creates renderer instances for active modules
**Renderers**: Modular rendering pipeline (base class + specific implementations)

### Module Types

- **HERO** (480×200px): Main weather display
- **MEDIUM** (240×200px): Barometer, forecast, sun data
- **SMALL** (240×100px): Clock/date, status

## Layout

### Layout A (Default)

**Total data points: 16**

```
┌─────────────────────────┬─────────────┐
│ Stockholm               │ 1007 ↗️     │
│ 25.1°C ⛅              │ hPa         │
│ Light rain showers     │ Rising      │
│ (NETATMO)              │ (Netatmo)   │
│ 🌅 04:16  🌇 21:30    ├─────────────┤
│ ☀️ UV 3.2             │ Tomorrow ⛅  │
├─────────┬──────────────┤ 25.4°C      │
│ 📅 25/7 │ Update: 12:07│ Partly cloud│
│ Friday  │ 🔋 85% Out   │ (SMHI)      │
│         │ 🔋 92% Rain  │             │
└─────────┴──────────────┴─────────────┘
```

### Dynamic Bottom Section

**Normal (no precipitation):**
```
┌─────────┬──────────────┐
│ Clock   │ Status       │
└─────────┴──────────────┘
```

**Precipitation detected:**
```
┌───────────────────────────┐
│ ⚠️  RAINING NOW: LIGHT   │
│     (Observatorielunden)  │
│     2.5mm last hour       │
└───────────────────────────┘
```

## Icon System - Weather Icons Integration

### SVG→PNG Conversion System
The app uses high-quality PNG icons converted from Weather Icons SVG sources with E-Paper optimization.

**Icon Sources:**
- **SVG source**: `\\EINK-WEATHER\downloads\weather-icons-master\svg\` (Windows share)
- **PNG destination**: `~/epaper_weather/icons/` (Raspberry Pi)
- **Conversion**: Via `convert_svg_to_png.py` in virtual environment with cairosvg

#### Icon Categories and Sizes

**Weather Icons (54 total)**
- **Source**: Erik Flowers Weather Icons
- **Mapping**: Exact SMHI-symbol → Weather Icons
- **Day/Night**: Automatic selection based on sun times
- **Sizes**: 32×32 (forecast), 48×48 (standard), 96×96 (HERO)

**Pressure Arrows (existing wi-direction-X)**
- **Source**: wi-direction-up/down/right.png (existing with rings)
- **Sizes**: 20×20, 56×56, 64×64 (optimal), 96×96, 120×120
- **Usage**: 3-hour pressure trend according to meteorological standard

**Sun Icons**
- **Source**: wi-sunrise.svg, wi-sunset.svg
- **Sizes**: 24×24, 40×40 (standard), 56×56, 80×80
- **Usage**: Precise sun times in HERO module

**System Icons**
- **Barometer**: wi-barometer.svg → various sizes (12-96px)
- **Clock**: wi-time-7.svg → 32×32 (optimal visibility)
- **Calendar**: wi-calendar.svg → 40×40 (for date module)
- **Battery**: wi-battery.svg → 24×24 (for status module)
- **UV**: wi-ultraviolet.svg → 40×40 (for HERO module)
- **Status**: wi-day-sunny.svg (OK), wi-refresh.svg (update)

## Configuration

### Dynamic Module System Configuration

```json
{
  "_comment_dynamic_system": "=== DYNAMIC MODULE SYSTEM ===",
  "module_groups": {
    "bottom_section": {
      "_comment": "Bottom: Normal = clock+status, Precipitation = warning", 
      "normal": ["clock_module", "status_module"],
      "precipitation_active": ["precipitation_module"]
    }
  },
  "triggers": {
    "precipitation_trigger": {
      "condition": "precipitation > 0 OR forecast_precipitation_2h > 0.2",
      "target_section": "bottom_section",
      "activate_group": "precipitation_active", 
      "priority": 100,
      "description": "Activate precipitation module on rain"
    }
  }
}
```

### API Configuration

**Netatmo:**
```json
{
  "api_keys": {
    "netatmo": {
      "client_id": "YOUR_CLIENT_ID",
      "client_secret": "YOUR_CLIENT_SECRET",
      "refresh_token": "YOUR_REFRESH_TOKEN"
    }
  }
}
```

**SMHI Observations:**
```json
{
  "stockholm_stations": {
    "observations_station_id": "98230",
    "observations_station_name": "Stockholm-Observatoriekullen A",
    "alternative_station_id": "97390", 
    "alternative_station_name": "Stockholm-Arlanda"
  }
}
```

**Location (used for SMHI, UV, and Sun API):**
```json
{
  "location": {
    "name": "Stockholm",
    "latitude": 59.3293,
    "longitude": 18.0686
  }
}
```

## Installation

### 1. System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Install ImageMagick (for icon conversion)
sudo apt install imagemagick -y

# Install E-Paper dependencies
sudo apt install python3-pil python3-numpy -y
```

### 2. Enable SPI

```bash
# Enable SPI via raspi-config
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable

# Verify SPI is enabled
lsmod | grep spi
# Should show: spi_bcm2835
```

### 3. Clone and Setup

```bash
# Clone repository
cd ~
git clone <your-repo-url> epaper_weather
cd epaper_weather

# Install Python dependencies
pip3 install -r requirements.txt

# Copy and edit configuration
cp config.json.example config.json
nano config.json
# Add your Netatmo credentials and adjust location
```

### 4. Install as Systemd Service

```bash
# Install daemon
sudo bash install_daemon.sh

# Check status
sudo systemctl status epaper-weather

# View logs
sudo journalctl -u epaper-weather -f
```

## Usage

### Daemon Commands

```bash
# Restart daemon
python3 restart.py

# View logs
sudo journalctl -u epaper-weather -f

# View specific logs
sudo journalctl -u epaper-weather -f | grep -E "UV|Battery|Precipitation"

# Stop daemon
sudo systemctl stop epaper-weather

# Start daemon
sudo systemctl start epaper-weather
```

### Testing Precipitation Module

```bash
# Inject test data
python3 test_precipitation_trigger.py
# Select scenario (e.g., "2" for moderate rain)

# Restart to load test data
python3 restart.py

# Clean test data
python3 test_precipitation_trigger.py
# Select "10" to clean
```

## Trigger System

### Trigger Syntax

**Operators:** `> < >= <= == != AND OR`

**Functions:** `precipitation`, `forecast_precipitation_2h`, `temperature`, `wind_speed`, `time_hour`, `time_month`, `pcat`

**Examples:**
```python
"precipitation > 0"  # Currently raining (Netatmo or Observations)
"forecast_precipitation_2h >= 0.2 AND pcat == 3"  # Rain expected
"pcat == 2 OR pcat == 3 OR pcat == 5"  # Rain-containing precipitation
"wind_speed > 6.0"  # Wind speed threshold
"time_month >= 6 AND time_month <= 8"  # Summer months
```

### Precipitation Categories (pcat)

| pcat | Type | Trigger? |
|------|------|----------|
| 0 | No precipitation | ❌ |
| 1 | Snow | ❌ |
| 2 | Mixed rain/snow | ✅ (you get wet) |
| 3 | Rain | ✅ |
| 4 | Hail (no rain) | ❌ |
| 5 | Hail + rain | ✅ |
| 6 | Hail + snow | ❌ |

## Troubleshooting

### Display Not Updating

```bash
# Check daemon status
sudo systemctl status epaper-weather

# Check logs for errors
sudo journalctl -u epaper-weather -n 50

# Verify SPI
lsmod | grep spi

# Restart daemon
python3 restart.py
```

### API Issues

**Netatmo:**
```bash
# Check credentials in config.json
# Verify token refresh works
sudo journalctl -u epaper-weather | grep "Netatmo"
```

**UV API:**
```bash
# Check UV logs
sudo journalctl -u epaper-weather | grep "UV"

# Verify coordinates in config.json
# Check API limit (500/day)
```

**SMHI:**
```bash
# Check SMHI logs
sudo journalctl -u epaper-weather | grep "SMHI"

# Verify station ID in config.json
```

### Battery Status Not Showing

```bash
# Verify Netatmo modules are connected
sudo journalctl -u epaper-weather | grep "Battery"

# Check if modules are reporting battery
sudo journalctl -u epaper-weather | grep "Netatmo sensorer"
```

## Project Structure

```
epaper_weather/
├── main_daemon.py              # Active daemon with dynamic system
├── main.py                     # Legacy backup
├── config.json                 # Configuration file
├── requirements.txt            # Python dependencies
├── install_daemon.sh           # Systemd installation script
├── restart.py                  # Daemon restart tool
├── modules/
│   ├── weather_client.py       # API integration
│   ├── icon_manager.py         # Icon management
│   ├── sun_calculator.py       # Sun calculations
│   └── renderers/              # Module renderers
│       ├── base_renderer.py
│       ├── module_factory.py
│       ├── precipitation_renderer.py
│       └── wind_renderer.py
├── icons/
│   ├── weather/                # Weather Icons (54 SMHI symbols)
│   ├── pressure/               # Pressure trend arrows
│   ├── sun/                    # Sunrise/sunset icons
│   └── system/                 # System icons (battery, UV, etc.)
├── cache/
│   ├── pressure_history.json   # 3-hour pressure trend data
│   └── last_run_values.json    # Change detection cache
├── logs/
│   └── epaper_weather.log      # Application logs
└── tools/
    └── test_precipitation_trigger.py
```

## Credits and Licenses

### APIs Used
- **SMHI Open Data** - CC0 1.0 Universal
- **Netatmo API** - OAuth2 integration
- **CurrentUVIndex.com** - Free UV API (CC BY 4.0)
- **ipgeolocation.io** - Sun times API

### Icon Sources
- **Weather Icons** by Erik Flowers - SIL OFL 1.1
- **Conversion**: ImageMagick + cairosvg

### Libraries
- **Waveshare E-Paper Library** - MIT License
- **Pillow** - PIL License
- **Requests** - Apache 2.0

## License

MIT License - See LICENSE file for details

---

**Created:** 2024  
**Last Updated:** December 2024  
**Platform:** Raspberry Pi 3B + Waveshare 4.26" E-Paper HAT
