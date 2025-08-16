class CellConfigDialog:
    def __init__(self, config):
        self.config = config

    def exec_(self):
        # Pop up a dialog to select row_span, col_span, aspect_ratio
        # Return updated config or None if cancelled
        return {
            "row_span": self.config.get("row_span", 1),
            "col_span": self.config.get("col_span", 1),
            "aspect_ratio": self.config.get("aspect_ratio", "auto"),
        }