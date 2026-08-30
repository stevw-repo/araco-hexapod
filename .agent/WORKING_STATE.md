# Araco Hexapod — Working State

Updated: 2026-08-30
Machine: `stevw-s14-Stealth-14Studio-A13VF` (Ubuntu 24.04.4 LTS)
Branch: `perception-v2`, branched from `main` at `8dd9429`

## Current goal

**Rebuild perception and navigation from scratch** to give the robot autonomous
mapping, relocalization, and waypoint navigation. The approved architecture is in
`docs/superpowers/specs/2026-08-30-perception-navigation-architecture-design.md`.
Read that first; this file tracks execution state only.

The one-line summary: leg odometry plus a body IMU become the odometry backbone,
a body-fixed 360° lidar becomes the SLAM geometry, rtabmap stops producing
odometry and starts consuming it, and Nav2 enters through the existing command
arbiter as an arbitrated, safety-gated source.

## Why the old stack was removed

rtabmap owned both odometry and mapping, so RGB-D visual odometry was the single
point of failure for the whole chain. It has a documented, reproducible failure:
facing a blank wall in the validation arena kills odometry within a second. The
workaround was a driving procedure — always face the direction of travel — which
cannot survive an autonomous planner that rotates the robot wherever it likes.

## What was removed on this branch

- `src/araco_perception/` and `src/araco_navigation/` — both packages, entirely
- `.agent/evidence/` — all 17 evidence summaries including the route 09 metrics
- The four perception profiles under `src/araco_bringup/config/profiles/`
- The previous `WORKING_STATE.md` content (1,761 lines of superseded history)

All of it remains in git history on branch `codex/rgbd-imu-aiding`, whose tip
commit `b6eb511` was made specifically to preserve it before the rebuild.

## Blocking first task: the tree does not build

Removing the two packages left dangling references in 12 files. Sub-project 0
must resolve every one of them before anything else compiles:

```
src/araco_bringup/config/profiles/gazebo_ci_v0.yaml
src/araco_bringup/config/profiles/gazebo_dev_v0.yaml
src/araco_bringup/config/profiles/gazebo_gate3_v0.yaml
src/araco_bringup/config/profiles/gazebo_gate4_v0.yaml
src/araco_bringup/config/profiles/gazebo_gate5_v0.yaml
src/araco_bringup/config/profiles/gazebo_joystick_v0.yaml
src/araco_bringup/launch/gazebo.launch.py
src/araco_bringup/package.xml                      (exec_depend lines 20-21)
src/araco_system_tests/scripts/araco_gate6_evidence
src/araco_system_tests/test/test_gate0_bundle.py
src/araco_system_tests/test/test_project_dependency_graph.py
src/araco_system_tests/test/test_slam_scoring.py
```

`gazebo_joystick_v0` references the old camera artifact
`config/sensors/gemini_335_sim_v0.yaml` directly. The gate profiles and
`test_slam_scoring.py` carry frozen fingerprints of the old stack that will not
survive the rebuild and should be re-derived rather than patched.

This breakage is expected and was accepted deliberately: rewiring bringup
requires knowing what replaces the perception artifacts, which is sub-project 0's
design work, not a mechanical fix.

## Sub-project sequence

Each gets its own spec, preregistered gates, and implementation plan. Gates are
fixed before measurement: a threshold that fails for a contingent reason is a
result, not an invitation to redefine it.

| # | Sub-project | State |
|---|---|---|
| 0 | Sensor suite — body IMU, lidar mast, RGB-D, reserved mounts | **next** |
| 1 | Leg odometry + EKF | not started |
| 2 | rtabmap on external odometry | not started |
| 3 | Relocalization from saved map | not started |
| 4 | Nav2 + arbiter bridge | not started |
| 5 | Waypoint navigation | not started |

Sub-project 1 is the one to get right; everything above inherits its errors.

## What survived and is still binding

- **Locomotion**, including the tripod gait. `duty_factor: 0.5`, explicit
  `phase_groups`, `gait_phase` and `gait_cycle` published on `LocomotionStatus`.
  Exactly three feet are planted at all times, which is what makes leg odometry
  tractable. `tripod_gait.cpp` already computes a per-leg swing flag internally;
  publishing `bool[6] leg_in_stance` is a small worthwhile addition.
- **Safety supervisor and command arbiter.** Nav2 becomes an arbitrated command
  source, not a direct `cmd_vel` binding.
- **`MotionIntent.msg`** already carries `geometry_msgs/Twist planar_velocity`,
  which is exactly what Nav2 emits, including the lateral term a holonomic
  hexapod can use.
- **Artifact discipline** — schema-validated config artifacts, profile
  composition, evidence-backed gates. Keep these; they are the strongest patterns
  in the repository.
- **`DECISIONS.md`** is retained in full. Its perception entries are now
  historical, but the safety, locomotion, and architecture rulings still bind.

## Inherited constraints

- **Gait limits bound navigation speed.** `maximum_stride_m: 0.12` and
  `maximum_cadence_hz: 2.5`. Nav2 velocity limits must be derived from these, not
  chosen. Commanding faster than the gait can walk makes Nav2 believe it is being
  ignored, and it will oscillate.
- **Simulator-only.** No physical servo actuation is authorized or described.
- **Orderly shutdown does not reap the backend.** `SafetyTransition` request 4
  returned `SUCCEEDED` on every observed shutdown while `gz sim` survived and
  needed an explicit `SIGTERM`. Anything scripting shutdown must reap rather than
  trust the action result.
- **The headed perception profile ran at roughly 0.5 real-time** on this machine,
  so wall duration was about twice sim duration. Expect similar for any new
  headed profile.

## Deliberately shelved

**Visual-inertial odometry.** A full VIO effort was scoped and its Phase 0
feasibility probe passed all five preregistered gates on 2026-08-30, on unchanged
thresholds. The estimator was never built and is not part of this architecture:
monocular VIO exists to recover odometry from a camera and an IMU when nothing
else is available, and this robot has legs. Leg odometry plus a body IMU covers
the same failure mode without a GPL source build or monocular scale recovery.

VIO remains available as future hardening if leg odometry disappoints. Nothing in
the design forecloses it. The prior measurements are in git history on
`codex/rgbd-imu-aiding`.

**Perceptive locomotion** — terrain elevation mapping, foothold selection, body
pose adaptation, dynamic balance, stairs. This is the larger half of Spot-like
capability and is a locomotion problem, not a navigation one. The sensor layout
reserves mounts so the track can begin without re-plumbing hardware.
