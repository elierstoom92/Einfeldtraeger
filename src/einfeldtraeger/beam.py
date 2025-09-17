"""Beam model for a simply supported beam (Einfeldträger).

The implementation is intentionally light-weight and focuses on the two
load cases that are most commonly encountered in basic structural
analysis exercises:

* A constant distributed load that spans the entire beam length.
* A single point load located at an arbitrary position on the beam.

Both load types can be combined thanks to the principle of
superposition.  The coordinate system assumes the left support at
``x = 0`` and the right support at ``x = L``.  Downward acting loads are
positive and the resulting reactions are upward acting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class PointLoad:
    """Representation of a single point load.

    Attributes
    ----------
    magnitude:
        Magnitude of the load (positive for downward acting loads).
    position:
        Distance of the load from the left support measured in metres.
    """

    magnitude: float
    position: float


class SimplySupportedBeam:
    """Model of an Einfeldträger with basic load cases.

    Parameters
    ----------
    length:
        Total span of the beam in metres.
    distributed_load:
        Intensity ``w`` of a constant distributed load in kN/m (optional).
        ``w`` is considered to act across the entire span.
    point_loads:
        Optional sequence of :class:`PointLoad` instances.
    """

    def __init__(
        self,
        length: float,
        *,
        distributed_load: float = 0.0,
        point_loads: Iterable[PointLoad] | None = None,
    ) -> None:
        if length <= 0:
            raise ValueError("Beam length has to be positive.")

        self.length = float(length)
        self.distributed_load = float(distributed_load)
        self.point_loads: Tuple[PointLoad, ...] = tuple(point_loads or [])
        for load in self.point_loads:
            if not (0.0 <= load.position <= self.length):
                raise ValueError(
                    "Point load position has to be within the beam span."
                )

        self._reaction_left, self._reaction_right = self._compute_support_reactions()

    # ------------------------------------------------------------------
    # Support reactions
    # ------------------------------------------------------------------
    def _compute_support_reactions(self) -> Tuple[float, float]:
        """Compute reactions at the left and right support."""

        r_left = 0.0
        r_right = 0.0

        if self.distributed_load:
            total = self.distributed_load * self.length
            r_left += total / 2.0
            r_right += total / 2.0

        for load in self.point_loads:
            proportion = load.position / self.length
            r_left += load.magnitude * (1.0 - proportion)
            r_right += load.magnitude * proportion

        return r_left, r_right

    @property
    def reaction_left(self) -> float:
        """Reaction at the left support (upward positive)."""

        return self._reaction_left

    @property
    def reaction_right(self) -> float:
        """Reaction at the right support (upward positive)."""

        return self._reaction_right

    # ------------------------------------------------------------------
    # Shear force and bending moment
    # ------------------------------------------------------------------
    def shear_force(self, x: float) -> float:
        """Shear force ``V(x)`` at position ``x`` measured from the left support."""

        if not (0.0 <= x <= self.length):
            raise ValueError("x has to lie within the beam span")

        shear = self._reaction_left
        if self.distributed_load:
            shear -= self.distributed_load * x

        for load in self.point_loads:
            if x >= load.position:
                shear -= load.magnitude

        return shear

    def bending_moment(self, x: float) -> float:
        """Bending moment ``M(x)`` at position ``x`` measured from the left support."""

        if not (0.0 <= x <= self.length):
            raise ValueError("x has to lie within the beam span")

        moment = self._reaction_left * x
        if self.distributed_load:
            moment -= 0.5 * self.distributed_load * x * x

        for load in self.point_loads:
            if x >= load.position:
                moment -= load.magnitude * (x - load.position)

        return moment

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def evaluate(self, points: int = 50) -> Tuple[List[float], List[float], List[float]]:
        """Evaluate ``V(x)`` and ``M(x)`` at evenly spaced points along the span."""

        if points < 2:
            raise ValueError("Need at least two evaluation points to form diagrams.")

        xs: List[float] = []
        vs: List[float] = []
        ms: List[float] = []
        step = self.length / (points - 1)

        for idx in range(points):
            x = idx * step
            if idx == points - 1:  # Prevent cumulative floating point errors
                x = self.length
            xs.append(x)
            vs.append(self.shear_force(x))
            ms.append(self.bending_moment(x))

        return xs, vs, ms

    def max_shear(self, points: int = 1001) -> Tuple[float, float]:
        """Return maximum absolute shear and its position."""

        xs, vs, _ = self.evaluate(points)
        magnitude = max(vs, key=abs)
        index = vs.index(magnitude)
        return xs[index], magnitude

    def max_moment(self, points: int = 1001) -> Tuple[float, float]:
        """Return maximum absolute bending moment and its position."""

        xs, _, ms = self.evaluate(points)
        magnitude = max(ms, key=abs)
        index = ms.index(magnitude)
        return xs[index], magnitude


__all__ = ["PointLoad", "SimplySupportedBeam"]
