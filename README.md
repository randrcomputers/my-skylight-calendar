# DIY Smart Home Family Calendar (Skylight-style)

[![Week Planner Card Plus](https://img.shields.io/badge/Uses-Week%20Planner%20Card%20Plus-41BDF5)](https://github.com/randrcomputers/week-planner-card-plus)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)

Fork of [mohesles/my-skylight-calendar](https://github.com/mohesles/my-skylight-calendar) with a **visual setup wizard** and **[Week Planner Card Plus](https://github.com/randrcomputers/week-planner-card-plus)**.

![Skylight calendar](assets/main_view.jpeg)

---

## Recommended install (wizard)

The wizard creates filter switches, a view selector, optional **Local Calendars**, writes a ready dashboard file, and tries to install a Lovelace dashboard — so you don’t hunt `# <--- UPDATE THIS ENTITY` markers.

### 1. Frontend cards (HACS)

Install under **HACS → Frontend**, then **Ctrl+F5**:

| Card | Required |
|------|----------|
| **[Week Planner Card Plus](https://github.com/randrcomputers/week-planner-card-plus)** | Yes |
| Bubble Card | Yes |
| Config Template Card | Yes |
| card-mod | Yes |
| Better Moment Card | Yes |

### 2. Install this integration (HACS)

1. HACS → **Integrations** → ⋮ → **Custom repositories**
2. Add this repo URL — category **Integration**
3. Download **Skylight Family Calendar**
4. Restart Home Assistant

### 3. Run the wizard

1. **Settings → Devices & services → Add Integration → Skylight Family Calendar**
2. Choose how many people
3. For each person: name, optional existing calendar (or leave empty to auto-create Local Calendar), color
4. Optional: Family / Holidays / Birthdays calendars + weather
5. Finish → create calendars + install dashboard

### 4. Open the calendar

- Sidebar: **Family Calendar** (if auto-install worked), **or**
- Paste `/config/skylight_calendar/dashboard_generated.yaml` into a new dashboard (Raw editor)

### 5. Check status

Entity `sensor.skylight_setup_status`:

- `ready` — calendars/helpers look good  
- `needs_attention` — see attribute `missing`

Services:

- `skylight_calendar.install_dashboard` — regenerate / reinstall dashboard  
- `skylight_calendar.create_missing_calendars` — create any still-missing Local Calendars  

---

## What the wizard creates

| Item | Entity / location |
|------|-------------------|
| View selector | `select.skylight_view` |
| Show/hide toggles | `switch.skylight_filter_<name>` |
| Setup sensor | `sensor.skylight_setup_status` |
| Local calendars | When enabled & missing |
| Dashboard | Lovelace path (default `skylight-calendar`) + YAML backup under `/config/skylight_calendar/` |

Add / Edit / Delete use **Week Planner Card Plus** built-in dialogs (tap empty day or an event). No Browser Mod popup required for the wizard dashboard.

Optional Local `.ics` helper: [ICS Calendar Tools](https://github.com/randrcomputers/ics-calendar-tools).

---

## Manual / classic install (still available)

If you prefer the original YAML package approach:

1. Use [`setup/setup-dashboard.yaml`](setup/setup-dashboard.yaml) checklist  
2. Copy [`packages/family_calendar.yaml`](packages/family_calendar.yaml)  
3. Paste [`dashboard.yaml`](dashboard.yaml) (already uses `week-planner-card-plus`)

See older steps in git history / upstream README style docs in [`FORK.md`](FORK.md).

---

## Hardware

Any HD display / tablet in kiosk mode. Original build used a touchscreen + mini PC.

---

## Credits

- **[@mohesles](https://github.com/mohesles)** — original DIY Skylight project  
- **[@FamousWolf](https://github.com/FamousWolf)** — Week Planner Card  
- **[Week Planner Card Plus](https://github.com/randrcomputers/week-planner-card-plus)** · **[ICS Calendar Tools](https://github.com/randrcomputers/ics-calendar-tools)**

Community: [DIY Family Calendar (Skylight)](https://community.home-assistant.io/t/diy-family-calendar-skylight/844830)
