# Perception and Navigation Architecture — Design

Date: 2026-08-30
Status: approved for implementation
Scope: complete replacement of the perception and navigation stack

## Goal

Give the Araco hexapod autonomous mapping, relocalization, and waypoint
navigation: point at a spot on a map, and the robot walks there.

## Non-goals

Explicitly out of scope for this effort, and deferred rather than rejected:

- **Perceptive locomotion.** Terrain elevation mapping, foothold selection, body
  pose adaptation, dynamic balance, stair traversal. This is the larger half of
  what makes a Boston Dynamics Spot impressive, and it is a locomotion problem
  rather than a navigation one. The sensor layout below reserves mounts so this
  track can begin without re-plumbing hardware, but nothing in it is built now.
- **Visual-inertial odometry.** Shelved deliberately. See "Why VIO was dropped".
- **Physical hardware.** Simulator-only, as with all prior work.

## Why the previous stack was replaced

The prior perception stack made rtabmap responsible for odometry as well as
mapping. RGB-D visual odometry was therefore the single point of failure for the
entire navigation chain, and it has a documented, reproducible failure: facing a
blank wall in the validation arena kills odometry within a second. The
workaround was a *driving procedure* — always face the direction of travel.

That workaround cannot survive autonomy. A local planner rotates the robot to
whatever heading it wants, including at walls. The architecture below removes the
failure mode rather than working around it, by giving the robot an odometry
source that does not depend on vision at all.

## Key insight: a hexapod is not a drone

The robot has proprioception. Joint states publish at 125 Hz across 24 joints,
and the tripod gait knows which legs are in stance at every instant. This is how
legged robots actually estimate state: proprioception is the backbone, vision is
the correction.

Leg kinematics plus IMU produce odometry that always exists and drifts slowly.
SLAM removes the drift when vision is available. When vision fails, the legs and
the IMU carry the robot. No vision-shaped hole in the estimator.

## Sensor suite

| Sensor | Mounting | Purpose |
|---|---|---|
| 360° 2D lidar | Rigid mast from `base_link`, on the gimbal yaw axis, above the camera | Navigation: SLAM geometry, costmaps, obstacle avoidance |
| RGB-D (Gemini 335) | On `gimbal_yaw_link`, free to rotate | 3D perception, visual loop closure |
| IMU | Rigidly at `base_link` | State estimation |
| Camera IMU | On `camera_link` | Retained; not the estimator's primary |
| *(reserved)* | Downward / surround depth mounts | Terrain track, not populated now |

### Lidar placement rationale

Measured geometry: `gimbal_yaw_joint` is parented to `base_link` at
`[-0.005, 0, 0.08435]` with axis `[0,0,1]` — **yaw only**, ±1.571 rad, 1.5 rad/s.
`camera_mount_joint` sits at `[0.04, 0, 0.04]` from the gimbal, putting
`camera_link` roughly 124 mm above `base_link`. Legs are coxa 0.043 m, femur
0.12 m, tibia 0.12 m.

Two candidate placements were rejected:

- **On the gimbal.** Yaw-only rotation would keep the scan plane horizontal, so
  this avoids the tilt failure a pitching mount would cause. It is rejected for
  different reasons: a 360° lidar gains nothing from being aimed, and mounting it
  on a moving joint injects that joint into the TF chain of the primary SLAM
  sensor. Every scan would need the gimbal angle at scan time, joint-state
  latency would become scan error, a 1.5 rad/s slew would smear a sweep, and map
  quality would become coupled to an unrelated operator control.
- **Underneath the body.** The leg workspace is exactly that volume, and the
  tripod gait keeps three legs swinging through it continuously. The result is
  phantom returns that are periodic and correlated with gait phase — the hardest
  kind to filter, because they look like real obstacles.

The chosen mount is a short rigid mast rising from `base_link`, bypassing the
gimbal, carrying the lidar above the camera at roughly `z = 0.19 m`. Three
properties matter:

