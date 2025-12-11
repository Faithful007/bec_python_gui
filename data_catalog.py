# data_catalog.py
import json
import os
from typing import Optional, Dict, Any, List

from speed_grade_tables import (
    build_override_from_structured_data,
    set_table_override,
    clear_table_override
)


class ImportedTableState:
    """
    This replaces React Context: useImportedTable()
    Stores the currently-imported pollutant.
    """
    def __init__(self):
        self.imported_pollutant: Optional[str] = None

    def set(self, pollutant: Optional[str]):
        self.imported_pollutant = pollutant


# Global shared state
table_state = ImportedTableState()


def load_json(file: str) -> Optional[Dict[str, Any]]:
    """Load JSON from the Data folder in the main directory."""
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, "Data", file)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


DATA_OPTIONS = [
    {"name": "PM Correction Factor", "file": "pmSpeedGradeFiv.json", "pollutant": "PM"},
    {"name": "CO Correction Factor", "file": "coSpeedGradeFiv.json", "pollutant": "CO"},
    {"name": "NOx Correction Factor", "file": "noxSpeedGradeFiv.json", "pollutant": "NOx"},
    {"name": "All Pollutants", "file": "all", "pollutant": "ALL"},
]


class DataCatalog:
    """Python version of the DataCatalog React component."""

    ALL_FILES = [
        ("pmSpeedGradeFiv.json", "PM"),
        ("coSpeedGradeFiv.json", "CO"),
        ("noxSpeedGradeFiv.json", "NOx"),
    ]

    def import_option(self, option: Dict[str, str]):
        """Handle pollutant import selection."""
        pollutant = option["pollutant"]

        try:
            if pollutant == "ALL":
                self._import_all_pollutants()
                table_state.set("ALL")
                return "Imported ALL pollutants successfully."

            # Import one pollutant
            data = load_json(option["file"])
            if not data:
                raise FileNotFoundError(f"Could not load file: {option['file']}")

            override = build_override_from_structured_data(data)
            set_table_override(pollutant, override)
            table_state.set(pollutant)
            return f"{pollutant} imported successfully."

        except Exception as e:
            return f"Error: {str(e)}"

    def _import_all_pollutants(self):
        """Helper for importing all JSON tables."""
        for file, pollutant in self.ALL_FILES:
            data = load_json(file)
            if data:
                override = build_override_from_structured_data(data)
                set_table_override(pollutant, override)

    def clear_all(self):
        """Clear all pollutant overrides."""
        for _, pollutant in self.ALL_FILES:
            clear_table_override(pollutant)

        table_state.set(None)
        return "Cleared all imported pollutant tables."
