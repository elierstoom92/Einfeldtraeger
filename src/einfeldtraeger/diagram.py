"""Utility helpers for ASCII diagrams."""

from __future__ import annotations

from typing import Sequence


def render_diagram(xs: Sequence[float], values: Sequence[float], *, height: int = 15, width: int = 60) -> str:
    """Render an ASCII diagram for ``values`` defined over coordinates ``xs``.

    The diagram is meant for console output and gives a qualitative view of
    shear force and bending moment distributions without requiring external
    plotting libraries.
    """

    if len(xs) != len(values):
        raise ValueError("xs and values must have the same length")
    if len(xs) < 2:
        raise ValueError("Need at least two samples to render a diagram")
    if height < 3 or width < 2:
        raise ValueError("Diagram dimensions are too small")

    min_val = min(values)
    max_val = max(values)
    span = max(abs(min_val), abs(max_val))
    if span == 0:
        span = 1.0

    # Normalise values to fit within the diagram height.
    def normalise(value: float) -> int:
        scaled = value / span
        return int(round((height - 1) / 2 * scaled))

    zero_row = height // 2
    grid = [[" " for _ in range(width)] for _ in range(height)]

    step = (len(xs) - 1) / (width - 1)
    for column in range(width):
        index = min(len(xs) - 1, int(round(column * step)))
        row_offset = normalise(values[index])
        row = zero_row - row_offset
        row = max(0, min(height - 1, row))
        grid[row][column] = "●"

    # Draw zero axis
    for column in range(width):
        if grid[zero_row][column] == "●":
            continue
        grid[zero_row][column] = "─"

    grid[zero_row][0] = "┼"
    grid[zero_row][-1] = "┤"

    top_label = f"{max_val:.2f}"
    bottom_label = f"{min_val:.2f}"

    lines = [top_label.rjust(width)]
    lines.extend("".join(row) for row in grid)
    lines.append(bottom_label.rjust(width))
    return "\n".join(lines)


__all__ = ["render_diagram"]
