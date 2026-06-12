#!/usr/bin/env python3
"""
Entry point for Ansu Invest Scraper & Dashboard.

Usage:
    python run.py scrape          # Fetch ALL data
    python run.py dashboard       # Launch Streamlit dashboard
    python run.py all             # Scrape then launch dashboard
    python run.py desktop         # Launch the desktop launcher app
"""
import sys
import subprocess
import os


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    cmd = args[0]
    base = os.path.dirname(os.path.abspath(__file__))

    if cmd == "scrape":
        print("Starting full scrape (all pages)...")
        from scraper.runner import run_all
        run_all()
        print("Scrape complete.")

    elif cmd == "dashboard":
        print("Launching dashboard...")
        subprocess.run(["streamlit", "run", os.path.join(base, "dashboard", "app.py")])

    elif cmd == "all":
        print("Starting scrape, then dashboard...")
        from scraper.runner import run_all
        run_all()
        print("Scrape complete. Launching dashboard...")
        subprocess.run(["streamlit", "run", os.path.join(base, "dashboard", "app.py")])

    elif cmd == "desktop":
        print("Launching desktop app...")
        subprocess.Popen(["pythonw", os.path.join(base, "launcher.pyw")])

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
