#!/usr/bin/env python3
# Copyright 2026 Araco Hexapod contributors
# SPDX-License-Identifier: MIT

"""Generate the technical SVG figures embedded by the root README."""

from __future__ import annotations

from html import escape
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs" / "assets" / "readme"

INK = "#172233"
MUTED = "#5b6678"
GRID = "#d9e0ea"
PALE = "#f5f7fb"
BLUE = "#3977d4"
TEAL = "#168c7a"
ORANGE = "#dc6b32"
PURPLE = "#7457c8"
RED = "#c94d58"
WHITE = "#ffffff"


class Svg:
    def __init__(self, width: int, height: int, title: str, description: str):
        self.width = width
        self.height = height
        self.items = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f"<title id=\"title\">{escape(title)}</title>",
            f"<desc id=\"desc\">{escape(description)}</desc>",
            "<defs>",
            f'<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>',
            f'<marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{BLUE}"/></marker>',
            f'<marker id="arrow-orange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{ORANGE}"/></marker>',
            "</defs>",
            f'<rect width="{width}" height="{height}" fill="{WHITE}"/>',
        ]

    def add(self, value: str) -> None:
        self.items.append(value)

    def text(
        self, x: float, y: float, value: str, *, size: int = 18,
        weight: int = 400, fill: str = INK, anchor: str = "start",
        family: str = "Inter,Segoe UI,Arial,sans-serif",
    ) -> None:
        self.add(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(value)}</text>'
        )

    def line(
        self, x1: float, y1: float, x2: float, y2: float, *,
        stroke: str = INK, width: float = 2, dash: str | None = None,
        marker: str | None = None,
    ) -> None:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        marker_attr = f' marker-end="url(#{marker})"' if marker else ""
        self.add(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{width}" stroke-linecap="round"'
            f'{dash_attr}{marker_attr}/>'
        )

    def rect(
        self, x: float, y: float, width: float, height: float, *,
        fill: str = PALE, stroke: str = GRID, radius: float = 12,
        stroke_width: float = 1.5,
    ) -> None:
        self.add(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )

    def circle(
        self, x: float, y: float, radius: float, *, fill: str = WHITE,
        stroke: str = INK, stroke_width: float = 2,
    ) -> None:
        self.add(
            f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )

    def polyline(
        self, points: list[tuple[float, float]], *, stroke: str = INK,
        width: float = 3, fill: str = "none", dash: str | None = None,
    ) -> None:
        values = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<polyline points="{values}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{dash_attr}/>'
        )

    def finish(self) -> str:
        return "\n".join([*self.items, "</svg>", ""])


def title(svg: Svg, heading: str, subtitle: str) -> None:
    svg.text(44, 48, heading, size=27, weight=600)
    svg.text(44, 77, subtitle, size=15, fill=MUTED)


def node(svg: Svg, x: float, y: float, width: float, height: float, heading: str, body: str, color: str) -> None:
    svg.rect(x, y, width, height, fill=WHITE, stroke=color, radius=14, stroke_width=2)
    svg.add(f'<rect x="{x}" y="{y}" width="8" height="{height}" rx="4" fill="{color}"/>')
    svg.text(x + 24, y + 34, heading, size=18, weight=600)
    svg.text(x + 24, y + 61, body, size=14, fill=MUTED)


