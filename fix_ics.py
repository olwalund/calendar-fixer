import requests
import yaml
import pytz
from icalendar import Calendar
from pathlib import Path
from datetime import datetime
from io import StringIO

LOCAL_TZ = pytz.timezone("Europe/Stockholm")

def fix_ics_times(ics_content):
    cal = Calendar.from_ical(ics_content)
    new_cal = Calendar()

    for k, v in cal.items():
        new_cal.add(k, v)

    for component in cal.walk():
        if component.name == "VEVENT":
            for time_key in ("DTSTART", "DTEND", "DTSTAMP"):
                if time_key in component:
                    dt = component.get(time_key).dt
                    if isinstance(dt, datetime):
                        if dt.tzinfo is None:
                            # Anta att den är UTC, konvertera till lokal tid
                            dt = pytz.utc.localize(dt).astimezone(LOCAL_TZ)
                        else:
                            dt = dt.astimezone(LOCAL_TZ)
                        component[time_key].dt = dt
        new_cal.add_component(component)

    return new_cal.to_ical().decode("utf-8")

def main():
    print("🔄 Startar script...")
    with open("feeds.yaml", "r") as f:
        feeds = yaml.safe_load(f)

    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)

    for name, info in feeds.get("calendars", {}).items():
        url = info["url"]
        print(f"🌐 Hämtar {name} från {url}")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            fixed = fix_ics_times(r.text)
            output_path = output_dir / f"{name}.ics"
            output_path.write_text(fixed, encoding="utf-8")
            print(f"✅ Sparade {output_path}")
        except Exception as e:
            print(f"❌ Fel vid hämtning av {name}: {e}")

if __name__ == "__main__":
    main()
