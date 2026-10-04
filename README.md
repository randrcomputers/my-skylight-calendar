# DIY Smart Home Family Calendar (Skylight-style)

[![Week Planner Card Plus](https://img.shields.io/badge/Uses-Week%20Planner%20Card%20Plus-41BDF5)](https://github.com/randrcomputers/week-planner-card-plus)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![hacs_badge](https://img.shields.io/badge/Open%20Plus%20in%20HACS-my-41BDF5.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=randrcomputers&repository=week-planner-card-plus&category=plugin)
[![hacs_badge](https://img.shields.io/badge/Open%20this%20integration%20in%20HACS-my-41BDF5.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=randrcomputers&repository=my-skylight-calendar&category=integration)

Fork of [mohesles/my-skylight-calendar](https://github.com/mohesles/my-skylight-calendar) with a **setup wizard** and **[Week Planner Card Plus](https://github.com/randrcomputers/week-planner-card-plus)**. The wizard builds a dashboard that matches the **original Skylight look**.

![Skylight calendar](assets/main_view.jpeg)

---

## Install

### 1. Frontend cards (HACS → Frontend)

Install these so the dashboard looks like the screenshots (person pills, clock, week grid, etc.):

| Card | Why |
|------|-----|
| **[Week Planner Card Plus](https://github.com/randrcomputers/week-planner-card-plus)** | Calendar grid (required) |
| **Bubble Card** | Person pills + Add Event |
| **Config Template Card** | Today / Week / Month view |
| **card-mod** | Rounded tiles / colors |
| **Better Moment Card** | Big clock |
| **Weather Card** | Weather panel (if you use weather) |

[![Open Plus in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=randrcomputers&repository=week-planner-card-plus&category=plugin)

Plus custom repo (if needed): `https://github.com/randrcomputers/week-planner-card-plus` → category **Plugin**.

Optional: copy [`themes/skylight.yaml`](themes/skylight.yaml) into your HA themes for the same fonts/colors.

Hard-refresh the browser after install (**Ctrl+F5**).

### 2. This integration (HACS → Integrations)

[![Open this integration in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=randrcomputers&repository=my-skylight-calendar&category=integration)

1. Custom repositories → `https://github.com/randrcomputers/my-skylight-calendar` → **Integration**
2. Download **Skylight Family Calendar** → restart HA
3. **Settings → Devices & services → Add Integration → Skylight Family Calendar**
4. Walk the wizard (people, calendars, weather)
5. Open the **Family Calendar** dashboard (or follow the notification)

Missing cards show on `sensor.skylight_setup_status` and in **Settings → System → Repairs**.

Chore/todo checkboxes (dishwasher, laundry, …) are **not** part of the shared template — add those yourself if you want them.

### Stuck? One-click fix

**Developer Tools → Services → `skylight_calendar.fix_setup`**

That re-registers Plus, reinstalls the dashboard, and shows the checklist again.

Also check:

- `sensor.skylight_setup_status` → should be `ready` (attributes list anything `missing`)
- **Settings → System → Repairs**
- HACS frontend cards above are installed + hard-refresh (**Ctrl+F5**)

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
| HA Repairs | Warns if Plus or look cards (Bubble, etc.) are missing |
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
4. Confirm HACS frontend cards (Plus, Bubble, Config Template, card-mod, Better Moment, Weather)
5. Settings → Dashboards → ⋮ → Resources → URL containing `week-planner-card-plus`
6. Check **Settings → System → Repairs**

---

## Manual / classic YAML (optional)

Still available if you prefer the package-style setup:

- [`setup/setup-dashboard.yaml`](setup/setup-dashboard.yaml) checklist
- [`packages/family_calendar.yaml`](packages/family_calendar.yaml)
- [`dashboard.yaml`](dashboard.yaml)

---

## Credits

- **[@mohesles](https://github.com/mohesles)** — original DIY Skylight project
- **[@randrcomputers](https://github.com/randrcomputers)** — this fork (wizard, Week Planner Card Plus, install helpers)
- **[@FamousWolf](https://github.com/FamousWolf)** — Week Planner Card
- **[Week Planner Card Plus](https://github.com/randrcomputers/week-planner-card-plus)** · **[ICS Calendar Tools](https://github.com/randrcomputers/ics-calendar-tools)**

Community: [DIY Family Calendar (Skylight)](https://community.home-assistant.io/t/diy-family-calendar-skylight/844830)