def system_overview() -> str:
    svg = Svg(1200, 405, "Araco software path", "The high-level path from operator input to a replaceable robot backend and physical feedback.")
    title(svg, "From motion intent to 25 controlled joints", "The locomotion mathematics is independent of whether the backend is Gazebo or future hardware.")
    specs = [
        (44, "Operator input", "joystick or keyboard", BLUE),
        (274, "Motion intent", "velocity + body pose", TEAL),
        (504, "Command boundary", "selection + validation", PURPLE),
        (734, "Locomotion", "body · gait · IK", ORANGE),
        (964, "ros2_control", "24 leg + 1 gimbal", RED),
    ]
    for x, heading, body, color in specs:
        node(svg, x, 125, 190, 88, heading, body, color)
    for x in (234, 464, 694, 924):
        svg.line(x + 8, 169, x + 35, 169, stroke=INK, width=2, marker="arrow")
    svg.rect(680, 277, 476, 78, fill=PALE, stroke=GRID, radius=12)
    svg.text(704, 309, "Replaceable backend", size=17, weight=600)
    svg.text(704, 336, "Gazebo Harmonic today · Raspberry Pi servo interface later", size=14, fill=MUTED)
    svg.line(1059, 215, 1059, 271, stroke=INK, width=2, marker="arrow")
    svg.line(694, 316, 278, 316, stroke=BLUE, width=2, marker="arrow-blue")
    svg.text(486, 302, "joint state / observations", size=14, fill=BLUE, anchor="middle")
    return svg.finish()


def robot_topology() -> str:
    svg = Svg(1200, 720, "Araco joint topology and tripod groups", "Top view of the six four-joint legs, one gimbal joint, and alternating tripod groups.")
    title(svg, "Six four-joint legs plus a yaw gimbal", "Tripod A and Tripod B alternate support; every leg uses the same 43–120–120–50 mm chain.")
    cx, cy = 600, 360
    svg.rect(cx - 115, cy - 80, 230, 160, fill=PALE, stroke=INK, radius=55, stroke_width=2)
    svg.text(cx, cy - 8, "base_link", size=21, weight=600, anchor="middle")
    svg.text(cx, cy + 22, "1 gimbal yaw joint", size=14, fill=MUTED, anchor="middle")
    svg.circle(cx, cy - 118, 22, fill=WHITE, stroke=PURPLE, stroke_width=3)
    svg.line(cx, cy - 80, cx, cy - 96, stroke=PURPLE, width=4)
    legs = [
        ("LF", -0.62, BLUE, "A"), ("LM", -math.pi / 2, ORANGE, "B"),
        ("LR", -2.52, BLUE, "A"), ("RF", 0.62, ORANGE, "B"),
        ("RM", math.pi / 2, BLUE, "A"), ("RR", 2.52, ORANGE, "B"),
    ]
    # SVG y grows downward; the chosen angles produce a conventional top view.
    for label, angle, color, group in legs:
        ux, uy = math.cos(angle), math.sin(angle)
        start = (cx + ux * 112, cy + uy * 72)
        lengths = (34, 60, 60, 30)
        points = [start]
        current = start
        for length in lengths:
            current = (current[0] + ux * length, current[1] + uy * length)
            points.append(current)
        svg.polyline(points, stroke=color, width=8)
        for joint_index, point in enumerate(points[:-1], start=1):
            svg.circle(*point, 8, fill=WHITE, stroke=color, stroke_width=3)
            if joint_index == 1:
                svg.text(point[0] + (-18 if ux < 0 else 18), point[1] - 13, f"{label} · {group}", size=15, weight=600, fill=color, anchor="end" if ux < 0 else "start")
        svg.circle(*points[-1], 6, fill=color, stroke=color)
    # Segment key.
    key_y = 650
    labels = [("coxa", "43 mm"), ("femur", "120 mm"), ("tibia", "120 mm"), ("foot", "50 mm")]
    for index, (name, length) in enumerate(labels):
        x = 152 + index * 225
        svg.circle(x, key_y, 7, fill=WHITE, stroke=INK)
        svg.line(x + 8, key_y, x + 75, key_y, stroke=INK, width=5)
        svg.text(x, key_y + 35, f"q{index + 1}  {name}", size=15, weight=600)
        svg.text(x, key_y + 57, length, size=13, fill=MUTED)
    svg.rect(935, 610, 210, 90, fill=WHITE, stroke=GRID, radius=10)
    svg.line(958, 637, 1002, 637, stroke=BLUE, width=7)
    svg.text(1015, 642, "Tripod A", size=14)
    svg.line(958, 671, 1002, 671, stroke=ORANGE, width=7)
    svg.text(1015, 676, "Tripod B", size=14)
    return svg.finish()


