#!/usr/bin/env python
"""Add FocusOut bindings to Entry widgets."""

with open('main_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Bind to TunnelGeometry entries (after .bind('<FocusIn>', NumericValidator.clear_on_focus))
tunnel_focusin = "ent.bind('<FocusIn>', NumericValidator.clear_on_focus)"
tunnel_new = """ent.bind('<FocusIn>', NumericValidator.clear_on_focus)
                ent.bind('<FocusOut>', NumericValidator.default_to_zero_on_focusout)"""

if tunnel_focusin in content:
    print("Binding FocusOut to TunnelGeometry entries...")
    content = content.replace(tunnel_focusin, tunnel_new)
else:
    print("WARNING: Could not find TunnelGeometry FocusIn binding")

# 2. Bind to elevation entries
elev_focusin = "elev_entry1.bind('<FocusIn>', NumericValidator.clear_on_focus)"
elev_new = """elev_entry1.bind('<FocusIn>', NumericValidator.clear_on_focus)
        elev_entry1.bind('<FocusOut>', NumericValidator.default_to_zero_on_focusout)"""

if elev_focusin in content:
    print("Binding FocusOut to elevation entry 1...")
    content = content.replace(elev_focusin, elev_new)

# Same for elev_entry2
elev2_focusin = "elev_entry2.bind('<FocusIn>', NumericValidator.clear_on_focus)"
elev2_new = """elev_entry2.bind('<FocusIn>', NumericValidator.clear_on_focus)
        elev_entry2.bind('<FocusOut>', NumericValidator.default_to_zero_on_focusout)"""

if elev2_focusin in content:
    print("Binding FocusOut to elevation entry 2...")
    content = content.replace(elev2_focusin, elev2_new)

# 3. Bind to traffic entry fields (after the loop binding FocusIn)
traffic_focusin = "entry.bind('<FocusIn>', NumericValidator.clear_on_focus)"
traffic_new = """entry.bind('<FocusIn>', NumericValidator.clear_on_focus)
            entry.bind('<FocusOut>', NumericValidator.default_to_zero_on_focusout)"""

if traffic_focusin in content:
    print("Binding FocusOut to traffic entry fields...")
    content = content.replace(traffic_focusin, traffic_new)
else:
    print("WARNING: Could not find traffic FocusIn binding")

# Write back
with open('main_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! Added FocusOut bindings")
