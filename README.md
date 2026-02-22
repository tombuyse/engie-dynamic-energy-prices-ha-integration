# Engie Dynamic Prices — Home Assistant Integration

A custom Home Assistant integration that exposes [Engie Belgium](https://www.engie.be) dynamic electricity prices (EPEX SPOT day-ahead) as sensors.

Prices are published daily around 14:00 for the following day and are fetched automatically once per day.

## Sensors

| Entity | Description | Unit |
|---|---|---|
| `sensor.engie_dynamic_prices_current_price` | Price for the current hour | EUR/kWh |
| `sensor.engie_dynamic_prices_next_price` | Price for the next hour | EUR/kWh |
| `sensor.engie_dynamic_prices_average_price` | Today's average price | EUR/kWh |
| `sensor.engie_dynamic_prices_min_price` | Today's cheapest hour price | EUR/kWh |
| `sensor.engie_dynamic_prices_max_price` | Today's most expensive hour price | EUR/kWh |

The **average price** sensor also carries a `cheapest_hours` attribute — a list of all 24 hours sorted by ascending price, useful for scheduling automations (e.g. start the dishwasher during the 3 cheapest hours).

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations** → **Custom repositories**
3. Add `https://github.com/tombuyse/engie-dynamic-energy-prices-ha-integration` with category **Integration**
4. Install **Engie Dynamic Prices**
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/engie_dynamic_prices` folder into your HA `config/custom_components/` directory
2. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Engie Dynamic Prices**
3. Click **Submit** — no configuration required

## How it works

- The integration polls the [Engie EPEX SPOT XLSX feed](https://www.engie.be/api/engie/be/ms/pricing/public/v1/epex-prices/export?exportType=XLSX) once per day (at midnight when the API switches to the new day's prices)
- The coordinator wakes up hourly to update `current_price` and `next_price` without making a new API call
- Prices are converted from EUR/MWh (raw) to EUR/kWh to match Home Assistant's energy dashboard convention

## Automation example

Turn on a high-power device only when the current price is below today's average:

```yaml
automation:
  - alias: "Run dishwasher when price is cheap"
    trigger:
      - platform: state
        entity_id: sensor.engie_dynamic_prices_current_price
    condition:
      - condition: template
        value_template: >
          {{ states('sensor.engie_dynamic_prices_current_price') | float
             < states('sensor.engie_dynamic_prices_average_price') | float }}
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.dishwasher
```
