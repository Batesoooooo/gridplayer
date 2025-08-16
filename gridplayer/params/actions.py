ACTIONS = {
    "Set Custom Cell Size": {
        "title": "Set Custom Cell Size",
        "icon": "cell-size",  # Provide icon file or use a default one
        "func": "ask_custom_cell_size",
    },
    "Reset Custom Cell Size": {
        "title": "Reset Custom Cell Size",
        "icon": "cell-size-reset",
        "func": "reset_custom_cell_size",
    },
    # Add other existing actions below
    "Size: %v": {
        "title": "Grid Size",
        "icon": "grid-size",
        "func": "ask_grid_size",
    },
    "Fit Grid": {
        "title": "Fit Grid",
        "icon": "grid-fit",
        "func": "switch_is_grid_fit",
    },
    # ... (add any additional existing actions here) ...
}