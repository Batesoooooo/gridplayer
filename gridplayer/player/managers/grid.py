import gridplayer.models.grid_state as grid_state
from gridplayer.dialogs.cell_config import CellConfigDialog

class GridManager:
    def __init__(self, state: grid_state.GridState):
        self.state = state

    def customize_cell(self, row, col):
        config = self.state.custom_cell_config.get((row, col), {})
        dialog = CellConfigDialog(config)
        new_config = dialog.exec_()
        if new_config:
            self.state.custom_cell_config[(row, col)] = new_config
            self.state.save_config()

    def get_cell_span(self, row, col):
        config = self.state.custom_cell_config.get((row, col), {})
        return config.get("row_span", 1), config.get("col_span", 1)

    def get_cell_aspect_ratio(self, row, col):
        config = self.state.custom_cell_config.get((row, col), {})
        return config.get("aspect_ratio", "auto")