- **Rigid to `base_link`** — static TF, no joint state required, no latency
  coupling; every scan has an exactly known pose.
- **Centered on the yaw axis** — an in-place turn rotates the lidar without
  translating it. Any offset adds scan distortion proportional to the offset.
- **Above the camera** — the scan plane clears the gimbal and camera assembly, so
  no sector is occluded.

### What this unlocks

The current `gimbal_policy` is `fixed_for_initial_validation`: the camera is kept
centered because moving it breaks visual odometry. Once the lidar is the
geometric SLAM backbone and leg odometry supplies odometry, **the camera becomes
free**. Nothing in the navigation stack depends on where it points.

### Deliberate blind spot

With the body standing roughly 0.10–0.13 m off the floor, the scan plane sits
about 0.30 m above ground. It sees walls, chair legs, and table legs, and misses
anything shorter. This is handled by the local costmap's voxel layer consuming
the depth cloud, not by lowering the lidar — lowering it would put it back into
the leg workspace.

### Measurement required before the mount is final

Gait-induced body roll and pitch tilt the scan plane even with a rigid mount. Log
body attitude over a walking route and examine the distribution. If p99 tilt is
under roughly 2°, the rigid mount stands as designed. Above that, add scan
rejection above a tilt threshold. The `duty_factor: 0.5` tripod is statically
stable with three feet always down, so a small result is expected — but this is
cheap to measure and expensive to assume.

## Architecture

```
  ┌─ INHERITED, UNCHANGED ───────────────────────────────┐
  │  joint_states 125 Hz · tripod gait (phase, groups)    │
  │  MotionIntent/Twist · command arbiter · safety        │
  └───────────────────────────────────────────────────────┘
                            │
  1. STATE ESTIMATION       ▼
     joint_states + LocomotionStatus → leg_odometry ─┐
       3-stance-foot FK, least squares               │
       slip residual → covariance                    ├→ robot_localization EKF
     body IMU ───────────────────────────────────────┘        │
                                                              ▼ odom → base_link
  2. SLAM                                                     │ continuous
     rtabmap ← lidar + RGB-D + external odometry              │
                                                              ▼ map → odom
  3. RELOCALIZATION                                           │ drift correction
     rtabmap localization mode ← saved database               │
                                                              ▼
  4. NAV2                                                     │
     global costmap ← rtabmap occupancy grid                  │
     local costmap  ← lidar + depth cloud (voxel)             │
     planner: Smac 2D · controller: MPPI (holonomic)          │
                                                              ▼ Twist
  5. WAYPOINTS → nav2_arbiter_bridge → MotionIntent → arbiter → gait
```

### State estimation

`leg_odometry` subscribes to `joint_states` and `LocomotionStatus`. Stance legs
are derived from `gait_phase`, `duty_factor: 0.5`, and the declared
`phase_groups`; `tripod_gait.cpp` already computes a per-leg swing flag
internally, and publishing an explicit `bool[6] leg_in_stance` on
`LocomotionStatus` is a small, worthwhile addition.

With `duty_factor: 0.5` exactly three feet are planted at all times. Three
contact points over-determine the body twist, so forward kinematics on the stance
feet yields a least-squares solution **and** a residual. That residual is a live
slip-quality signal: when feet slip the legs disagree, the residual rises, and the
EKF covariance rises with it, shifting weight onto the IMU. Graceful degradation
falls out of the geometry at no extra cost.

Known limitation: this is kinematic odometry that assumes the gait schedule is
truth. With no force sensing, an early or missed touchdown cannot be detected
directly — only inferred from inconsistency.

`robot_localization`'s EKF fuses the leg-odometry twist with the body IMU and
publishes `odom -> base_link`. Lidar or visual odometry may be added as a third
input later; the design does not require it.

### SLAM

rtabmap is the single SLAM system, consuming lidar, RGB-D, and external odometry.
It publishes both the 2D occupancy grid Nav2 consumes and the 3D cloud, from one
database with one localization mode.

