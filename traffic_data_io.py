"""
traffic_data_io.py

Pure Python translation of src/modules/trafficEstimation/dataImportExport.js.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Iterable
import csv
import io
import datetime
import webbrowser
import os


@dataclass
class TrafficRow:
    """
    One row of base inputs in the CSV file.

    Matches:
      Year, Gasoline, Diesel, BusSmall, BusLarge, TruckSmall, TruckMedium,
      TruckLarge, Special
    """
    year: int
    passengerGasoline: float
    passengerDiesel: float
    busSmall: float
    busLarge: float
    truckSmall: float
    truckMedium: float
    truckLarge: float
    truckSpecial: float


def parse_csv(text: str) -> List[TrafficRow]:
    """
    Parse CSV/TSV text into list of TrafficRow objects.

    Expected columns:
      Year, Gasoline, Diesel, BusSmall, BusLarge, TruckSmall,
      TruckMedium, TruckLarge, Special
    """
    # Normalize newlines, split by lines
    lines = text.strip().splitlines()
    if len(lines) < 2:
        raise ValueError("File must have at least a header row and one data row")

    data: List[TrafficRow] = []
    # Skip header row (index 0)
    for i in range(1, len(lines)):
        # Split by comma or tab
        parts = [p for p in csv.reader([lines[i]], delimiter=",", skipinitialspace=True)][0]
        # If there are tabs, split manually
        if len(parts) < 9:
            parts = lines[i].split("\t")

        if len(parts) < 9:
            # Skip incomplete rows
            continue

        row = TrafficRow(
            year=int(parts[0] or 0),
            passengerGasoline=float(parts[1] or 0),
            passengerDiesel=float(parts[2] or 0),
            busSmall=float(parts[3] or 0),
            busLarge=float(parts[4] or 0),
            truckSmall=float(parts[5] or 0),
            truckMedium=float(parts[6] or 0),
            truckLarge=float(parts[7] or 0),
            truckSpecial=float(parts[8] or 0),
        )
        data.append(row)

    return data


def export_to_csv(
    data: Iterable[Dict[str, Any]],
    direction: str,
) -> str:
    """
    Export data to CSV format (string), matching exportToCSV in JS.

    Each dict in `data` can contain:
      year, passengerGasoline, passengerDiesel, busSmall, busLarge,
      truckSmall, truckMedium, truckLarge, truckSpecial,
      totalAadt (optional), heavyVehicleMixPt (optional),
      mixPercents (optional dict).
    """
    headers = [
        "Year",
        "Direction",
        "Gasoline",
        "Diesel",
        "Bus Small",
        "Bus Large",
        "Truck Small",
        "Truck Medium",
        "Truck Large",
        "Special",
        "Total AADT",
        "Heavy Mix Pt (%)",
    ]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    for row in data:
        year = row.get("year", "")
        passenger_gasoline = row.get("passengerGasoline", 0) or 0
        passenger_diesel = row.get("passengerDiesel", 0) or 0
        bus_small = row.get("busSmall", 0) or 0
        bus_large = row.get("busLarge", 0) or 0
        truck_small = row.get("truckSmall", 0) or 0
        truck_medium = row.get("truckMedium", 0) or 0
        truck_large = row.get("truckLarge", 0) or 0
        truck_special = row.get("truckSpecial", 0) or 0

        # Derive Total AADT if missing
        if row.get("totalAadt") is not None:
            total_aadt = float(row["totalAadt"])
        else:
            total_aadt = float(
                (passenger_gasoline or 0)
                + (passenger_diesel or 0)
                + (bus_small or 0)
                + (bus_large or 0)
                + (truck_small or 0)
                + (truck_medium or 0)
                + (truck_large or 0)
                + (truck_special or 0)
            )

        # Derive Pt% if missing
        pt = row.get("heavyVehicleMixPt", None)
        if pt is None:
            mix_percents = row.get("mixPercents")
            if mix_percents:
                mp = mix_percents
                pt = round(
                    (mp.get("busLarge", 0)
                     + mp.get("truckMedium", 0)
                     + mp.get("truckLarge", 0)
                     + mp.get("truckSpecial", 0)),
                    2,
                )
            elif total_aadt > 0:
                f = float(bus_large or 0)
                h = float(truck_medium or 0)
                i = float(truck_large or 0)
                j = float(truck_special or 0)
                pt = round(((f + h + i + j) / total_aadt) * 100.0, 2)

        writer.writerow(
            [
                year,
                direction,
                passenger_gasoline,
                passenger_diesel,
                bus_small,
                bus_large,
                truck_small,
                truck_medium,
                truck_large,
                truck_special,
                total_aadt if total_aadt else "",
                f"{float(pt):.2f}" if pt is not None else "",
            ]
        )

    return output.getvalue()


def save_csv_to_file(csv_content: str, filename: str = "traffic_estimation.csv") -> None:
    """
    Python equivalent of downloadCSV: writes CSV content to a file on disk
    instead of triggering a browser download.
    """
    with open(filename, "w", encoding="utf-8", newline="") as f:
        f.write(csv_content)


def build_pdf_html(data: Iterable[Dict[str, Any]], title: str = "Traffic Estimation Results") -> str:
    """
    Build an HTML string suitable for printing/saving as PDF,
    mirroring exportToPDF's markup.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows_html = []
    for row in data:
        year = row.get("year", "")
        g = int(row.get("passengerGasoline", 0) or 0)
        d = int(row.get("passengerDiesel", 0) or 0)
        b_s = int(row.get("busSmall", 0) or 0)
        b_l = int(row.get("busLarge", 0) or 0)
        t_s = int(row.get("truckSmall", 0) or 0)
        t_m = int(row.get("truckMedium", 0) or 0)
        t_l = int(row.get("truckLarge", 0) or 0)
        t_sp = int(row.get("truckSpecial", 0) or 0)
        total_aadt = int(row.get("totalAadt", 0) or 0)
        pt = row.get("heavyVehicleMixPt", None)

        rows_html.append(
            f"""
            <tr>
              <td>{year}</td>
              <td>{g:,}</td>
              <td>{d:,}</td>
              <td>{b_s:,}</td>
              <td>{b_l:,}</td>
              <td>{t_s:,}</td>
              <td>{t_m:,}</td>
              <td>{t_l:,}</td>
              <td>{t_sp:,}</td>
              <td><strong>{total_aadt:,}</strong></td>
              <td><strong>{f"{float(pt):.2f}" if pt is not None else ""}</strong></td>
            </tr>
            """
        )

    rows_joined = "\n".join(rows_html)

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 20px;
      font-size: 12px;
    }}
    h1 {{
      color: #333;
      font-size: 18px;
      margin-bottom: 5px;
    }}
    .timestamp {{
      color: #666;
      font-size: 10px;
      margin-bottom: 20px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
    }}
    th, td {{
      border: 1px solid #ddd;
      padding: 8px;
      text-align: right;
    }}
    th {{
      background-color: #4CAF50;
      color: white;
      font-weight: bold;
      font-size: 11px;
    }}
    td:first-child, th:first-child {{
      text-align: center;
    }}
    tr:nth-child(even) {{
      background-color: #f9f9f9;
    }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="timestamp">Generated: {now}</div>
  <table>
    <thead>
      <tr>
        <th>Year</th>
        <th>Gasoline</th>
        <th>Diesel</th>
        <th>Bus Small</th>
        <th>Bus Large</th>
        <th>Truck Small</th>
        <th>Truck Medium</th>
        <th>Truck Large</th>
        <th>Special</th>
        <th>Total AADT</th>
        <th>Pt (%)</th>
      </tr>
    </thead>
    <tbody>
      {rows_joined}
    </tbody>
  </table>
</body>
</html>
"""
    return html


def open_pdf_preview_in_browser(data: Iterable[Dict[str, Any]], title: str = "Traffic Estimation Results") -> str:
    """
    Convenience helper: write the HTML to a temp file and open it in the browser.
    The user can then "Print → Save as PDF".

    This is the closest desktop equivalent of the JS exportToPDF behavior.
    """
    html = build_pdf_html(data, title=title)
    filename = f"traffic_estimation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open("file://" + os.path.abspath(filename))
    return filename
