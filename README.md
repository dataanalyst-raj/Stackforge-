# StackForge

**Professional Steel Chimney Design Software**

Based on:
- IS 6533 (Part 1 & Part 2)
- IS 875 (Part 3)
- IS 1893

## Features

- Complete structural design of self-supporting steel chimneys
- Auto Flare Height calculation
- Auto Wind Speed & Seismic Zone from Location
- Static + Dynamic + Gust Wind Loads
- Earthquake Analysis
- Flange Design
- Base Chair Design
- Shell Stress Checks
- Dark / Light Theme
- Installable Desktop Application (PySide6)

## Project Structure

```
StackForge/
├── main.py                 # Entry point
├── app.py                  # Main window
├── ui/                     # User Interface
├── core/                   # Calculation modules (Backend)
├── utils/                  # Helpers & constants
├── data/                   # Saved projects
└── resources/              # Icons & assets
```

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

## Development Status

Version 1.0.0 - Foundation created