def leg_kinematics() -> str:
    svg = Svg(1200, 760, "Four degree of freedom leg kinematics", "Top and sagittal views of the analytic four-joint leg geometry and wrist-point reduction.")
    title(svg, "Reducing four joints to a solvable two-link triangle", "q₁ chooses the leg plane; q₂ and q₃ reach the wrist; q₄ closes the requested foot pitch ψ.")
    # Top-view inset.
    svg.rect(44, 112, 330, 252, fill=PALE, stroke=GRID, radius=14)
    svg.text(68, 145, "1 · Choose the sagittal plane", size=18, weight=600)
    ox, oy = 125, 275
    svg.line(ox, oy, 325, oy, stroke=GRID, width=2, dash="7 6")
    svg.line(ox, oy, 285, 190, stroke=BLUE, width=6)
    svg.circle(ox, oy, 9, fill=WHITE, stroke=INK)
    svg.circle(285, 190, 7, fill=BLUE, stroke=BLUE)
    svg.add(f'<path d="M {ox + 58} {oy} A 58 58 0 0 0 {ox + 51} {oy - 27}" fill="none" stroke="{ORANGE}" stroke-width="3"/>')
    svg.text(180, 253, "q₁ = atan2(y, x)", size=16, fill=ORANGE)
    svg.text(294, 186, "P(x,y,z)", size=15, weight=600)
    svg.text(68, 338, "r = √(x² + y²)", size=16)
    # Side view.
    svg.rect(404, 112, 752, 560, fill=WHITE, stroke=GRID, radius=14)
    svg.text(430, 145, "2 · Solve inside that plane", size=18, weight=600)
    O = (478, 400)
    A = (570, 400)
    B = (738, 242)
    W = (920, 407)
    P = (920, 540)
    svg.line(450, 540, 1068, 540, stroke=GRID, width=2)
    svg.line(O[0], O[1], A[0], A[1], stroke=PURPLE, width=8)
    svg.line(A[0], A[1], B[0], B[1], stroke=BLUE, width=8)
    svg.line(B[0], B[1], W[0], W[1], stroke=TEAL, width=8)
    svg.line(W[0], W[1], P[0], P[1], stroke=ORANGE, width=8)
    for point, label in ((O, "O"), (A, "A"), (B, "K"), (W, "W"), (P, "P")):
        svg.circle(*point, 10, fill=WHITE, stroke=INK, stroke_width=3)
        svg.text(point[0] + 14, point[1] - 13, label, size=15, weight=600)
    svg.text(512, 386, "L₁ = 43 mm", size=14, fill=PURPLE, anchor="middle")
    svg.text(650, 302, "L₂ = 120 mm", size=14, fill=BLUE, anchor="middle")
    svg.text(832, 310, "L₃ = 120 mm", size=14, fill=TEAL, anchor="middle")
    svg.text(939, 480, "L₄ = 50 mm", size=14, fill=ORANGE)
    svg.line(A[0], A[1], W[0], W[1], stroke=RED, width=2, dash="7 6")
    svg.text(748, 431, "wrist vector (s, zᵥ)", size=14, fill=RED, anchor="middle")
    svg.line(P[0], P[1], 1036, P[1], stroke=GRID, width=2, dash="6 6")
    svg.add(f'<path d="M {P[0]} {P[1] - 55} A 55 55 0 0 1 {P[0] + 55} {P[1]}" fill="none" stroke="{ORANGE}" stroke-width="3"/>')
    svg.text(982, 506, "ψ", size=19, weight=600, fill=ORANGE)
    # Equations and status strip.
    svg.rect(44, 405, 330, 267, fill=WHITE, stroke=GRID, radius=14)
    svg.text(68, 440, "Wrist-point reduction", size=18, weight=600)
    equations = [
        "r = √(x² + y²)",
        "s = r − L₁ − L₄ cos ψ",
        "zᵥ = z − L₄ sin ψ",
        "c₃ = (s² + zᵥ² − L₂² − L₃²) / (2L₂L₃)",
        "q₃ = −acos(c₃)   (knee-down)",
        "q₂ = atan2(zᵥ,s) − atan2(L₃ sin q₃,L₂+L₃ cos q₃)",
        "q₄ = ψ − q₂ − q₃",
    ]
    for index, equation in enumerate(equations):
        svg.text(68, 472 + index * 29, equation, size=14, family="Cambria Math,STIX Two Math,serif")
    svg.text(600, 711, "The solver then checks reachability, singularity, joint limits, and FK reconstruction error.", size=15, fill=MUTED, anchor="middle")
    return svg.finish()


