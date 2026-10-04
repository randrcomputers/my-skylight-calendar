# DIY Smart Home Family Calendar (Skylight-style)

[![Week Planner Card Plus](https://img.shields.io/badge/Uses-Week%20Planner%20Card%20Plus-41BDF5)](https://github.com/randrcomputers/week-planner-card-plus)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![hacs_badge](https://img.shields.io/badge/Open%20Plus%20in%20HACS-my-41BDF5.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=randrcomputers&repository=week-planner-card-plus&category=plugin)
[![hacs_badge](https://img.shields.io/badge/Open%20this%20integration%20in%20HACS-my-41BDF5.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=randrcomputers&repository=my-skylight-calendar&category=integration)

Fork of [mohesles/my-skylight-calendar](https://github.com/mohesles/my-skylight-calendar) with a **foolproof setup wizard** and **[Week Planner Card Plus](https://github.com/randrcomputers/week-planner-card-plus)**.

![Skylight calendar](assets/main_view.jpeg)

---

## Foolproof install (2 downloads)

### 1. Week Planner Card Plus (HACS → Frontend)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=randrcomputers&repository=week-planner-card-plus&category=plugin)

Or: HACS → Frontend → Custom repositories →  
`https://github.com/randrcomputers/week-planner-card-plus` → **Plugin** → Download.

Hard-refresh the browser after install (**Ctrl+F5**).

### 2. This integration (HACS → Integrations)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=randrcomputers&repository=my-skylight-calendar&category=integration)

1. Download **Skylight Family Calendar** → restart HA  
2. **Settings → Devices & services → Add Integration → Skylight Family Calendar**  
3. Walk the wizard (it checks whether Plus is installed)  
4. Open the **Family Calendar** dashboard (or follow the notification)

That's it. The generated dashboard matches the **original Skylight look** (big clock, weather, person pills, Add Event, view selector, week grid).

**Frontend cards (HACS → Frontend)** so it actually looks like the screenshots:

1. Week Planner Card Plus (required)
2. Bubble Card (person pills + Add Event)
3. Config Template Card (Today / Week / Month)
4. card-mod (rounded tiles / colors)
5. Better Moment Card (clock)
6. Weather Card (optional, if you pick a weather entity)

Copy `themes/skylight.yaml` into your HA themes if you want the same fonts/colors.

Hard-refresh (**Ctrl+F5**) after installing cards. Missing cards show up on `sensor.skylight_setup_status` and in **Settings → System → Repairs**.

Chore/todo checkboxes (dishwasher, laundry, …) are **not** part of the shared template — those stay on your own dashboard.

### Stuck? One-click fix

**Developer Tools → Services → `skylight_calendar.fix_setup`**

That re-registers Plus, reinstalls the dashboard, and shows the checklist again.

Also check:

- `sensor.skylight_setup_status` → should be `ready` (attributes list anything `missing`)
- **Settings → System → Repairs** — Plus problems show up there with steps

---

## What the wizard does

| Action | Details |
|--------|---------|
| Prerequisite check | Detects Plus on disk / in Lovelace resources |
| Pick people / calendars | Entity selectors — or leave blank to create Local Calendars |
| Never recreate existing calendars | Skips if entity or same-name calendar already exists |
| Filter UI | Color **person pills** (Bubble) — tap to show/hide |
| Week grid | Plus week/month via **Select View** (Config Template) |
| Add / Edit | Tap empty day or event; **Add Event** opens the family calendar |
| Lovelace resource | Auto-registers the Plus JS when HACS installed it |
| HA Repairs | Creates a Repair if Plus is missing or unregistered |
| Status | `sensor.skylight_setup_status` → `ready` / `needs_attention` |
| Backup YAML | `/config/skylight_calendar/dashboard_generated.yaml` |

Services:

- `skylight_calendar.fix_setup` ← start here if something’s wrong  
- `skylight_calendar.install_dashboard`  
- `skylight_calendar.create_missing_calendars`

---

## If something’s wrong

1. Call `skylight_calendar.fix_setup`
2. Hard-refresh (**Ctrl+F5**)
3. Open `sensor.skylight_setup_status` → attribute `missing`
4. Confirm Plus: HACS → Frontend → Week Planner Card Plus
5. Settings → Dashboards → ⋮ → Resources → URL containing `week-planner-card-plus`
6. Check **Settings → System → Repairs**

---

## Manual / classic YAML (optional)

Still available if you want the original package style:

- [`setup/setup-dashboard.yaml`](setup/setup-dashboard.yaml) checklist  
- [`packages/family_calendar.yaml`](packages/family_calendar.yaml)  
- [`dashboard.yaml`](dashboard.yaml)  

---

## Credits

- **[@mohesles](https://github.com/mohesles)** — original DIY Skylight project  
- **[@FamousWolf](https://github.com/FamousWolf)** — Week Planner Card  
- **[Week Planner Card Plus](https://github.com/randrcomputers/week-planner-card-plus)** · **[ICS Calendar Tools](https://github.com/randrcomputers/ics-calendar-tools)**

Community: [DIY Family Calendar (Skylight)](https://community.home-assistant.io/t/diy-family-calendar-skylight/844830)
