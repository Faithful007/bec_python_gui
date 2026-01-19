# This is a helper to show the exact code to insert

# After line 51 (after pass), insert:

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
