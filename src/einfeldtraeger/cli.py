"""Command line interface for the Einfeldträger helper."""

from __future__ import annotations

import argparse
from typing import List

from .beam import PointLoad, SimplySupportedBeam
from .diagram import render_diagram


def parse_point_load(value: str) -> PointLoad:
    try:
        magnitude_str, position_str = value.split(",")
        magnitude = float(magnitude_str)
        position = float(position_str)
    except ValueError as exc:  # pragma: no cover - defensive programming
        raise argparse.ArgumentTypeError(
            "Point loads have to be supplied as '<magnitude>,<position>'"
        ) from exc
    return PointLoad(magnitude=magnitude, position=position)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Berechnung eines Einfeldträgers mit Strecken- und Einzellast",
    )
    parser.add_argument("length", type=float, help="Gesamtlänge des Trägers in m")
    parser.add_argument(
        "--streckenlast",
        "--distributed-load",
        dest="distributed_load",
        type=float,
        default=0.0,
        help="Konstante Streckenlast q in kN/m (Standard: 0)",
    )
    parser.add_argument(
        "--einzellast",
        "--point-load",
        dest="point_loads",
        action="append",
        type=parse_point_load,
        default=[],
        metavar="P,x",
        help="Einzellast in kN sowie Position in m (z.B. 15,2.5). Mehrfach angaben möglich.",
    )
    parser.add_argument(
        "--punkte",
        dest="points",
        type=int,
        default=81,
        help="Anzahl der Auswerte-Punkte für die Diagramme",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    beam = SimplySupportedBeam(
        length=args.length,
        distributed_load=args.distributed_load,
        point_loads=args.point_loads,
    )

    xs, shear, moment = beam.evaluate(points=args.points)
    reaction_left = beam.reaction_left
    reaction_right = beam.reaction_right

    print("Einfeldträger mit L = {:.3f} m".format(beam.length))
    if args.distributed_load:
        print("Streckenlast q = {:.3f} kN/m".format(args.distributed_load))
    if args.point_loads:
        for idx, load in enumerate(args.point_loads, start=1):
            print(
                "Einzellast {}: P = {:.3f} kN @ x = {:.3f} m".format(
                    idx, load.magnitude, load.position
                )
            )
    print("Auflagerreaktion links:  {:.3f} kN".format(reaction_left))
    print("Auflagerreaktion rechts: {:.3f} kN".format(reaction_right))

    print("\nQuerkraftverlauf V(x):")
    print(render_diagram(xs, shear))

    print("\nMomentenverlauf M(x):")
    print(render_diagram(xs, moment))

    max_shear_pos, max_shear_val = beam.max_shear()
    max_moment_pos, max_moment_val = beam.max_moment()
    print(
        "\nMaximale Querkraft: {:+.3f} kN bei x = {:.3f} m".format(
            max_shear_val, max_shear_pos
        )
    )
    print(
        "Maximales Moment: {:+.3f} kNm bei x = {:.3f} m".format(
            max_moment_val, max_moment_pos
        )
    )

    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