def body_foot_projection() -> str:
    svg = Svg(1200, 610, "Planted-foot body transform and foot projection", "A moved body expressed relative to fixed world feet, with world-down projected into each leg plane.")
    title(svg, "Move the body while the feet remain planted", "The desired world-vertical foot direction is projected into each leg’s realizable sagittal plane.")
    # World and body frames.
    svg.line(88, 517, 356, 517, stroke=INK, width=2, marker="arrow")
    svg.line(88, 517, 88, 212, stroke=INK, width=2, marker="arrow")
    svg.text(362, 523, "world x", size=14)
    svg.text(70, 197, "world z", size=14, anchor="middle")
    svg.add(f'<g transform="translate(310 315) rotate(-12)"><rect x="-122" y="-48" width="244" height="96" rx="28" fill="{PALE}" stroke="{BLUE}" stroke-width="3"/><line x1="0" y1="0" x2="120" y2="0" stroke="{BLUE}" stroke-width="3" marker-end="url(#arrow-blue)"/><text x="0" y="-67" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="17" font-weight="600" fill="{INK}">moved base_link</text></g>')
    svg.circle(560, 517, 10, fill=ORANGE, stroke=ORANGE)
    svg.text(560, 550, "fixed foot Pᵂ", size=15, weight=600, anchor="middle")
    svg.line(372, 337, 560, 517, stroke=TEAL, width=6)
    svg.text(474, 413, "target expressed in moved body", size=14, fill=TEAL, anchor="middle")
    # Equation box.
    svg.rect(655, 117, 501, 438, fill=WHITE, stroke=GRID, radius=14)
    svg.text(682, 155, "Coordinate transform", size=19, weight=600)
    svg.text(682, 194, "Pᴮ = Rᵀ (Pᵂ − t)", size=24, family="Cambria Math,STIX Two Math,serif")
    svg.text(682, 225, "R = Rz(yaw) Ry(pitch) Rx(roll)", size=16, fill=MUTED, family="Cambria Math,STIX Two Math,serif")
    # Projection sketch.
    svg.line(750, 480, 750, 290, stroke=ORANGE, width=3, marker="arrow-orange")
    svg.text(768, 308, "world-down in body", size=14, fill=ORANGE)
    svg.add(f'<path d="M 725 490 L 994 390 L 1035 504 Z" fill="{PALE}" stroke="{GRID}" stroke-width="2"/>')
    svg.text(965, 376, "leg sagittal plane", size=14, fill=MUTED, anchor="middle")
    svg.line(750, 480, 961, 402, stroke=BLUE, width=4, marker="arrow-blue")
    svg.text(883, 430, "realizable projection", size=14, fill=BLUE, anchor="middle")
    svg.line(750, 480, 820, 454, stroke=RED, width=3, dash="5 5")
    svg.text(842, 491, "residual δ", size=14, fill=RED)
    svg.text(682, 265, "A four-DOF leg controls pitch in one plane.", size=15)
    svg.text(682, 540, "δ reports the lateral component the chain cannot realize.", size=14, fill=MUTED)
    return svg.finish()


