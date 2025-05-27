import requests
import yaml
from pathlib import Path

def fix_ics_times(ics_content):
    # Placeholder: här kan du lägga in logik för att fixa tidzoner om det behövs
    return ics_content

def main():
    with open("feeds.yaml", "r") as f:
        feeds = yaml.safe_load(f)

    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)

    for feed in feeds:
        name = feed["name"]
        url = feed["url"]
        print(f"Hämtar {name} från {url}")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            fixed = fix_ics_times(r.text)
            (output_dir / f"{name}.ics").write_text(fixed, encoding="utf-8")
            print(f"✔️  Sparade {name}.ics")
        except Exception as e:
            print(f"❌ Fel vid hämtning av {name}: {e}")

if __name__ == "__main__":
    main()
