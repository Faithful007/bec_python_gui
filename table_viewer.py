# table_viewer.py
import json
import os
from typing import Optional, Dict, Any, List

try:
    from speed_grade_tables import (
        build_override_from_structured_data,
        set_table_override,
        clear_table_override
    )
except ImportError:
    # Fallback if speed_grade_tables not available
    def build_override_from_structured_data(data):
        return data
    def set_table_override(pollutant, override):
        pass
    def clear_table_override(pollutant):
        pass

from data_catalog import table_state


def load_json(file: str):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, "Data", file)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TableViewer:
    ALL_FILES = [
        "pmSpeedGradeFiv.json",
        "coSpeedGradeFiv.json",
        "noxSpeedGradeFiv.json"
    ]

    def detect_pollutant(self, filename: str) -> Optional[str]:
        filename = filename.lower()
        if filename.startswith("pm"):
            return "PM"
        if filename.startswith("co"):
            return "CO"
        if filename.startswith("nox"):
            return "NOx"
        return None

    def load_table(self, file: str):
        """Load single or multiple speed-grade tables."""
        if file == "all":
            tables = []
            for f in self.ALL_FILES:
                data = load_json(f)
                if data:
                    tables.append({"file": f, "data": data})
            return tables
        else:
            return load_json(file)

    def import_all(self):
        """Equivalent to clicking 'Import All' in React."""
        for f in self.ALL_FILES:
            data = load_json(f)
            pollutant = self.detect_pollutant(f)
            if data and pollutant:
                override = build_override_from_structured_data(data)
                set_table_override(pollutant, override)

        table_state.set("ALL")
        return "All pollutant tables imported."

    def import_single(self, file: str):
        """Import one pollutant from JSON."""
        data = load_json(file)
        if not data:
            return f"Unable to load table: {file}"

        pollutant = self.detect_pollutant(file)
        if not pollutant:
            return "Cannot detect pollutant from file name."

        override = build_override_from_structured_data(data)
        set_table_override(pollutant, override)
        table_state.set(pollutant)
        return f"{pollutant} table imported."

    def clear(self, file: str):
        """Clear table override."""
        if file == "all":
            for f in self.ALL_FILES:
                pollutant = self.detect_pollutant(f)
                clear_table_override(pollutant)
        else:
            pollutant = self.detect_pollutant(file)
            clear_table_override(pollutant)

        table_state.set(None)
        return "Cleared imported table(s)."