def legacy_horizontal_scale(phase: float) -> float:
    counter = phase * 100.0
    if counter < 25.0:
        value = -2.0 * counter
    elif counter < 50.0:
        value = (2.0 / 25.0) * (counter - 25.0) ** 2 - 50.0
    elif counter < 60.0:
        value = (-3.0 / 50.0) * (counter - 50.0) ** 3 + (7.0 / 10.0) * (counter - 50.0) ** 2 + 4.0 * (counter - 50.0)
    elif counter < 75.0:
        value = 50.0
    else:
        value = 2.0 * (100.0 - counter)
    return value / 100.0


def legacy_lift_scale(phase: float) -> float:
    counter = phase * 100.0
    value = 0.0
    if 25.0 <= counter < 50.0:
        value = 0.00208 * counter ** 3 - 0.308 * counter ** 2 + 15.2 * counter - 220.0
    elif 50.0 <= counter < 60.0:
        value = 30.0
    elif 60.0 <= counter < 75.0:
        value = (4.0 / 225.0) * (counter - 60.0) ** 3 - (2.0 / 5.0) * (counter - 60.0) ** 2 + 30.0
    return max(0.0, min(1.0, value / 30.0))


def legacy_rotation_scale(phase: float) -> float:
    counter = phase * 100.0
    if counter < 25.0:
        value = -2.0 * counter
    elif counter < 75.0:
        value = (-1.0 / 625.0) * counter ** 3 + (150.0 / 625.0) * counter ** 2 - 9.0 * counter + 50.0
    else:
        value = -2.0 * counter + 200.0
    return value / 100.0


def gait_curves() -> str:
    svg = Svg(1200, 650, "Normalized Araco gait curves", "Exact repeating horizontal, lift, and rotation curves sampled from the current tripod implementation.")
    title(svg, "One continuous phase drives translation, lift, and yaw", "These normalized curves are regenerated from tripod_gait.cpp; physical amplitude comes from stride and clearance.")
    left, right, top_y, bottom = 90, 1145, 132, 530
    width, height = right - left, bottom - top_y
    svg.rect(left, top_y, width, height, fill=WHITE, stroke=GRID, radius=0)
    # Swing half background.
    swing_x = left + width * 0.5
    svg.add(f'<rect x="{swing_x}" y="{top_y}" width="{width * 0.5}" height="{height}" fill="{PALE}"/>')
    for i in range(5):
        x = left + width * i / 4
        svg.line(x, top_y, x, bottom, stroke=GRID, width=1)
        svg.text(x, bottom + 28, f"{i / 4:.2g}", size=13, fill=MUTED, anchor="middle")
    for value in (-0.5, 0.0, 0.5, 1.0):
        y = bottom - (value + 0.55) / 1.6 * height
        svg.line(left, y, right, y, stroke=GRID, width=1)
        svg.text(left - 16, y + 5, f"{value:g}", size=13, fill=MUTED, anchor="end")
    svg.text((left + right) / 2, bottom + 58, "normalized gait phase", size=15, anchor="middle")
    svg.text(left, top_y - 17, "support / stance", size=14, fill=MUTED)
    svg.text(swing_x + 14, top_y - 17, "swing", size=14, fill=MUTED)
    samples = [i / 400 for i in range(401)]
    series = []
    for name, fn, color in (
        ("horizontal", legacy_horizontal_scale, BLUE),
        ("lift", legacy_lift_scale, ORANGE),
        ("rotation", legacy_rotation_scale, PURPLE),
    ):
        points = []
        for local_phase in samples:
            curve_phase = (local_phase + 0.75) % 1.0
            value = fn(curve_phase)
            x = left + local_phase * width
            y = bottom - (value + 0.55) / 1.6 * height
            points.append((x, y))
        svg.polyline(points, stroke=color, width=4)
        series.append((name, color))
    for index, (name, color) in enumerate(series):
        x = 310 + index * 230
        svg.line(x, 606, x + 44, 606, stroke=color, width=5)
        svg.text(x + 56, 612, name, size=15)
    svg.text(90, 612, "normalized scale", size=15, fill=MUTED)
    return svg.finish()


