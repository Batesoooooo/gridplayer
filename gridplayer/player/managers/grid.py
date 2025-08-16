import contextlib
import math
from typing import NamedTuple

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout

from gridplayer.dialogs.input_dialog import QCustomSpinboxInput
from gridplayer.models.grid_state import GridState
from gridplayer.params.static import (
    FONT_SIZE_BIG_INFO,
    PLAYER_INITIAL_SIZE,
    PLAYER_MIN_VIDEO_SIZE,
    GridMode,
)
from gridplayer.player.managers.base import ManagerBase
from gridplayer.settings import Settings
from gridplayer.utils.qt import translate


class GridDimensions(NamedTuple):
    cols: int
    rows: int

    @property
    def max_size(self):
        return self.cols * self.rows


def _clear_layout(layout):
    for _ in range(layout.count()):
        l_item = layout.takeAt(0)

        sublay = l_item.layout()

        if sublay is not None:
            _clear_layout(sublay)
            sublay.deleteLater()


class GridManager(ManagerBase):
    minimum_size_changed = pyqtSignal(QSize)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._ctx.grid_state = self.grid_state

        self._grid_mode = Settings().get("playlist/grid_mode")
        self._is_grid_fit = Settings().get("playlist/is_grid_fit")
        self._grid_size = Settings().get("playlist/grid_size")

        self._grid = QGridLayout()
        self._grid.setSpacing(0)

        # Custom cell size feature
        self._custom_cell_size = None

        self._parent_widget = kwargs.get("parent_widget")

        self._minimum_size = PLAYER_INITIAL_SIZE

    def set_custom_cell_size(self, size):
        """Set custom cell size for grid cells"""
        self._custom_cell_size = size
        self.reload_video_grid()

    def get_custom_cell_size(self):
        """Get current custom cell size"""
        return self._custom_cell_size

    def reset_custom_cell_size(self):
        """Reset to default cell sizing"""
        self._custom_cell_size = None
        self.reload_video_grid()

    @property
    def widget(self):
        return self._parent_widget

    @property
    def visible_count(self):
        return len([vb for vb in self._ctx.video_blocks if vb.is_visible])

    @property
    def grid_dimensions(self):
        if self.visible_count <= 1:
            return GridDimensions(1, 1)

        if self._grid_size == 0:
            grid_size = math.ceil(math.sqrt(self.visible_count))
        else:
            grid_size = self._grid_size

        grid_slices = math.ceil(self.visible_count / grid_size)

        if self._grid_mode == GridMode.AUTO_COLS:
            cols, rows = grid_slices, grid_size
        else:
            cols, rows = grid_size, grid_slices

        return GridDimensions(cols, rows)

    @contextlib.contextmanager
    def slow_ui_operation(self):
        self.parent().setUpdatesEnabled(False)
        yield
        self.parent().setUpdatesEnabled(True)

    def grid_state(self):
        return GridState(
            mode=self._grid_mode,
            is_fit=self._is_grid_fit,
            size=self._grid_size,
        )

    def cmd_ask_grid_size(self):
        input_value = QCustomSpinboxInput(
            title=translate("Grid Size", "Grid Size"),
            label=translate("Grid Size", "Size") + ":",
            default_value=self._grid_size,
            min_value=0,
            max_value=20,
            zero_text=translate("Grid Size", "Auto"),
            parent=self.parent(),
        )

        value = input_value.get()

        if value is None:
            return

        self._grid_size = value
        Settings().set("playlist/grid_size", value)

        self.reload_video_grid()

    def cmd_set_grid_mode(self, grid_mode):
        self._grid_mode = grid_mode
        Settings().set("playlist/grid_mode", grid_mode)

        self.reload_video_grid()

    def cmd_is_grid_mode_set_to(self, grid_mode):
        return self._grid_mode == grid_mode

    def cmd_is_grid_fit(self):
        return self._is_grid_fit

    def cmd_get_grid_size(self):
        if self._grid_size == 0:
            return translate("Grid Size", "Auto")

        return str(self._grid_size)

    def cmd_switch_is_grid_fit(self):
        self._is_grid_fit = not self._is_grid_fit
        self.reload_video_grid()

    def cmd_ask_custom_cell_size(self):
        """Command to ask user for custom cell size"""
        from gridplayer.dialogs.input_dialog import QCustomSpinboxInput
        
        # Get current size as default
        current_size = self._custom_cell_size if self._custom_cell_size else QSize(300, 200)
        
        # Ask for width
        width_input = QCustomSpinboxInput(
            title=translate("Custom Cell Size", "Custom Cell Size"),
            label=translate("Custom Cell Size", "Width") + ":",
            default_value=current_size.width(),
            min_value=50,
            max_value=2000,
            parent=self.parent(),
        )
        
        width = width_input.get()
        if width is None:
            return
            
        # Ask for height
        height_input = QCustomSpinboxInput(
            title=translate("Custom Cell Size", "Custom Cell Size"),
            label=translate("Custom Cell Size", "Height") + ":",
            default_value=current_size.height(),
            min_value=50,
            max_value=2000,
            parent=self.parent(),
        )
        
        height = height_input.get()
        if height is None:
            return
            
        # Set the custom cell size
        self.set_custom_cell_size(QSize(width, height))

    def cmd_reset_custom_cell_size(self):
        """Command to reset custom cell size"""
        self.reset_custom_cell_size()

    def adapt_grid(self):
        self._reset_grid_stretch()

        if self.visible_count > 1:
            self._adjust_grid_stretch()

    def reload_video_grid(self):
        with self.slow_ui_operation():
            self._reset_video_grid()

            if not self._ctx.video_blocks:
                self._grid.activate()
                return

            self._adjust_window()
            self._adjust_cells()

            self._populate_grid()

            self.adapt_grid()

            self._grid.activate()

    def _reset_grid_stretch(self):
        for c in range(self._grid.columnCount()):
            self._grid.setColumnStretch(c, 0)

        for r in range(self._grid.rowCount()):
            self._grid.setRowStretch(r, 0)

    def _adjust_grid_stretch(self):
        if self._is_grid_fit:
            # Fit entire grid to parent widget
            for c in range(self.grid_dimensions.cols):
                self._grid.setColumnStretch(c, 1)

            for r in range(self.grid_dimensions.rows):
                self._grid.setRowStretch(r, 1)

    def _adjust_cells(self):
        for vb in self._ctx.video_blocks:
            vb.setMinimumSize(self._minimum_vb_size())

    def _populate_grid(self):
        odd_cells = self.grid_dimensions.max_size - len(self._ctx.video_blocks)

        if odd_cells == 0 or not self._is_grid_fit:
            self._fill_grid(self._ctx.video_blocks)
        else:
            if self._grid_mode == GridMode.AUTO_COLS:
                straight_cells = self.grid_dimensions.rows * (
                    self.grid_dimensions.cols - 1
                )

                self._fill_grid(self._ctx.video_blocks[:straight_cells])
                self._fill_last_col(self._ctx.video_blocks[straight_cells:])
            else:
                straight_cells = self.grid_dimensions.cols * (
                    self.grid_dimensions.rows - 1
                )

                self._fill_grid(self._ctx.video_blocks[:straight_cells])
                self._fill_last_row(self._ctx.video_blocks[straight_cells:])

    def _fill_grid(self, widgets):
        for n, w in enumerate(widgets):
            c = n % self.grid_dimensions.cols
            r = n // self.grid_dimensions.cols

            self._grid.addWidget(w, r, c)

    def _fill_last_row(self, widgets):
        last_row = QHBoxLayout()

        for w in widgets:
            last_row.addWidget(w, 1)

        last_row_num = self.grid_dimensions.rows - 1

        self._grid.addLayout(last_row, last_row_num, 0, 1, -1)

    def _fill_last_col(self, widgets):
        last_row = QVBoxLayout()

        for w in widgets:
            last_row.addWidget(w, 1)

        last_col_num = self.grid_dimensions.cols - 1

        self._grid.addLayout(last_row, 0, last_col_num, -1, 1)

    def _minimum_vb_size(self):
        if self._custom_cell_size:
            # Use custom cell size if set
            return self._custom_cell_size
        else:
            # Default minimum size calculation
            return QSize(
                self._minimum_size.width() // self.grid_dimensions.cols,
                self._minimum_size.height() // self.grid_dimensions.rows,
            )

    def _adjust_window(self):
        # Let's recalculate how big the window should be
        if self._custom_cell_size:
            # When custom cell size is set, use it to calculate window size
            new_width = self._custom_cell_size.width() * self.grid_dimensions.cols
            new_height = self._custom_cell_size.height() * self.grid_dimensions.rows
            new_size = QSize(new_width, new_height)
        else:
            # Default window size calculation
            new_size = QSize(
                max(self._minimum_size.width(), PLAYER_MIN_VIDEO_SIZE.width()),
                max(self._minimum_size.height(), PLAYER_MIN_VIDEO_SIZE.height()),
            )

        if new_size != self._minimum_size:
            self._minimum_size = new_size
            self.minimum_size_changed.emit(new_size)

    def _reset_video_grid(self):
        _clear_layout(self._grid)

        for vb in self._ctx.video_blocks:
            vb.show()

    def _format_warning_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", FONT_SIZE_BIG_INFO))
        label.setAlignment(Qt.AlignCenter)

        return label

    def set_minimum_size(self, size):
        self._minimum_size = size

    def set_grid_layout(self, parent_widget):
        parent_widget.setLayout(self._grid)