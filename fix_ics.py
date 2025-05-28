import requests
import yaml
from pathlib import Path
import pytz
from icalendar import Calendar
from datetime import datetime

def fix_ics_times(ics_content):
    try:
        cal = Calendar.from_ical(ics_content)
        for component in cal.walk():
            if component.name == "VEVENT":
                dtstart = component.get("DTSTART")
                dtend = component.get("DTEND")
                if hasattr(dtstart, "dt") and isinstance(dtstart.dt, datetime) and dtstart.dt.tzinfo is None:
                    component["DTSTART"].dt = pytz.timezone("Europe/Stockholm").localize(dtstart.dt)
                if hasattr(dtend, "dt") and isinstance(dtend.dt, datetime) and dtend.dt.tzinfo is None:
                    component["DTEND"].dt = pytz.timezone("Europe/Stockholm").localize(dtend.dt)
        return cal.to_ical().decode("utf-8")
    except Exception as e:
        print(f"❌ Fel i fix_ics_times: {e}")
        return ics_content

def main():
    print("🚀 Startar")
    with open("feeds.yaml", "r") as f:
        feeds = yaml.safe_load(f)

    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)

    for name, info in feeds.get("calendars", {}).items():
        url = info["url"]
        print(f"🌐 Hämtar {name} från {url}")
        try:
            r = requests.get(url, timeout=30)
            print(f"📥 Statuskod: {r.status_code}")
            print(f"📄 Förhandsvisning: {r.text[:200]}")
            r.raise_for_status()
            fixed = fix_ics_times(r.text)
            output_path = output_dir / f"{name}.ics"
            output_path.write_text(fixed, encoding="utf-8")
            print(f"✅ Sparade {output_path}")
        except Exception as e:
            print(f"❌ Fel vid hämtning av {name}: {e}")

if __name__ == "__main__":
    main()
