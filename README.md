# GridPlayer Cell Customization Feature

## Cell Customization

You can now customize individual grid cells:
- Set row and column span for each cell.
- Choose aspect ratio per cell.
- Right-click a cell and select **Customize Cell**.

Cell customizations are saved in the grid state and persist across sessions.

## How to Use

1. Right-click any grid cell.
2. Choose **Customize Cell** from the context menu.
3. Set row span, column span, and aspect ratio.
4. Save your changes.

For developers: see `gridplayer/models/grid_state.py` for state management and `gridplayer/player/managers/grid.py` for customization logic.