def motion_blending() -> str:
    svg = Svg(1200, 590, "Translation and yaw blending", "Top-view construction of translation and rotation foot displacement with relative command weighting.")
    title(svg, "Translation and body yaw are blended as foot-space motion", "The stronger command sets overall magnitude; relative input magnitudes decide the translation/rotation weights.")
    cx, cy = 350, 335
    svg.circle(cx, cy, 114, fill=PALE, stroke=INK, stroke_width=2)
    svg.circle(cx, cy, 6, fill=INK, stroke=INK)
    svg.text(cx, cy + 7, "C", size=14, fill=WHITE, anchor="middle")
    foot = (505, 230)
    svg.line(cx, cy, *foot, stroke=GRID, width=3, dash="7 6")
    svg.circle(*foot, 9, fill=WHITE, stroke=INK, stroke_width=3)
    svg.text(520, 220, "nominal foot p", size=15, weight=600)
    # Translation, rotational tangent, final vector.
    svg.line(foot[0], foot[1], foot[0] + 134, foot[1] - 56, stroke=BLUE, width=5, marker="arrow-blue")
    svg.text(650, 161, "T · translation", size=15, fill=BLUE)
    svg.line(foot[0], foot[1], foot[0] + 82, foot[1] + 122, stroke=ORANGE, width=5, marker="arrow-orange")
    svg.text(594, 378, "R · yaw arc", size=15, fill=ORANGE)
    svg.line(foot[0], foot[1], foot[0] + 122, foot[1] + 28, stroke=INK, width=5, marker="arrow")
    svg.text(646, 281, "Δp", size=17, weight=600)
    svg.add(f'<path d="M 423 251 A 92 92 0 0 1 448 399" fill="none" stroke="{ORANGE}" stroke-width="3" marker-end="url(#arrow-orange)"/>')
    svg.text(423, 426, "rotation about base origin", size=14, fill=ORANGE, anchor="middle")
    # Formula panel.
    svg.rect(735, 125, 421, 385, fill=WHITE, stroke=GRID, radius=14)
    svg.text(766, 165, "Relative-magnitude mixing", size=20, weight=600)
    equations = [
        "uₜ = ‖vxy‖ / vscale",
        "uᵣ = |ω| / ωscale",
        "α = uₜ / (uₜ + uᵣ)",
        "β = uᵣ / (uₜ + uᵣ)",
        "m = max(uₜ, uᵣ)",
        "Δp = α T(m) + β R(m)",
    ]
    for index, equation in enumerate(equations):
        svg.text(775, 211 + index * 45, equation, size=20, family="Cambria Math,STIX Two Math,serif")
    svg.text(766, 490, "Pure translation and pure rotation remain unchanged.", size=14, fill=MUTED)
    return svg.finish()


