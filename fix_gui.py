#!/usr/bin/env python
"""Script to fix main_gui.py: remove pressure table and add FocusOut handling."""

import re

# Read the file
with open('main_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the pressure calculations table section (lines 3798-3824)
# Find and replace the pressure table block with just empty line
pressure_block = r'''            # Add pressure calculations table \(ΔPr, ΔPm, ΔPt, ΔPq\)
            try:
                text_widget\.insert\("end", "Table: Pressure Calculations\\n\\n"\)
                pressure_headers = \[
                    "ΔPr \(Pa\)",
                    "ΔPm \(Pa\)",
                    "ΔPt \(Pa\)",
                    "ΔPq \(Pa\)",
                \]
                pressure_col_widths = \[15, 15, 15, 15\]
                
                def format_pressure_row\(values\):
                    return " "\.join\(str\(val\)\.ljust\(width\) for val, width in zip\(values, pressure_col_widths\)\)
                
                text_widget\.insert\("end", format_pressure_row\(pressure_headers\) \+ "\\n"\)
                text_widget\.insert\("end", format_pressure_row\(\["-" \* \(w - 1\) for w in pressure_col_widths\]\) \+ "\\n"\)
                
                pressure_data_row = \[
                    f"\{res\.delta_Pr:\.4f\}",
                    f"\{res\.delta_Pm:\.4f\}",
                    f"\{res\.delta_Pt:\.4f\}",
                    f"\{res\.delta_Pq:\.4f\}",
                \]
                text_widget\.insert\("end", format_pressure_row\(pressure_data_row\) \+ "\\n"\)
                text_widget\.insert\("end", "\\n"\)
            except Exception as e:
                text_widget\.insert\("end", f"Error displaying pressure calculations: \{str\(e\)\}\\n\\n"\)
'''

# Simpler approach - use literal string replacement
old_pressure_section = '''            # Add pressure calculations table (ΔPr, ΔPm, ΔPt, ΔPq)
            try:
                text_widget.insert("end", "Table: Pressure Calculations\\n\\n")
                pressure_headers = [
                    "ΔPr (Pa)",
                    "ΔPm (Pa)",
                    "ΔPt (Pa)",
                    "ΔPq (Pa)",
                ]
                pressure_col_widths = [15, 15, 15, 15]
                
                def format_pressure_row(values):
                    return " ".join(str(val).ljust(width) for val, width in zip(values, pressure_col_widths))
                
                text_widget.insert("end", format_pressure_row(pressure_headers) + "\\n")
                text_widget.insert("end", format_pressure_row(["-" * (w - 1) for w in pressure_col_widths]) + "\\n")
                
                pressure_data_row = [
                    f"{res.delta_Pr:.4f}",
                    f"{res.delta_Pm:.4f}",
                    f"{res.delta_Pt:.4f}",
                    f"{res.delta_Pq:.4f}",
                ]
                text_widget.insert("end", format_pressure_row(pressure_data_row) + "\\n")
                text_widget.insert("end", "\\n")
            except Exception as e:
                text_widget.insert("end", f"Error displaying pressure calculations: {str(e)}\\n\\n")
'''

# Try finding without the \\n escapes (they're actual newlines in file)
pressure_section_to_find = """            # Add pressure calculations table (ΔPr, ΔPm, ΔPt, ΔPq)
            try:
                text_widget.insert("end", "Table: Pressure Calculations\\n\\n")
                pressure_headers = [
                    "ΔPr (Pa)",
                    "ΔPm (Pa)",
                    "ΔPt (Pa)",
                    "ΔPq (Pa)",
                ]
                pressure_col_widths = [15, 15, 15, 15]
                
                def format_pressure_row(values):
                    return " ".join(str(val).ljust(width) for val, width in zip(values, pressure_col_widths))
                
                text_widget.insert("end", format_pressure_row(pressure_headers) + "\\n")
                text_widget.insert("end", format_pressure_row(["-" * (w - 1) for w in pressure_col_widths]) + "\\n")
                
                pressure_data_row = [
                    f"{res.delta_Pr:.4f}",
                    f"{res.delta_Pm:.4f}",
                    f"{res.delta_Pt:.4f}",
                    f"{res.delta_Pq:.4f}",
                ]
                text_widget.insert("end", format_pressure_row(pressure_data_row) + "\\n")
                text_widget.insert("end", "\\n")
            except Exception as e:
                text_widget.insert("end", f"Error displaying pressure calculations: {str(e)}\\n\\n")
"""

if pressure_section_to_find in content:
    print("Found pressure section - removing it...")
    content = content.replace(pressure_section_to_find, "")
else:
    print("WARNING: Could not find exact pressure section - trying with raw strings...")
    # Try with actual newlines (no escaping)
    test_find = """            # Add pressure calculations table (ΔPr, ΔPm, ΔPt, ΔPq)
            try:
                text_widget.insert("end", "Table: Pressure Calculations\n\n")"""
    if test_find in content:
        print("Found start of pressure section")

# 2. Add FocusOut handler function to NumericValidator class
focusout_method = '''    @staticmethod
    def default_to_zero_on_focusout(event):
        """Set field to 0 if empty when focus is lost."""
        entry = event.widget
        try:
            value = entry.get().strip()
            if value == "":
                entry.delete(0, tk.END)
                entry.insert(0, "0")
                # Update the associated variable
                var_name = entry.cget('textvariable')
                if var_name:
                    entry.tk.setvar(var_name, '0')
        except Exception:
            pass

    '''

# Find the NumericValidator class and add after clear_on_focus
insert_after = '''        except Exception:
            pass
    @staticmethod
    def check_valid_numbers'''

if insert_after in content:
    print("Found insertion point for FocusOut method...")
    content = content.replace(insert_after, 
        '''        except Exception:
            pass
    
    @staticmethod
    def default_to_zero_on_focusout(event):
        """Set field to 0 if empty when focus is lost."""
        entry = event.widget
        try:
            value = entry.get().strip()
            if value == "":
                entry.delete(0, tk.END)
                entry.insert(0, "0")
                # Update the associated variable
                var_name = entry.cget('textvariable')
                if var_name:
                    entry.tk.setvar(var_name, '0')
        except Exception:
            pass

    @staticmethod
    def check_valid_numbers''')
    print("Added FocusOut method!")

# Write the modified content back
with open('main_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! Modified main_gui.py")
