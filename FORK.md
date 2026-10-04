# Fork notes

## Upstream

https://github.com/mohesles/my-skylight-calendar

## This fork adds

1. **HACS integration** `custom_components/skylight_calendar` — visual config-flow wizard  
2. Dashboard uses **Week Planner Card Plus**  
3. Checklist dashboard at `setup/setup-dashboard.yaml` (manual path)  
4. Generated dashboard backup at `/config/skylight_calendar/dashboard_generated.yaml`

## Publish

```bash
git remote rename origin upstream
git remote add origin https://github.com/YOUR_USER/my-skylight-calendar.git
git add -A
git commit -m "Add Skylight setup wizard integration and Week Planner Card Plus"
git push -u origin main
```

HACS users add your fork as a **custom repository** (Integration).
