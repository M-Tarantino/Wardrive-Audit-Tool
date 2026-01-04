# 🛡️ Wardrive Audit Tool (v18.0)

A professional-grade Python tool designed to transform raw wireless survey data into actionable security intelligence. This tool parses WiGLE CSV exports to identify infrastructure vulnerabilities, analyze RF spectrum congestion, and visualize geographical distribution.

## 🚀 Overview
As part of my transition into the IT & Cybersecurity field, I developed this implementation to bridge the gap between raw data collection and professional security reporting. The tool processes thousands of data points to provide a high-level executive summary of the wireless landscape.

## ✨ Key Features
- **Vendor Aggregation:** Intelligently groups fragmented MAC OUIs into major brands (e.g., AVM, Apple, TP-Link) for clear market share analysis.
- **Security Matrix:** Detailed breakdown of encryption standards (WPA3, WPA2, WEP) and critical risks like **WPS exposure**.
- **Adaptive Geocoding:** Features two modes—**Turbo** (5km clusters) for rapid overviews and **Detail** (500m clusters) for localized analysis.
- **RF Insights:** Automates channel load assessment to identify spectrum interference.
- **Telemetry Analysis:** Calculates total survey distance (Haversine formula) and captures precise run-time metadata.

## 🛠️ How To Use

### 1. Prerequisites
- Python 3.x
- An active internet connection for the initial setup (OUI database download) and geo-mapping.

### 2. Installation
Clone this repository to your local machine or Termux environment:
git clone https://github.com/YOUR_USERNAME/WardriveAudit.git
cd WardriveAudit

### 3. Running the Audit
Execute the script by passing your WiGLE CSV export as an argument:
python WardriveAudit.py your_wigle_file.csv

### 4. Output
The tool generates a detailed Markdown report (Wardriving_Audit_YYYYMMDD_HHMM.md) containing:
- Geographical signal distribution.
- Aggregated vendor inventory.
- Security risk & encryption tables.
- IoT (BLE) and Cellular (LTE/5G) intelligence.

## 📊 Sample Insights
In a recent audit covering 207 km, this tool successfully:
- Parsed 48,242 data nodes.
- Identified 10,764 WPS-vulnerable access points.
- Mapped signal density across multiple districts in real-time.

## ⚖️ License & Ethics
This project is for educational and authorized security auditing purposes only. Always respect local laws and privacy regulations regarding wireless scanning.