def digital_twin() -> str:
    svg = Svg(1200, 470, "Araco digital model pipeline", "The flow from Fusion geometry and measured component research into the canonical ROS model and Gazebo simulation.")
    title(svg, "One canonical model, several representations", "Presentation meshes, collision shapes, kinematics, and provisional dynamics are kept separate on purpose.")
    specs = [
        (44, "Fusion 360", "assembly + joints", BLUE),
        (270, "Export evidence", "meshes + properties", TEAL),
        (496, "Canonical model", "26 links · 25 joints", PURPLE),
        (722, "Xacro / URDF", "ROS frames + control", ORANGE),
        (948, "Gazebo", "physics + sensors", RED),
    ]
    for x, heading, body, color in specs:
        node(svg, x, 130, 190, 88, heading, body, color)
    for x in (234, 460, 686, 912):
        svg.line(x + 8, 174, x + 35, 174, stroke=INK, width=2, marker="arrow")
    channels = [
        ("visual", "49 exact mesh visuals", BLUE),
        ("collision", "simple stable primitives", TEAL),
        ("kinematics", "43 / 120 / 120 / 50 mm", PURPLE),
        ("dynamics", "rough_estimate_v0", ORANGE),
    ]
    for index, (label, body, color) in enumerate(channels):
        x = 80 + index * 276
        svg.rect(x, 295, 238, 86, fill=PALE, stroke=color, radius=12, stroke_width=1.8)
        svg.text(x + 18, 327, label, size=16, weight=600, fill=color)
        svg.text(x + 18, 356, body, size=14, fill=MUTED)
        svg.line(x + 119, 290, 591, 222, stroke=GRID, width=1.5)
    svg.text(600, 430, "Separation prevents a pretty mesh or a bad CAD material assignment from silently becoming physics truth.", size=15, fill=MUTED, anchor="middle")
    return svg.finish()


def perception_pipeline() -> str:
    svg = Svg(1200, 480, "Araco RGB-D mapping pipeline", "The simulated Gemini-style color and depth streams flow through registration, visual odometry, and RTAB-Map outputs.")
    title(svg, "From stereo depth to a map of the environment", "The yaw gimbal carries the Gemini 335 model; simulated RGB-D streams feed a six-DoF visual mapping pipeline.")
    specs = [
        (44, "Gazebo scene", "landmarks + lighting", BLUE),
        (270, "Gemini-like sensor", "RGB · depth · IMU", TEAL),
        (496, "RGB-D registration", "aligned color + depth", PURPLE),
        (722, "Visual odometry", "frame-to-map 6-DoF", ORANGE),
        (948, "RTAB-Map", "loop closure + graph", RED),
    ]
    for x, heading, body, color in specs:
        node(svg, x, 128, 190, 88, heading, body, color)
    for x in (234, 460, 686, 912):
        svg.line(x + 8, 172, x + 35, 172, stroke=INK, width=2, marker="arrow")
    # Outputs.
    output_specs = [
        (176, "registered images", "424 × 240 · 15 Hz", BLUE),
        (470, "2D occupancy grid", "5 cm cells", TEAL),
        (764, "accumulated 3D cloud", "colored geometry", PURPLE),
    ]
    for x, heading, body, color in output_specs:
        svg.rect(x, 315, 250, 86, fill=PALE, stroke=color, radius=12, stroke_width=1.8)
        svg.text(x + 20, 347, heading, size=16, weight=600, fill=color)
        svg.text(x + 20, 376, body, size=14, fill=MUTED)
    svg.line(1043, 219, 1043, 275, stroke=INK, width=2)
    svg.line(301, 275, 1043, 275, stroke=INK, width=2)
    for x in (301, 595, 889):
        svg.line(x, 275, x, 309, stroke=INK, width=2, marker="arrow")
    svg.text(600, 450, "Simulator ground truth is used for observation and scoring, never as an input to the estimator.", size=15, fill=MUTED, anchor="middle")
    return svg.finish()


FIGURES = {
    "system-overview.svg": system_overview,
    "robot-topology.svg": robot_topology,
    "leg-kinematics.svg": leg_kinematics,
    "body-foot-projection.svg": body_foot_projection,
    "gait-curves.svg": gait_curves,
    "motion-blending.svg": motion_blending,
    "digital-twin.svg": digital_twin,
    "perception-pipeline.svg": perception_pipeline,
}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for filename, factory in FIGURES.items():
        (OUTPUT / filename).write_text(factory(), encoding="utf-8")


if __name__ == "__main__":
    main()