`slam_toolbox` was considered — it is the Nav2-canonical choice and simpler — but
it is lidar-only, which would require a second system for the RGB-D and reproduce
the two-SLAM-stacks problem this design exists to avoid.

**The critical change from the previous stack: rtabmap no longer produces
odometry, it consumes it.** That single rewiring is what removes the blank-wall
failure. Vision becomes a correction rather than a dependency.

### Navigation

Costmaps: global from the rtabmap occupancy grid with inflation; local from lidar
and the depth cloud via obstacle and voxel layers, with inflation.

Planner Smac 2D. Controller MPPI, chosen because the hexapod is holonomic — it
strafes, and `MotionIntent.planar_velocity` already carries lateral velocity that
a differential-drive controller would discard.

Nav2 enters through a `nav2_arbiter_bridge` node that converts `Twist` to
`MotionIntent` and registers as a command source. It is arbitrated against the
joystick and safety-gated, so autonomy is preemptible by touching the stick. This
is a stronger autonomy safety story than binding Nav2 directly to `cmd_vel`, and
it reuses arbitration that already exists.

**Velocity limits must be derived from gait limits, not chosen.**
`maximum_stride_m: 0.12` and `maximum_cadence_hz: 2.5` bound real top speed.
Commanding faster than the gait can walk will make Nav2 believe it is being
ignored, and it will oscillate.

## Sub-projects

Each gets its own spec, preregistered gates, and implementation plan. Gates are
fixed before measurement, per the project's established discipline: a threshold
that fails for a contingent reason is a result, not an invitation to redefine it.

| # | Sub-project | Gate shape |
|---|---|---|
| 0 | Sensor suite — body IMU, lidar mast, RGB-D, reserved mounts | Streams present, TF tree correct, contract tests pass, body-tilt measurement taken |
| 1 | Leg odometry + EKF | Drift over a route against ground truth below a preregistered bound; survives a scripted vision blackout |
| 2 | rtabmap on external odometry | Map quality at or above the prior route baseline; **survives a blank-wall heading** |
| 3 | Relocalization from saved map | Recovers pose after restart, within bound, from N start positions |
| 4 | Nav2 + arbiter bridge | Reaches goals; arbiter preempts correctly; never exceeds gait limits |
| 5 | Waypoint navigation | Multi-waypoint route completes autonomously |

Sub-project 1 is the one to get right; everything above inherits its errors.
Gate 2 promotes the current blank-wall workaround into an explicit acceptance
test.

## Why VIO was dropped

A full visual-inertial odometry effort was scoped and its Phase 0 feasibility
probe passed all five preregistered gates on 2026-08-30. It is nonetheless not
part of this architecture.

The reason is that VIO solves a problem this robot does not have. Monocular VIO
exists to recover odometry from a camera and an IMU when nothing else is
available — the drone case. A hexapod has legs, and leg odometry plus a body IMU
covers the same failure mode without a GPL source build, without monocular scale
recovery, and without a new estimator to validate.

VIO remains available as future hardening if leg odometry disappoints. Nothing in
this design forecloses it.

## Inherited constraints

- **Gait limits bound navigation speed.** See Navigation above.
- **Safety and arbitration are not bypassed.** Nav2 is a command source, subject
  to the same arbitration and safety gating as the joystick.
- **Simulator-only.** No physical servo actuation is authorized or described.
- **Artifact discipline retained.** Schema-validated config artifacts, profile
  composition, and evidence-backed gates are kept; they are the strongest
  patterns in the repository and the new stack should follow them.

## Open decisions

- Exact lidar model, range, scan rate, and angular resolution.
- Reserved terrain mount positions and count — deferred until the terrain track
  is scoped, but the mast design must not preclude them.
- Whether AprilTag fiducials are added for guaranteed relocalization recovery.
  Spot uses them; they are cheap and robust. Not required for the gates above.
