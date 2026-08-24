# Araco Hexapod — Working State

Updated: 2026-08-24
Machine: `stevw-s14-Stealth-14Studio-A13VF` (Ubuntu 24.04.4 LTS)
Location: these continuity files moved from `docs/agent/` to `.agent/` on
2026-08-18, committed as `6b23132`.

## Current goal and result

### Route 09 acceptance — attempted twice, not yet accepted (2026-08-24)

Two operator attempts were run after the earlier handoff. Neither produced an
acceptance pass; both ended at the scorer's 300 s wall timeout. The simulator
and scorer are no longer running, and no `/dev/input/js*` device is currently
present.

- Attempt 1: `log/route09_attempt1/metrics.json`. Status `FAIL`; one ordered
  waypoint was completed, ground-truth path length was `1.836 m`, and tracking
  was lost for `30.294 s` through the finish. The robot stopped `0.931 m` from
  its starting position with `2.023 rad` yaw error.
- Attempt 2: `log/route09_attempt2/metrics.json`. Status `FAIL`; tracking stayed
  healthy, the ground-truth path length reached `6.592 m`, working memory grew,
  and loop closure `309` was observed. However, none of the four ordered route
  waypoints registered, the robot finished `0.635 m` from the start, and the
  scorer never entered the final dwell/convergence stage. Corrected closure
  errors at timeout were within their standalone bounds (`0.106 m`,
  `0.0286 rad`), but this does not compensate for the incomplete ordered route.

The prior route-09 database and score paths are no longer fresh:
`/tmp/araco_rgbd_acceptance_09.db` exists, and
`/tmp/araco_slam_acceptance_score_09/` exists but is empty. Preserve the two
local metrics files above. For the next trial use new attempt-specific
paths, connect the LiteStar PXN-2113 Pro first, and watch the scorer for each
`Route waypoint N/5 reached` message before proceeding to the next landmark.

### README research write-up — completed (2026-08-24)

**Result:** the short root `README.md` is replaced by a 4,500-word standalone
research write-up in the user's personal voice. It teaches the physical design,
software decomposition, coordinate frames, four-DOF FK/IK derivation,
planted-foot body transforms and foot-orientation projection, transactional
six-leg solving, responsive tripod scheduling, the exact piecewise gait curves,
translation/yaw blending, CAD-to-Gazebo modelling, mass research, and RGB-D
visual mapping. Intuition is paired with university-level equations.

The requested exclusions are retained: there is no build/reproduction or
troubleshooting guide, gate/test report, detailed supervision/safety chapter,
strict configuration/reproducibility chapter, dedicated negative-findings
section, limitations/roadmap, or standalone references/license chapter.
Necessary qualifications remain adjacent to physical-backend, dynamics, and
perception claims. Early generations receive one introductory sentence rather
than a dedicated comparison.

**Media and figures:** authentic source material was reduced to a local hero
render, a 1.5 MB physical-demo MP4, and a poster frame under
`docs/assets/readme/`. Eight replacement SVGs use one consistent visual language:
system overview, robot topology/tripod groups, leg IK geometry, planted-foot
projection, exact gait curves, motion blending, digital-twin construction, and
the perception pipeline. `tools/readme_assets/generate_readme_assets.py`
deterministically regenerates all eight. The old technical screenshots and the
two-page handwritten IK PDF were used only as research references.

**Validation performed:** the generator ran twice with identical SHA-256 hashes
for all eight SVGs; `python3 -m py_compile` passed; all eight generated files
parsed as XML; a local checker found no missing README asset links or TOC
anchors; and `git diff --check` passed. All eight SVGs were also rendered in
headless Chromium and visually inspected before temporary QA rasters were
removed. No ROS build or test run was needed because the implementation code
was not changed. No commit or push was made.

**License request withdrawn (2026-08-24):** the temporary repository-wide
license-removal pass was reverted at the user's request. The original MIT
license files, SPDX declarations, ROS package metadata, asset-rights records,
generated meshes, and license checks remain in place. The completed README and
its media, diagrams, and deterministic generator were preserved.

Repository maintenance note: the user renamed the GitHub repository on
2026-08-24. The current workspace is
`/home/stevw-s14/Desktop/araco-hexapod`, and its local `origin` is configured as
`https://github.com/stevw-repo/araco-hexapod.git` for fetch and push. The latest
recorded pull completed at 2026-08-24 20:31 +08:00. Before this continuity
update, `main` was clean and it and the locally known `origin/main` both pointed
to `e6b9c6b` (`0` ahead, `0` behind). Later remote movement has not been checked.

Merge readiness was rechecked on 2026-08-24. Before integration, `main` was an
ancestor of `fix/gate0-tests-and-relay-exec-bit`; the feature branch was eight
commits ahead and zero behind. The user approved committing the verification
note, fast-forwarding `main`, and pushing it. The fast-forward completed without
conflicts, and local `main` and `origin/main` were verified at `65dd3b7` after
the push.

The post-merge route-09 step has now been attempted twice without acceptance.
This checkout has `build/`, `install/`, and `log/` directories from 2026-08-24;
the latest recorded full build/test validation remains the `434 tests, 0
errors, 0 failures, 26 skipped` result below. No `/dev/input/js*` gamepad device
was present at the latest inspection.

The immediate SLAM-drift correction is implemented. Repeated operator routes
04–08 were suspended and replaced with short synchronized trials. Those trials
isolated the simulator camera-IMU timestamp path as defective: over 90% of
timestamp-specific `camera_link -> base_link` lookups were unavailable, while
RGB-D-only tracking handled both body motion and gimbal motion without tracking
loss.

`gazebo_perception_v0` now uses six-DoF RGB-D visual odometry without IMU
fusion (`araco.navigation.rtabmap-rgbd-sim` `0.4.0`). The simulated IMU remains
published and recorded; it is excluded only from the operational estimator.
Exact dynamic-IMU, fixed-gimbal-IMU, and visual-only variants remain available
as diagnostic profiles. Ground truth remains observer-only.

The acceptance protocol is also corrected. It requires the first four route
waypoints, then final position and starting yaw held for two simulator seconds,
followed by ten seconds of tracking-healthy stable corrected pose. The arena
has a visible +X heading arrow. The scorer reports strict JSON and cannot finish
on position alone before heading or graph convergence.

**Route 09 passed on 2026-08-24, twelve checks of twelve** — see the route 09
section below and `log/route09_pass/metrics.json`. The correction is validated
end to end: zero tracking loss, loop closure observed, 2.6 cm translation
closure and 0.0035 rad yaw closure. Saved-database relocalization and Nav2 are
no longer blocked.

## Implemented ownership

- `araco_gazebo` owns `rgbd_validation_v0` `0.3.0`, including the visible +X
  heading arrow and the established landmark route.
- `araco_perception` owns registered 424 x 240, 15 Hz simulated RGB-D streams,
  the 100 Hz simulated camera IMU, and RTAB-Map RViz layout.
- `araco_navigation` owns the operational visual-only estimator `0.4.0` and
  three test-only estimator variants:
  - `rtabmap_rgbd_visual_only_sim_v0.yaml`
  - `rtabmap_rgbd_dynamic_gimbal_imu_sim_v0.yaml`
  - `rtabmap_rgbd_fixed_gimbal_imu_sim_v0.yaml`
- `araco_bringup` resolves the exact selected navigation artifact. Operational
  profile `gazebo_perception_v0` selects visual-only estimation. Three
  `gazebo_perception_diagnostic_*` profiles select the exact variants above.
- `araco_system_tests` owns `araco.system-tests.slam-acceptance` `0.4.0`, the
  corrected scorer, and `araco_slam_diagnose`. The diagnostic recorder
  publishes commands on a dedicated 50 Hz wall-time thread, records safety
  state/reason, and rejects stale-command or no-motion trials.

## Controlled diagnostic evidence

All error values compare the estimator's relative motion with simulator truth.
No ground-truth signal entered RTAB-Map.

- Visual-only stationary:
  `/tmp/araco_diag_visual_stationary_20260818_01/summary.json` — corrected
  translation `0.0000505 m`, yaw `0.0000882 rad`, zero tracking loss.
- Fixed-IMU stationary:
  `/tmp/araco_diag_fixed_stationary_20260818_01/summary.json` — corrected
  translation `0.0000418 m`, yaw `0.0000579 rad`, zero tracking loss.
- Visual-only translation:
  `/tmp/araco_diag_visual_translation_20260818_02/summary.json` — `0.58626 m`
  true travel, corrected translation error `0.08229 m`, yaw error
  `0.002286 rad`, zero tracking loss or source staleness.
- Fixed-IMU translation:
  `/tmp/araco_diag_fixed_translation_20260818_03/summary.json` — `0.58452 m`
  true travel, corrected translation error `0.10386 m`, yaw error
  `0.004548 rad`, zero tracking loss or source staleness.
- Visual-only body yaw:
  `/tmp/araco_diag_visual_body_yaw_20260818_01/summary.json` — `3.134 rad`
  maximum true yaw, corrected translation error `0.0640 m`, yaw error
  `0.02211 rad`, zero tracking loss or source staleness.
- Fixed-IMU body yaw:
  `/tmp/araco_diag_fixed_body_yaw_20260818_02/summary.json` — `3.141 rad`
  maximum true yaw, corrected translation error `0.05005 m`, yaw error
  `0.02184 rad`, zero tracking loss or source staleness.
- Visual-only gimbal yaw with stationary body:
  `/tmp/araco_diag_visual_gimbal_yaw_20260818_01/summary.json` — gimbal reached
  `0.28 rad`; estimator invented only `0.0000470 m` translation and
  `0.000399 rad` yaw, with zero tracking loss.
- Timestamped camera-IMU transform checks failed for about 90–94% of samples in
  every controlled trial (for example visual stationary `135/1475` successes,
  fixed stationary `122/1481`). The fixed variant masks this by accepting the
  latest transform; it does not repair timing or prove valid inertial fusion.

The earlier fixed translation trial
`/tmp/araco_diag_fixed_translation_20260818_02` is excluded from comparison
because it reused a graph after a large yaw trial. Early diagnostic runs that
triggered `SOURCE_STALE` are also invalid and are not acceptance evidence.

## Static validation

- All operational and diagnostic profiles composed successfully from installed
  artifacts. Operational behavior fingerprint:
  `32dd967509420327c135167abefa9b2dfc2f5ef0754c5727d2f37db12f7a7aa2`.
  This replaces
  `d7d55a9774692baf62ae4f57c1272f782f0b26e59fc612b97c16c5eeb668b03c`, which was
  reproduced exactly from the unmodified tree immediately before the
  2026-08-18 evidence-source repoint and remains the correct value for commit
  `f1e41af`. Fingerprints are recomputable from source and were not lost with
  the deleted `/tmp` evidence.
- `gz sdf -k src/araco_gazebo/worlds/rgbd_validation_v0.sdf`: valid.
- Focused navigation, profile-composition, and scorer tests pass.
- 2026-08-24 fresh verification at `308c5f6`: `colcon build --symlink-install`
  completed all 11 packages, and `colcon test` plus
  `colcon test-result --verbose` reported `434 tests, 0 errors, 0 failures,
  26 skipped`. The worktree was clean immediately after verification.
- The earlier `386 tests, 0 errors, 0 failures, 23 skipped` result covered only
  `araco_navigation`, `araco_gazebo`, `araco_bringup`, and `araco_system_tests`.
  It never exercised `araco_description` or `araco_perception`.
- 2026-08-18 full-workspace run at commit `3bd9dc9`: `colcon build` succeeded;
  `colcon test` reported `424 tests, 0 errors, 4 failures, 26 skipped`. The
  four reported failures are two distinct tests, each counted twice across
  `Test.xml` and the xunit report. Both are described below.
- All Gazebo, RViz, bridge, RTAB-Map, and control sessions were closed after
  live diagnostics.

## Two open test failures — both fixed 2026-08-18

Both are resolved. `colcon build` succeeded and `colcon test` reports
`424 tests, 0 errors, 0 failures, 26 skipped`. Gate 6's independent
installed-space package-test phase reproduced the same totals.

1. `araco_description` —
   `test_gate0_description.py::test_resources_are_redistributable_hashed_and_reproducible`.
   Fixed by regenerating `meshes/presentation_exact/normalization_manifest.json`
   with `normalize_fusion_exact_visuals.py` using the arguments the test uses.
   The regenerated tree was diffed against the committed one before it was
   installed: all 49 STL outputs are byte-identical and only the manifest
   changed, by exactly two lines. **Two hashes were stale, not one.** The
   earlier note recorded only `canonical_model_sha256`; `nominal_pose_sha256`
   was stale for the same reason, because the 2026-08-18 repoint edited the
   evidence-source path in both `config/model/canonical_model_v1.yaml` and
   `config/poses/nominal_standing_reference_v0.yaml`.
   - `canonical_model_sha256`: `2286773314ded079...` -> `71dba5050f1f402b...`
   - `nominal_pose_sha256`: `76ba6ad316237ae1...` -> `2715b641788da5c8...`

2. `araco_perception` —
   `test_sensor_contract.py::test_rtabmap_rviz_layout_covers_2d_and_colored_3d_maps`.
   Fixed in the test by comparing `display['Topic']['Value']`, matching the Map
   assertion above it. The RViz layout was not changed and is correct.

Working tree contains only these two edits. Not committed; no commit was
authorized.

Note: `meshes/detailed/normalization_manifest.json` still embeds the stale
`nominal_pose_sha256`. No test covers that file, so it was left alone. It
should be regenerated or retired deliberately.

## Gate 0-6 rerun at 2026-08-18 (post-fix)

Run from installed space into `log/`, not `/tmp`. The mandated rerun found two
real scoring failures and one real teardown defect. One of the three, the Gate
5 failure, has since been root-caused and fixed. The Gate 0-5 precondition is
still not met and route 09 remains blocked. Gate 6 halted in preflight at
Gate 2 on the teardown defect.

| Gate | Result | Evidence directory | Run fingerprint |
| --- | --- | --- | --- |
| 0 | PASS | `log/gate_0_20260818_slam_regression` | ci `a7df64b2fdc9c476...` dev `7925dd73d7eaf0e1...` |
| 1 | FAIL (1 PASS of 6) | `log/gate_1_20260818_slam_regression`(PASS), `_02`,`_03`,`_04` | `a7df64b2fdc9c476...` |
| 2 | FAIL (0 of 2) | `log/gate_2_20260818_slam_regression`, `_02` | `a7df64b2fdc9c476...` |
| 3 | PASS | `log/gate_3_20260818_slam_regression` | `67d86b7cc029fa50...` |
| 4 | scoring PASS after GPU fix | `log/gate_4_20260819_nvidia_full_02` (8/8 cases); `_slam_regression`,`_02` pre-fix | `133e92276ea5fd07...` |
| 5 | FAIL (0 of 3) | `_01`,`_02` pre-fix; `log/gate_5_20260818_slam_regression_03` post-fix, 28/29 | `812d652eb82b56dd...` |
| 6 | FAIL | `log/gate_6_20260818_slam_regression` | scenario `c442bc2b70947fdd...` |

Gate 0 behavior fingerprint: `228c8ca49d0f146bf9e2d86e6c0f8b5e3fa62d9dd151a733960c929dffacc3bb`.
This replaces `4f5d37e91c937543fae18dc76793b57eb58adabacba3c72eba91fd1677f14dc8`
from the 2026-08-16 `gate_0_20260816_phase5_final` run. Gates 1-4 report the
same behavior fingerprint as Gate 0. **Gate 5 does not, and never did:** it runs
`gazebo_gate5_v0` and reports `92fc5afca01d5783...`. The 2026-08-18 and
2026-08-22 Gate 5 runs agree exactly on that value, so it is stable and
correct. The earlier blanket "Gates 1-5" claim here was wrong. Input-selection fingerprints for Gate 0:
ci `85e8fba289fb4364...`, development `5d92d70b107db8ca...`.

The Gate 0 `source_revision` is `unreported-dirty-or-installed-tree` because the
two test fixes are uncommitted.

### Gate 6 outcome

Gate 6 ran to completion with `--build-base build --install-base install` and
FAILED. Its own stages that passed are worth keeping:

- `package_tests` and `package_test_results`: PASS. Gate 6 independently
  reproduced `424 tests, 0 errors, 0 failures, 26 skipped` from installed space,
  confirming the two test fixes.
- `sanitizers` and `no_sanitizer_diagnostic`: PASS. The sanitizer build and
  suite produced no diagnostic.
- `no_lifecycle_deadlock`: PASS.

Failed checks: `gates_0_through_5_preflight`,
`three_complete_no_retry_repetitions`, `suite_wall_budget`,
`no_unclassified_error_or_fatal`.

**Gate 6 halted in preflight at Gate 2, so it never reached Gates 3-5 and never
exercised Regressions A or B.** Preflight Gate 0 PASS, Gate 1 PASS, Gate 2 FAIL
on `launch_exit` and `launch_log_clean` only. The proximate cause of the Gate 6
failure is therefore Defect C, the intermittent teardown deadlock, not the two
scoring regressions. Both still have to be fixed.

`automatic_retry_performed` is `false`; the runner does not retry a required
attempt. Environment captured: Gazebo `8.11.0`, ROS 2 Jazzy,
`rmw_fastrtps_cpp`, git revision `0098cbb` with the three worktree changes
listed.

### Regression A — Gate 4 yaw JOINT_STATE_STALE — FIXED 2026-08-19 (environment)

**Root cause was the graphics stack, not the gait and not the watchdog.**
Gazebo was rendering the robot's cameras in **software**. This machine has an
Intel Iris Xe iGPU and an NVIDIA RTX 4060 (driver 595.84, working), with both
`10_nvidia.json` and `50_mesa.json` EGL vendors installed. Headless gz picked
Mesa, failed with `libEGL warning: egl: failed to create dri2 screen`, and fell
back to llvmpipe. The NVIDIA GPU sat at 0% and 15 MiB during gate runs.

Software rendering of the 15 Hz `gemini_rgbd` and `gemini_color` cameras pushed
the real-time factor down to ~0.48 and produced wall-clock scheduling gaps of
115-138 ms in `/joint_states`. The safety supervisor's wall-clock
`joint_state_timeout_s` of 0.1 s then tripped `REASON_JOINT_STATE_STALE` (18),
latching `FAULT_HOLD`, aborting `yaw_left`, and leaving `yaw_right` and
`combined` unable to acquire authority.

Fix — per-process environment only, **no source or config change**:

```bash
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia
```

Measured effect on Gate 4:

| | before | after |
| --- | --- | --- |
| NVIDIA GPU use | 0%, 15 MiB | up to 55%, 736 MiB |
| `dri2 screen` errors | 2 | 0 |
| `reason=18` faults | 2 | 0 |
| RTF (yaw case alone) | 0.484 | 0.887 |
| RTF (full 8-case matrix) | 0.693 | 0.731 |
| scorer | FAIL | **PASS, all 8 cases** |

`log/gate_4_20260819_nvidia_full_02` — `precision_forward`, `forward`,
`reverse`, `left`, `right`, `yaw_left`, `yaw_right`, `combined` all PASS.

**Evidence integrity: the run fingerprint is unchanged at
`133e92276ea5fd07...` and the behavior fingerprint at `228c8ca49d0f146b...`,
identical to the failing 2026-08-18 runs.** Same configuration, different
runtime environment. The earlier gate results were therefore valid evidence of
a real environmental defect, not of a configuration difference.

Gate 4 still reports FAIL overall, but now only on `launch_log_clean`, caused by
the Defect C shutdown `SIGSEGV` (exit code 139). Every scored check passes.

Withdrawn along the way: the earlier "tripod yaw loses support / suspect the
`legacy_rotation_scale` blend" theory, and the follow-on theory that the
watchdog itself needed relaxing. **No safety threshold was changed and no gait
code was touched.** The offline gait replay and the isolated-case run that
disproved the gait theory remain valid.

One `REASON_CONTROLLER_NOT_READY` (20) startup abort was seen in the first full
GPU run and did not reproduce on rerun. Treat as a startup flake unless it
recurs.

**Made durable 2026-08-19 in `~/.bashrc`** (operator's choice), as a guarded
block that no-ops when `/usr/share/glvnd/egl_vendor.d/10_nvidia.json` is absent
and never overrides an already-set value. Repository source was deliberately
left unchanged, because hardcoding NVIDIA selection into
`araco_bringup/launch/gazebo.launch.py` would be wrong on machines without an
NVIDIA EGL vendor.

Verified end to end with no manual exports, relying only on `~/.bashrc`:
`log/gate_4_20260819_bashrc_verify` — `yaw_left` PASS, 7 cycles, RTF 0.836,
zero `reason=18`, zero `dri2 screen` errors.

Caveat: `~/.bashrc` only applies to interactive shells. Gate runs started from a
desktop launcher, a cron job, or CI will **not** inherit these variables and will
silently fall back to software rendering. If gates ever need to run
non-interactively, this must be solved again at that layer.

### Gate 6 outcome

Gate 6 ran to completion with `--build-base build --install-base install` and
FAILED. Its own stages that passed are worth keeping:

- `package_tests` and `package_test_results`: PASS. Gate 6 independently
  reproduced `424 tests, 0 errors, 0 failures, 26 skipped` from installed space,
  confirming the two test fixes.
- `sanitizers` and `no_sanitizer_diagnostic`: PASS. The sanitizer build and
  suite produced no diagnostic.
- `no_lifecycle_deadlock`: PASS.

Failed checks: `gates_0_through_5_preflight`,
`three_complete_no_retry_repetitions`, `suite_wall_budget`,
`no_unclassified_error_or_fatal`.

**Gate 6 halted in preflight at Gate 2, so it never reached Gates 3-5 and never
exercised Regressions A or B.** Preflight Gate 0 PASS, Gate 1 PASS, Gate 2 FAIL
on `launch_exit` and `launch_log_clean` only. The proximate cause of the Gate 6
failure is therefore Defect C, the intermittent teardown deadlock, not the two
scoring regressions. Both still have to be fixed.

`automatic_retry_performed` is `false`; the runner does not retry a required
attempt. Environment captured: Gazebo `8.11.0`, ROS 2 Jazzy,
`rmw_fastrtps_cpp`, git revision `0098cbb` with the three worktree changes
listed.

### Regression A — Gate 4 yaw case aborted by JOINT_STATE_STALE (blocking)

**Corrected characterization, 2026-08-19.** This was first recorded as "tripod
yaw loses support", suspected in the `legacy_rotation_scale` /
`rotation_warm_start` blend added by `f1e41af`. **The gait is not defective and
that lead is withdrawn.** Two independent checks:

- An offline driver linking the real `tripod_gait.cpp` with the real
  `tripod_slow_sim_v0` values (`base_cadence 1.0`, `maximum_stride_m 0.06`,
  `swing_clearance_m 0.03`, `planar_command_scale 0.05`,
  `yaw_command_scale 0.3`) replayed a pure 0.2 rad/s yaw for 400 steps:
  **0 non-monotonic phase events, 0 lift-without-swing-flag events.** The
  startup handover and the `legacy_curve_phase` swing/lift alignment are
  self-consistent.
- Running `yaw_left` **alone** (`--case-name yaw_left`) reports
  `minimum_support_contacts: 3`. The support loss reported in the full 8-case
  run did not reproduce, so it is a downstream artifact, not the cause.

What actually happens: the `yaw_left` case is aborted by a safety fault
`REASON_JOINT_STATE_STALE` (18), seen twice in every Gate 4 run including the
isolated one. The supervisor latches `FAULT_HOLD`, which is why `yaw_right` and
`combined` then report `authority acquisition failed`. `gait_cycles_completed`
is 4 instead of 7 because the case is cut short.

Mechanism: `joint_state_timeout_s` is `0.1` and is evaluated by
`fresh(joint_receipt_, joint_timeout)` in `safety_supervisor_node.cpp`, where
`joint_receipt_` is a `SteadyClock` (wall) stamp. The `/joint_states` stream is
paced by **simulation** time, so its wall-clock rate scales with the real-time
factor. Measured during the yaw case on a pinned domain (1605 samples):

| metric | value |
| --- | --- |
| mean gap | 17.5 ms |
| p99 gap | 109 ms |
| max gap | 137.6 ms |
| gaps over the 100 ms budget | 38 |

These are marginal overruns of roughly 8x nominal jitter, **not** a stall. RTF
measured 0.484 (yaw alone) to 0.697 (full matrix), and headless runs log
`libEGL warning: egl: failed to create dri2 screen`, indicating a **software**
GL fallback.

Attribution is partly open. The watchdog values were **not** changed by
`f1e41af` (`watchdogs_s.joint_state: 0.1` predates it; that commit added only
`startup_readiness_stable_s`). `f1e41af` did add an always-on 15 Hz
`gemini_rgbd` camera, a 15 Hz `gemini_color` camera and a 100 Hz IMU to the
robot, and added the `araco.perception.gemini-335-sim` artifact to the **Gate 4
profile** — a locomotion gate that does not need rendering. `gemini_rgbd` first
appears in `f1e41af`.

**That added-cost hypothesis is plausible but UNPROVEN.** An attempt to A/B it
by removing the sensor from `gazebo_gate4_v0.yaml` failed to test anything: the
composer requires the artifact (`expected exactly one selected
simulated_rgbd_imu artifact`), so the runtime bundle was never emitted and the
run produced no usable timing data. The profile was restored and verified by
recomposition; the run fingerprint is back to `133e92276ea5fd07...`.

No fix applied. Every available option is a design or safety decision:

1. Make the simulator-facing staleness check sim-clock based, or scale it by
   RTF. Note the current use of steady clock looks deliberate: it lets a
   stalled sim clock be detected, and a separate `clock_progress` watchdog
   exists. On real hardware wall time is the correct basis.
2. Relax `watchdogs_s.joint_state` in the simulator-only safety policy
   (`araco_supervision/config/policy/simulator_v0.yaml`, `simulator_only`
   scope) with a version bump. This weakens a safety threshold and must be an
   explicit owner decision.
3. Restore hardware GL so rendering stops falling back to software and RTF
   recovers. Safety-neutral and environmental; the EGL dri2 failure is the
   concrete lead. Try this first.
4. Add a sensor-artifact variant with the camera disabled for the locomotion
   gates, plus composer support for it. This is the only option that removes
   the cost rather than accommodating it, and it is the largest change.

### Gate 6 outcome

Gate 6 ran to completion with `--build-base build --install-base install` and
FAILED. Its own stages that passed are worth keeping:

- `package_tests` and `package_test_results`: PASS. Gate 6 independently
  reproduced `424 tests, 0 errors, 0 failures, 26 skipped` from installed space,
  confirming the two test fixes.
- `sanitizers` and `no_sanitizer_diagnostic`: PASS. The sanitizer build and
  suite produced no diagnostic.
- `no_lifecycle_deadlock`: PASS.

Failed checks: `gates_0_through_5_preflight`,
`three_complete_no_retry_repetitions`, `suite_wall_budget`,
`no_unclassified_error_or_fatal`.

**Gate 6 halted in preflight at Gate 2, so it never reached Gates 3-5 and never
exercised Regressions A or B.** Preflight Gate 0 PASS, Gate 1 PASS, Gate 2 FAIL
on `launch_exit` and `launch_log_clean` only. The proximate cause of the Gate 6
failure is therefore Defect C, the intermittent teardown deadlock, not the two
scoring regressions. Both still have to be fixed.

`automatic_retry_performed` is `false`; the runner does not retry a required
attempt. Environment captured: Gazebo `8.11.0`, ROS 2 Jazzy,
`rmw_fastrtps_cpp`, git revision `0098cbb` with the three worktree changes
listed.

### Regression A — Gate 4 tripod yaw loses support (blocking)

Reproduced identically twice. The five linear cases
(`precision_forward`, `forward`, `reverse`, `left`, `right`) all PASS. Then:

- `yaw_left` FAIL: `minimum_support_contacts` reaches `0` while three swing legs
  are touching, `phase_monotonic` is `false`, `controlled_stop_seen` is `false`,
  and the scheduler reports `policy_valid: false` with `cadence_hz_min 0.0`,
  `stride_scale_min 0.0`, `velocity_scale_min 0.0`.
- `yaw_right` and `combined` then FAIL with `authority acquisition failed`,
  which looks like a cascade from the `yaw_left` fault rather than an
  independent defect.
- Failed scorer checks: `active_stand`, `all_direction_cases`, `manual_hold`.

Suspect `f1e41af`, which rewrote `tripod_gait.cpp` to the
`tripod_legacy_translation_rotation_blend_responsive_scheduler` with a separate
`legacy_rotation_scale` curve and a `rotation_warm_start` special case. The
gait config itself changed only `gait_id`, version, and evidence, so the
behavior change is in the C++ blend, not the artifact.

### Regression B — Gate 5 never reached enabled motion — FIXED 2026-08-18

**Corrected attribution.** This was first recorded as a suspected `f1e41af`
supervision regression (`gimbal_yaw_rad` intent contract,
`startup_readiness_stable_s` dwell). **That was wrong.** Investigating the
`gimbal_yaw_hard_rad` lead disproved it: the arbiter deliberately passes hard
limits into both the normal and hard envelope slots for every field, so the
apparent duplicate `gimbal_yaw_hard_rad, gimbal_yaw_hard_rad` pair in
`command_arbiter_node.cpp` is the intended pattern, not a defect.

Actual root cause: `src/araco_system_tests/scripts/araco_joint_state_relay`
lost its execute bit. Git recorded it as `100644` while all nine sibling
scripts are `100755`. Gate 5 is the only gate that starts the relay, and the
workspace uses `--symlink-install`, so the installed path is a symlink to the
non-executable source and `ros2 run` returned `No executable found`. The relay
never ran, joint-state readiness never set, readiness stalled at `91/127` with
`joints=0`, and the supervisor entered `FAULT_HOLD reason=19 fault_mask=8`
before ever reaching HOLDING.

Introduced by `9e0284b` (2026-08-17), **not** `f1e41af`. Gate 5 last passed
2026-08-16, the bit was dropped 2026-08-17, and gates were not rerun until
2026-08-18, so this sat undetected. The evidence that would have caught it went
to `/tmp` and was lost.

Fix applied: `chmod +x` plus `git update-index --chmod=+x` on that script. No
rebuild was needed because of symlink-install.

Result after the fix, `log/gate_5_20260818_slam_regression_03`: 28 of 29 scorer
checks pass, `fault_matrix_complete` true, `orderly_safety_shutdown` true,
`startup_failure` null. Gate 5's whole fault matrix now runs.

The single remaining Gate 5 scorer failure is
`backend_process_loss_quiesces_runtime`, and it **is Defect C, not a separate
defect**. That final scenario issues the same
`gz service -s /server_control --req 'stop: true'` and then requires the
runtime to quiesce within 2 s. While the server refuses to exit, the safe and
locomotion streams keep publishing and the check cannot pass.

Lesson worth keeping: a lost file mode is invisible to `colcon test` and to
code review of diffs. Consider a metadata test asserting every file in
`scripts/` is mode `100755`.

### Defect C — Gazebo shutdown race, upstream in gz-sim 8.11.0

**Status 2026-08-20: option 3 taken, committed as `8865e3c`. The defect is
now recorded as a named non-blocking upstream condition rather than counted
as a gate failure. It is not fixed, and options 1 and 2 remain open.** The
full decision, guards, and accepted limitations are in `DECISIONS.md` under
"Record the gz-sim teardown failure as a named non-blocking upstream
defect". The characterization below stands unchanged and is what justified
that choice.

**Corrected characterization, 2026-08-18.** An earlier entry in this file
claimed the orderly safety shutdown triggers this, "isolated with a controlled
pair of runs". **That claim is withdrawn.** It rested on one run per arm, and
the failure is intermittent, so it was a coincidence. A 3-vs-3 repetition on
`gazebo_ci_v0` shows no effect from the safety shutdown:

| | exited | wedged |
| --- | --- | --- |
| with orderly safety shutdown | 2 | 1 |
| without | 1 | 2 |

Gate 3 also sends the orderly shutdown and tears down cleanly, which is
consistent with the corrected reading. Do not look for this in the
safety/arbitration path.

What actually happens: on `gz service -s /server_control --req 'stop: true'`
the server reaches one of three outcomes, non-deterministically — clean exit,
`SIGSEGV`, or hang.

- **Hang:** all 56 threads sleeping, 40 in `futex_do_wait`. No progress, not a
  busy loop. The gz log stops right after `Successfully switched controllers!`
  and never reaches the `controller_manager.pal_statistics` teardown lines that
  a clean shutdown emits.
- **SIGSEGV:** null dereference (`Address not mapped to object (nil)`) on a
  gz-sim worker thread. Post-mortem backtrace from the apport core of the Gate
  5 run (`gdb` on a core needs no `ptrace_scope` change):
  `clone3` -> `start_thread` -> libstdc++ thread trampoline -> two frames inside
  `libgz-sim8.so.8`. So it is a gz-sim internal thread faulting during teardown.
  Exact function not nameable: `libgz-sim8` is stripped and the frames are local
  symbols, the nearest exported symbols being 5864 and 273 bytes away and
  therefore meaningless. Naming it needs gz-sim debug symbols.

Scope, established by elimination — each arm run three times:

| Configuration | Result |
| --- | --- |
| stock Gazebo world (`shapes.sdf`), no Araco plugins | clean 3/3 |
| our `resolved_world.sdf` alone, no robot, no ROS nodes | clean 3/3 |
| full launch: robot spawned with `gz_ros2_control` + controllers | fails ~50% |

So the world's own plugin set (contact, imu, physics, scene-broadcaster,
sensors, user-commands) is **not** sufficient. The trigger needs the robot model
with `gz_ros2_control`, which hosts the `controller_manager` inside the server
process.

**Conclusion: this is an upstream shutdown race in gz-sim 8.11.0 exercised via
`gz_ros2_control` 1.2.19, not a defect in Araco code.** No Araco source change
will fix it directly. Both failure modes occur strictly after all scored
behavior has completed and after `metrics.json` is written, which is why Gates
1 and 2 pass every scored check and fail only `launch_exit` and
`launch_log_clean`.

Options, none of which should be chosen silently:

1. Install gz-sim debug symbols, symbolize the core, and file upstream.
   **Still open.**
2. Upgrade or patch Gazebo. **Still open.**
3. Change the gate contract so "server failed to exit cleanly" is recorded as a
   distinct, explicitly tracked upstream condition instead of being conflated
   with `launch_log_clean`. This is now defensible because the defect is
   upstream and post-scoring, but it is a contract change and is the operator's
   decision, not the agent's. It must not be done by quietly enlarging the
   runner's 5 s wait, which would hide a real crash.
   **Taken 2026-08-20 as `8865e3c`.** The 5 s wait was left alone, as
   required. Gates 1-5 share `araco_gate1_evidence`, so one change covers
   all five; Gate 6 classifies the same signatures in its log scan.
   Attribution requires that scoring completed and that a stop was
   requested, only `[gazebo-1]` may be excused for a crash signal, and
   group-signal deaths count only when the runner actually escalated.
   Every attributed line is written to evidence under
   `upstream_defects.gz_sim_shutdown`, so a PASS now means "scored clean,
   any unclean exit matched the recorded signature" rather than "the
   simulator exited cleanly". Covered by six unit tests; **not yet
   exercised by a gate run.**

Operational note: the wrapper matched by `pgrep -f resolved_world.sdf` is
`/bin/sh`, not the server; the real server is its child. Do not use `pkill -f`
with a pattern that also matches your own shell command line.

## Gate 0-5 rerun at 2026-08-22 — all six PASS

First all-green Gate 0-5 result, and the first live exercise of the `8865e3c`
shutdown-defect classification. Run from installed space into `log/`, tag
`20260822_defectc_class`.

| Gate | Result | Run fingerprint | Behavior fingerprint | Defect C variant seen |
| --- | --- | --- | --- | --- |
| 0 | PASS | ci `a7df64b2fdc9c476...` dev `7925dd73d7eaf0e1...` | `228c8ca49d0f146b...` | n/a, no simulator |
| 1 | PASS | `a7df64b2fdc9c476...` | `228c8ca49d0f146b...` | SIGSEGV + escalation |
| 2 | PASS | `a7df64b2fdc9c476...` | `228c8ca49d0f146b...` | SIGSEGV, clean launch exit |
| 3 | PASS | `67d86b7cc029fa50...` | `228c8ca49d0f146b...` | hang |
| 4 | PASS, 8/8 cases | `133e92276ea5fd07...` | `228c8ca49d0f146b...` | hang |
| 5 | PASS, 29/29 checks | `812d652eb82b56dd...` | `92fc5afca01d5783...` | SIGSEGV, clean launch exit |

**Every run fingerprint reproduces its previously recorded value exactly.** Gate
0's input-selection fingerprints also reproduce: ci `85e8fba289fb4364...`,
development `5d92d70b107db8ca...`. Gate 5 reported 29/29 and Gate 4 all eight
cases; nothing else moved.

**Caveat added later the same day: Gate 5's 29/29 was variant-dependent.** It
passed because that run drew the crash form of Defect C. Later runs of the same
gate returned 28/29 whenever the hang form occurred. See "Gate 5's last scorer
check is decided by which Defect C variant occurs". This table records what the
run produced; it is not a claim that Gate 5 passes reliably.

`source_revision` is again `unreported-dirty-or-installed-tree`, because the
2026-08-22 documentation edits are uncommitted. The identical fingerprints
confirm documentation content is not part of artifact identity.

### The classification behaved correctly on all three variants

- **SIGSEGV with escalation** (Gate 1): `[gazebo-1] Segmentation fault`, launch
  return code `-15`, `escalated: true`, six lines attributed — the gazebo crash
  plus five nodes killed by the group signal.
- **SIGSEGV with a clean launch exit** (Gates 2 and 5): return code `0`, no
  escalation, three lines, all `[gazebo-1]`.
- **Hang** (Gates 3 and 4): return code `-15`, `escalated: true`, five lines,
  **no `[gazebo-1]` line at all**. A deadlocked server logs nothing, so
  attribution rests entirely on the escalation rule. This is the weakest of the
  three: any other cause of launch failing to exit within 5 s would present
  identically. It is consistent with the design but should be remembered when
  reading a Gate result that reports the hang variant.

No gate reported an unclassified error line, and no gate was excused a failure
it should have kept: Gates 4 and 5 failed loudly on scored checks in the
contaminated attempt described below, exactly as the guards intend.

### Defect C leaves an orphaned server that poisons the next gate

**Found 2026-08-22 and not previously recorded.** When the hang variant fires,
the runner signals the process group, but the real `gz sim` server is a *child*
of the `/bin/sh` wrapper and survives. It keeps running at roughly 70% CPU on
the same DDS domain.

The first attempt at this rerun ran Gates 2-5 back to back with no cleanup
between them. Gate 3's server orphaned at 19:38:29 and was still alive through
both Gate 4 and Gate 5:

- **Gate 4 failed `gate4_score`** after 43 s with zero cases run. Its safety
  supervisor went silent for 4.2 s, resumed with `joints=0 controllers=0`, and
  latched `state=6 reason=20` (`CONTROLLER_NOT_READY`) 105 microseconds later,
  recovering to `127/127` just 240 ms after that. A starvation blip, not a
  controller defect. Zero `dri2 screen` errors, so this was **not** Regression A
  returning.
- **Gate 5 failed** `gate5_score` and `backend_process_loss_proven`.

Rerun in isolation with the orphan reaped first, Gate 4 passed all eight cases
over 77.8 simulated seconds and Gate 5 passed 29/29. Preserved for comparison:
`log/gate_4_20260822_orphancontam`, `log/gate_5_20260822_orphancontam`. **Those
two directories are invalid evidence.**

The orphan **ignores SIGTERM** and needs SIGKILL — expected, since the process
is deadlocked in `futex_do_wait`. Reap by PID from `pgrep -x "gz sim"`. Do not
`pkill -f` on the world path: the wrapper is `/bin/sh` and the pattern also
matches your own command line.

**Implication for Gate 6, which has not been verified:** Gate 6 runs preflight
Gates 0-5 and then three full repetitions sequentially in one process tree. If a
sub-gate orphans a server, every later sub-gate runs against a CPU competitor,
and Gate 6 does no reaping between them. The 2026-08-18 Gate 6 failure was
attributed to preflight halting at Gate 2 on Defect C; that reading is still
correct for that run, since preflight stopped before anything could cascade. But
any Gate 6 run that gets past preflight is exposed. Adding a reap between
sub-gates is a runner change and is the operator's call.

Operational rule for any sequential gate run:

```bash
pgrep -x "gz sim" && kill -KILL $(pgrep -x "gz sim")
```

## `8865e3c` shipped unlinted code and failed Gate 6 (fixed 2026-08-22)

The first Gate 6 run on 2026-08-22 failed in four minutes with
`432 tests, 0 errors, 8 failures, 26 skipped`. **Every failure was a linter
failure on `araco_system_tests`, all of it in the code `8865e3c` added.** That
commit was never linted before it was committed and pushed.

- flake8, 4: import order in `gate6.py` — the configured style sorts
  case-insensitively, so `launch_exit_code` belongs between
  `GAZEBO_CRASH_EXIT_CODES` and `TEARDOWN_SIGNAL_EXIT_CODES` — plus three
  double-quoted string fragments in `test_gate1_scoring.py`. Only the fragments
  containing no single quote of their own were converted; the ones holding
  `cmd '...'` correctly stay double-quoted.
- pep257, 2: `D213` on the two new multi-line docstrings, in
  `gate1.classify_launch_log` and `gate6.is_gz_shutdown_defect`. The enforced
  style puts the summary on the second line. There was no precedent to copy:
  every other docstring in the package is a single line.

The remaining four Gate 6 failures — `gates_0_through_5_preflight`,
`three_complete_no_retry_repetitions`, `suite_wall_budget`, and
`no_unclassified_error_or_fatal` — were pure cascade. The run aborted at package
tests, so no simulator ever started. The evidence for that is the **absence of a
`preflight/` directory** in `log/gate_6_20260822_defectc_class`, not the orphan
sampler that ran alongside it: that sampler used `pgrep -x "gz sim"` and was
blind, for the reason recorded in the next section.

Fixed and verified with the authoritative ament linters, not a hand-rolled
flake8 invocation — a local `python3 -m flake8` with guessed options reports
`W504` on pre-existing lines and is not the configured check. After the fix,
`colcon test --packages-select araco_system_tests` reports
`67 tests, 0 errors, 0 failures, 0 skipped`.

Lesson worth keeping: this defect had nothing to do with Defect C and would have
failed Gate 6 on its own. Run `colcon test --packages-select araco_system_tests`
after editing anything in that package, before running the gates.

## Gate 6 at 2026-08-22 — seven of nine checks pass, orphan cascade confirmed

Second run, after the lint fix: `log/gate_6_20260822_defectc_class_02`, 773 s.

| Check | Result |
| --- | --- |
| `package_tests` | PASS |
| `package_test_results` | PASS |
| `sanitizers` | PASS |
| `no_sanitizer_diagnostic` | PASS |
| `no_lifecycle_deadlock` | PASS |
| `no_unclassified_error_or_fatal` | PASS |
| `gates_0_through_5_preflight` | **PASS — first time** |
| `three_complete_no_retry_repetitions` | FAIL |
| `suite_wall_budget` | FAIL |

`no_unclassified_error_or_fatal` passing is the live confirmation that the Gate 6
half of the `8865e3c` classification works across a whole log tree.

### Both remaining failures are one event

`suite_wall_budget` is not a timing problem. It reads:

```python
checks['suite_wall_budget'] = (
    len(repetition_wall) == registry['repetitions'] and
    all(value <= suite_wall_limit for value in repetition_wall))
```

Only one repetition ran, so `len(...) == 1 != 3` and the check fails on arity,
not on duration. The one repetition that did run took 121.65 s against a 260 s
limit. Both failures therefore reduce to: **repetition 1 stopped early**, and
the loop has `if not passed: break`.

Repetition 1 ran gates 0, 1, 2 PASS and then **gate 3 FAIL**, on
`gate3_score`: `motion_enabled_observed`, `trusted_enable_accepted`,
`release_returns_to_hold`, and `all_pose_cases` all false. The same gate 3
passed standalone an hour earlier.

### Cause: orphaned servers starve the next sub-gate of CPU

The failing repetition gate 3 latched `state=6 reason=23`,
**`REASON_TIME_DISCONTINUITY`**, with readiness collapsing to `3/127`. Zero
`dri2` errors, so rendering was fine.

Four orphaned `gz sim` servers were left running by this Gate 6 run, started
20:02:38, 20:03:17, 20:05:23 and 20:09:16, still alive after it exited, one at
75% CPU.

**Corrected 2026-08-22.** An earlier version of this section blamed `/clock`
crosstalk on a shared DDS domain. **That was wrong, and the claim is
withdrawn.** `araco_gate1_evidence` already isolates every run: it sets
`ROS_DOMAIN_ID` to `100 + os.getpid() % 100` when `--domain-id` is absent, and a
unique `GZ_PARTITION` alongside it. The domains actually recorded in this run
were preflight `106, 138, 178, 163, 180` and repetition `100, 130, 125` — all
distinct, and the orphans held domains of their own. No orphan could publish
into the failing gate's domain.

The mechanism is contention, not crosstalk. Three to four deadlocked servers
running full physics leave too little CPU for the new sub-gate, its own `/clock`
publishing stutters, and the supervisor faults on the gap. This is the same
class of failure as the standalone Gate 4 contamination earlier the same day,
which showed a 4.2 s supervisor stall under one orphan.

Chain, end to end: Defect C hang -> the runner signals the process group but the
real server is a child of the `/bin/sh` wrapper and survives -> the orphan
ignores SIGTERM because it is deadlocked in `futex_do_wait` -> it keeps running
full physics and burning CPU -> a later sub-gate is starved and faults on time
discontinuity -> the repetition breaks -> `three_complete_no_retry_repetitions`
and `suite_wall_budget` both fail.

This supersedes the 2026-08-18 reading that Gate 6 fails because preflight halts
at Gate 2. That was true then. Preflight now passes and the failure has moved.

### Correction: the orphan sampler used in both runs was invalid

It counted with `pgrep -x "gz sim"`, which matches the process **name**, and the
server's name is `ruby` — the string `gz sim -r -s ...` is only its argument
list. The sampler reported a peak of zero throughout a run that in fact leaked
four servers, and the postflight "orphans: none" line was equally wrong. The
reap helper in the Gate 4-5 rerun script happened to work only because it had a
`pgrep -f '^gz sim -r -s'` fallback after the `-x` attempt.

**Use `pgrep -f '^gz sim'`.** Never `pgrep -x "gz sim"`, and never `pkill -f` on
the world path.

```bash
pgrep -f '^gz sim' && kill -KILL $(pgrep -f '^gz sim')
```

### Decision needed before Gate 6 can pass

No Araco behavior is wrong here; the gate harness does not isolate its sub-gates
from a known upstream leak. Options, for the operator:

1. Reap orphaned servers between sub-gates in `araco_gate6_evidence`. Smallest
   change, directly targets the observed cause.
2. Give each sub-gate its own `ROS_DOMAIN_ID`. `araco_gate1_evidence` already
   takes `--domain-id`, so this is wiring, and it isolates `/clock` even from an
   orphan that is still alive. Does not reclaim the CPU an orphan burns.
3. Both. Recommended: 2 prevents the interference, 1 stops the machine filling
   with deadlocked servers over a long suite.

All three are runner changes, so none was made. Note this is the *harness*
reacting to the upstream defect, a different question from the Defect C gate
contract already settled on 2026-08-20.

## Gate 5's last scorer check is decided by which Defect C variant occurs — FIXED 2026-08-22

**Established 2026-08-22 by direct experiment, and fixed the same day by option
2 below.** It was the top blocker. The diagnosis is kept in full because the fix
only makes sense against it; see "Resolved" at the end of this section.

`backend_process_loss_quiesces_runtime` is the 29th Gate 5 scorer check. Its
outcome tracks the Defect C variant exactly, with no exceptions in five
observations:

| Run | Variant | `quiesce` |
| --- | --- | --- |
| `gate_5_20260822_defectc_class` | crash, rc `0`, no escalation | **PASS** |
| `gate_5_20260822_probe_explicitdomain` | crash, rc `0`, no escalation | **PASS** |
| `gate_5_20260822_probe_default` | hang, rc `-15`, escalated | FAIL |
| `gate_6_20260822_reap_domains` preflight gate 5 | hang, rc `-15`, escalated | FAIL |
| `gate_5_20260822_orphancontam` | hang, rc `-15`, escalated | FAIL |

The mechanism was already recorded correctly in the Regression B section: the
final Gate 5 scenario issues the same `/server_control stop` and then requires
the runtime to quiesce within 2 s. When the server crashes it dies immediately
and the runtime quiesces. When it hangs, the backend is still alive and still
publishing, so the check cannot pass. **The check is not flaky.** It is a
deterministic function of a non-deterministic upstream outcome, which the
2026-08-18 3-vs-3 repetition put at roughly 50/50.

### This is why Gate 6 could not pass (before the fix)

Gate 6 runs Gate 5 four times: once in preflight and once per repetition. At
roughly even odds per run, all four landing on the crash variant is about a 6%
outcome. Reaping does not help — the orphan is a *consequence* of the hang, and
by the time it is reaped the scored check has already failed.

**The 2026-08-20 Option 3 decision does not cover this.** That classification
was deliberately scoped to `launch_exit` and `launch_log_clean`, and it
deliberately never excuses a scored check. This is a scored check. So Defect C
still blocks Gate 6, through a path the contract change was never meant to
address.

### The 2026-08-22 all-green Gate 0-5 result was variant-dependent

Recorded honestly: that run's Gate 5 passed because it drew the crash variant.
It was a real pass of every check, reproduced fingerprints and all, but it is
**not** evidence that Gate 5 passes reliably. Re-running Gate 5 today produced
29/29 twice and 28/29 three times.

### Ruled out by experiment, not assumption

The explicit `--domain-id` added on 2026-08-22 was suspected when preflight
gate 5 failed. Two standalone probes settled it: **arm A with the default
pid-derived domain FAILED 28/29, arm B with an explicit `--domain-id 145`
PASSED 29/29** — the opposite of what a domain-id regression would produce.
The check also failed on 2026-08-18 in
`gate_5_20260818_slam_regression_03`, before any of this existed.

### Options, for the operator

1. Fix the upstream hang — upgrade or patch Gazebo, or file it. The only option
   that removes the cause rather than working around it.
2. Change the Gate 5 scenario so it forces the backend dead — SIGKILL once the
   graceful stop is seen to fail — and only then asserts quiescence within 2 s.
   **Recommended.** The property under test is "the runtime quiesces when the
   backend is lost". When the server hangs the backend is not lost, so the
   scenario's own premise is unmet and the current result is not a true
   negative. Forcing the kill tests the real property and stops an upstream
   hang presenting as an Araco safety failure.
3. Extend the shutdown-defect classification to this scored check. **Not
   recommended.** It would excuse a genuine safety assertion on the strength of
   a log signature, which is exactly the line the 2026-08-20 decision drew and
   should keep.

### Resolved 2026-08-22 — the scenario now forces the backend dead

The operator chose **option 2**. The final Gate 5 scenario issues the same
graceful `/server_control stop`, waits 3 s for the server to exit, SIGKILLs it
if it has not, and only then asserts that the runtime quiesces within 2 s. The
check is not relaxed: quiescence is still asserted in full, over the same
window, against a premise that now actually holds. See the `DECISIONS.md` entry
of the same date for the reasoning and the full implementation notes.

Proven in both variants:

| Run | Variant | Forced | `quiesce` |
| --- | --- | --- | --- |
| `gate_5_20260822_forcekill_01` | crash | — | **PASS** |
| `gate_5_20260822_forcekill_02` | crash | — | **PASS** |
| `gate_5_20260822_forcekill_03` | crash | — | **PASS** |
| `gate_5_20260822_forcekill_04` | crash | — | **PASS** |
| `gate_5_20260822_forcekill_05` | **hang** | pid 27632 | **PASS** |

All five are 29/29 with no failing runner check. The hang variant is the case
that failed five of five before. The four crash-variant runs needed no kill,
which is the evidence that the graceful path is untouched.

Two findings came out of the work, both by experiment:

- **The graceful stop request was never the discriminator.** In a controlled
  deadlock reproduction — orderly shutdown, then server stop, leaving the server
  in `futex_do_wait` at 174% CPU — the `gz service` call still returned
  `data: true` and rc `0`. The old check's `backend_process_stop` conjunct was
  therefore true in both variants; only the quiesce measurement ever moved.
- **`ros2 launch` tracks the `ruby` wrapper, not the server.** Killing the
  server child leaves the wrapper exiting **137** (128 + 9), which was not in
  `GAZEBO_CRASH_EXIT_CODES`. Left unhandled, forcing the kill would have turned
  a `backend_process_loss_quiesces_runtime` failure into a `launch_log_clean`
  failure — moving the failure rather than removing it. 137 is now classified,
  on `[gazebo-1]` lines only.

The forced kill also removes the teardown escalation: the hang-variant run
finished at `launch_return_code: 0` with `escalated: false` and left no orphan,
where that variant previously ended at rc `-15` with the runner signalling the
whole process group. Reaping in `araco_gate6_evidence` stays load-bearing all
the same, because gates 1-4 still tear down through the orderly shutdown
followed by the server stop, which is the documented reliable hang trigger.

`upstream_defects.gz_sim_shutdown.observed` stays `true` on both variants. The
defect is still reported; only its consequence for a scored safety assertion is
removed.

## Gate 6 at 2026-08-23 — twenty of twenty-one checks, three complete repetitions

`log/gate_6_20260822_forcekill_01`, started 2026-08-22 and finished 2026-08-23,
the first run after the Gate 5 forced-kill fix.

**`three_complete_no_retry_repetitions` passes.** All three repetitions ran all
six sub-gates with no retry, which unlocks the twelve comparison checks that can
only be evaluated once three repetitions exist. Every one of them passes:
`identical_behavior_fingerprints`, `identical_case_sets`,
`exact_discrete_outcomes`, `median_real_time_factor`, and the eight per-case
`*_physical_repeatability` checks.

The check list grew from nine to twenty-one for that reason, so the counts are
not directly comparable run to run. Substantively: everything that failed before
now passes, and one check fails that had never been reached on its merits.

| Check | Result |
| --- | --- |
| `package_tests`, `package_test_results` | PASS |
| `sanitizers`, `no_sanitizer_diagnostic` | PASS |
| `no_lifecycle_deadlock` | PASS |
| `no_unclassified_error_or_fatal` | PASS |
| `gates_0_through_5_preflight` | PASS |
| `three_complete_no_retry_repetitions` | **PASS — first time** |
| twelve repetition-comparison checks | **PASS — first time evaluated** |
| `suite_wall_budget` | FAIL |

Preflight gate 5 drew the **hang** variant and passed, forcing pid 33314 dead.
That is precisely the event that ended the previous Gate 6 run at its preflight.

### `suite_wall_budget` now fails on duration, not on arity

The previous failure was arity: only one repetition ran, so `len(...) == 1 != 3`.
This time all three ran and each exceeded the limit:

| Repetition | Wall | Over 260.0 s by |
| --- | --- | --- |
| 1 | 298.3 s | 38.3 s |
| 2 | 292.1 s | 32.1 s |
| 3 | 323.4 s | 63.4 s |

The limit is derived, not configured directly:

```python
suite_wall_limit = (
    2.0 * thresholds['planned_complete_suite_sim_s'] +
    thresholds['startup_artifact_allowance_s'])
```

which is `2.0 * 100.0 + 60.0 = 260.0` s. Sub-gate launch wall alone accounts for
almost all of it — 285 s, 283 s, and 306 s respectively:

| Repetition | gate 1 | gate 2 | gate 3 | gate 4 | gate 5 |
| --- | --- | --- | --- | --- | --- |
| 1 | 29 s | 27 s | 72 s | 115 s | 42 s |
| 2 | 34 s | 26 s | 68 s | 113 s | 42 s |
| 3 | 36 s | 36 s | 76 s | 118 s | 41 s |

**This is the stale-threshold question recorded on 2026-08-22, now with
evidence.** `planned_complete_suite_sim_s` is still 100.0 while Gate 4 alone
consumes 77.8 simulated seconds; the budget was set when the suite was smaller.
No threshold was changed. It is a contract number, so it is the operator's call,
and it needs its own decision entry rather than being quietly raised to whatever
this run happened to measure.

### One reaped orphan was recorded as `SURVIVED`, most likely wrongly

`metrics.orphan_servers_reaped` holds six records for this run. Five ended in
`SIGKILL`; one — gate 3 of repetition 1, pid 34875 — is recorded as `SURVIVED`.

That record is probably an artifact of how the reaper tests liveness.
`_process_alive()` in `araco_gate6_evidence` uses `os.kill(pid, 0)`, **which
succeeds on a zombie**, and a SIGKILLed server lingers as a zombie until its
`/bin/sh` wrapper reaps it. The Gate 5 scorer avoids this by reading process
state out of `/proc` instead. Supporting evidence, though not proof: no `gz sim`
process was alive after the run, and repetition 1 went on to pass — a genuinely
surviving server at high CPU is what starved a sub-gate in the previous
campaign, and gate 4 of repetition 1 ran 115 s, in line with the other two.

Not fixed here: it is a different gate's runner and it overstates leakage rather
than hiding it, so it corrupts evidence in the safe direction. Worth closing
with the same `/proc` check the scorer uses.

## Gates 2-5 run stale code unless the workspace is rebuilt (found 2026-08-22)

`araco_gate1_evidence` is the shared runner for Gates 1-5. `CMakeLists.txt`
installs it four more times with `RENAME araco_gate2_evidence` and so on.
**`colcon build --symlink-install` symlinks the plain `PROGRAMS` installs but
copies the renamed ones.** Gate 0, Gate 1, and Gate 6 are symlinks and pick up
source edits immediately; Gates 2, 3, 4, and 5 are copies and keep running the
code from the last build.

This was found the hard way on 2026-08-22. The first rerun after `8865e3c` was
started without rebuilding. Gate 1 passed with the new classification while
Gates 2 and 3 failed on `launch_log_clean` and emitted no `upstream_defects`
block at all, because their installed copies still held the `9e0284b` runner.
Those two runs are preserved as `log/gate_2_20260822_staleinstall` and
`log/gate_3_20260822_staleinstall`. **They are not valid evidence for anything
except this finding.**

The earlier campaign is unaffected. The stale copies hashed identically to
`9e0284b`, which was the current runner throughout the 2026-08-18 and
2026-08-19 runs, so those results stand.

Rule: **after any edit to `scripts/araco_gate1_evidence`, run
`colcon build --packages-select araco_system_tests --symlink-install` before
running Gates 2-5.** Verify with a hash comparison, which takes a second and is
the only reliable check:

```bash
sha256sum src/araco_system_tests/scripts/araco_gate1_evidence \
  install/araco_system_tests/lib/araco_system_tests/araco_gate{1,2,3,4,5}_evidence
```

Worth fixing properly: the four `RENAME` installs could be replaced with
symlinks created at install time, which would remove the trap. Not done,
because it changes package install behavior and was out of scope for the run
that found it.

## The 2026-08-23 Gate 6 campaign — four attempts, no pass, one real finding

Four attempts were made. None produced three repetitions. The chronology is not
worth preserving; what follows is what it established.

| Run | Outcome |
| --- | --- |
| `gate_6_20260823_suitebudget` 11:42 | died at preflight gate 3, machine loaded |
| `gate_6_20260823_suitebudget_02` 19:57 | died at preflight gate 5, machine loaded |
| `gate_6_20260823_suitebudget_03` 22:05 | preflight all six PASS; repetition 1 complete in 313.2 s; repetition 2 died at gate 2 |
| `gate_6_20260823_prearmed` 23:09 | preflight all six PASS; repetition 1 died at gate 5 in 293.2 s |

### `suite_wall_budget` is decided and twice measured inside its limit

`planned_complete_suite_sim_s` was raised 100.0 to 145.0 on 2026-08-23, moving
the limit to 350.0 s. Two complete repetitions have since been measured at
**313.2 s and 293.2 s**, against `forcekill_01` repetitions of 298.3, 292.1 and
323.4 s. The number is sound. The check still needs three repetitions in one run
to be formally discharged.

### The blocker is an intermittent spurious `FAULT_HOLD`

The runtime reaches `HOLDING` at full readiness, then a joint-state or
controller-state sample arrives late, the supervisor latches `FAULT_HOLD`, and
`wait_for_holding` aborts the launch. Readiness typically recovers within
240-600 ms. **Nothing the robot does is wrong** — the gate that failed this way
on 2026-08-23 recorded a maximum leg error of 3.27e-07 rad and contact duty 1.0
on all six feet.

Measured over every retained launch log with supervisor telemetry, excluding
Gate 5 which injects faults deliberately:

| Window | Gate 1-4 launches | Reached `FAULT_HOLD` | Rate |
| --- | --- | --- | --- |
| All time | 96 | 9 | 9.4% |
| On/after 2026-08-22, post orphan isolation | 52 | 3 | 5.8% |

Seven of the nine have identified, since-fixed causes — five from the
2026-08-18 software-GL regression, one from orphan contamination, one from the
GL investigation itself. Reason codes seen: `18` `JOINT_STATE_STALE`, `20`
`CONTROLLER_NOT_READY`, `23` `TIME_DISCONTINUITY`, depending on which readiness
bits happen to lapse.

**At 5.8% per launch and about 21 launches per Gate 6 attempt, an attempt
survives only 29% of the time.** That, not any threshold, is why Gate 6 has not
passed.

### Measured cause: `/joint_states` can gap 335 ms against a 100 ms watchdog

Measured directly on 2026-08-23 with a monitor subscribed at matching
`SensorDataQoS` to every armed stream, against a manual `gazebo_ci_v0` launch of
55 s. The fault reproduced during the measurement.

| Stream | Samples | Median | p99 | Max | >100 ms |
| --- | --- | --- | --- | --- | --- |
| `/joint_states` | 6565 | 8.32 ms | 16.09 ms | **334.62 ms** | 1 |
| `/araco/locomotion/status` | 2000 | 29.59 ms | 30.96 ms | **339.21 ms** | 1 |
| `/leg_trajectory_controller/controller_state` | 12891 | 4.16 ms | 8.11 ms | 19.23 ms | 0 |
| `/gimbal_trajectory_controller/controller_state` | 12681 | 4.16 ms | 8.20 ms | 19.24 ms | 0 |

`/joint_states` runs an 8 ms median against a 100 ms watchdog — 12x margin — and
then misses one deadline by 3.3x. Locomotion status stalls in the same instant,
which is expected since it is derived from joint state. The controller *state
topics* did not stall at all, which is why the readiness bit pattern differs
between incidents.

**The frequency is not established: this is one stall in one launch.** Whether
stalls are rare and this one was unlucky, or concentrated near startup, is open.
The mismatch itself does not depend on knowing the rate.

The monitor is at
`/tmp/claude-1000/.../scratchpad/gap_monitor.py` and will not survive a reboot.
Rewriting it is 60 lines: subscribe at `qos_profile_sensor_data` to the four
streams above plus `/araco/safety/status`, record `time.monotonic()` deltas per
topic, print percentiles. Worth re-creating in `araco_system_tests` if this is
picked up again.

### Two hypotheses were tried and reverted — do not repeat them

Both were built on a log-mined correlation between faults and the
`/araco/command_arbiter` lifecycle bring-up window, and both were disproven:

1. **One `lifecycle_transition` process per node instead of one per transition.**
   Reduced the arbiter's two transitions from 1.3-2.3 s apart to 1.4 ms apart.
   The next run faulted anyway, 0.37 s *before* the first transition completed.
2. **Starting that process before the supervisor arms, waiting for `HOLDING`
   internally.** Cut arbiter bring-up to 32 ms after `HOLDING` with zero new DDS
   participants in the armed window. The next run faulted anyway, with nothing
   having started within 1.4 s of the fault.

The direct measurement then showed the stall is a *publication* problem inside
the simulator, not a delivery or discovery one — a delivery problem would have
hit the controller state topics arriving at 234 Hz over the same transport.
Both changes were reverted on 2026-08-23. They were harmless and arguably better
wiring, but they fixed nothing, and the clustering that suggested them is
incidental: the arbiter window is simply where the runtime is armed and idle.

**Method note worth keeping.** Log mining produced a confident false lead that
cost two 15-minute runs. Direct instrumentation settled it in one 70-second run.
When the question is "how big and how often", measure it; do not infer it from
correlations in logs that only record the failures and never the near-misses.

### Gate 6 is not a prerequisite for route 09

An earlier handoff recorded route 09 as "blocked on Gate 6". That was a policy,
not a technical dependency, and it went unchallenged for a full day of work.
Gate 6 certifies harness repeatability across gates 0-5; route 09 is a separate
operator trial with its own scorer and profile. The spurious `FAULT_HOLD` can
interrupt a route run — condition evaluation stays active in `MOTION_ENABLED` —
but at roughly 5.8% per launch that is a relaunch, not a blocker.


## Route 09, 2026-08-24 — PASSED, 12 of 12, on the fifth attempt

**`log/route09_pass/metrics.json` — `status: PASS`,
`completion_reason: route_complete_and_converged`, all twelve checks.** This
closes the SLAM-drift correction and unblocks saved-database relocalization and
Nav2.

| Result | Value |
| --- | --- |
| Route waypoints | 5 of 5 |
| Tracking lost | **0.0 s** |
| Loop closure | observed, node 160 |
| Translation closure error | **0.0259 m** |
| Yaw closure error | **0.0035 rad** |
| Convergence | 10.0 s, translation span 0.28 mm, yaw span 0.47 mrad |
| Map | 68 working-memory nodes, 83 704 cloud points |
| Wall duration | 265 s of the 300 s budget |

The 2.6 cm closure is the headline: raw visual odometry had been accumulating
roughly 8.2 cm over a controlled 58.6 cm translation, and loop closure corrected
it inside the acceptance bound. Ground-truth path length was 7.12 m.

The four failed attempts are archived as `log/route09_attempt{1,2,3}/` and are
worth keeping, because they localise the one real problem found along the way.

| | Attempt 1 | Attempt 2 | Attempt 3 |
| --- | --- | --- | --- |
| Checks passed | 3/12 | **10/12** | 7/12 |
| `ordered_route_complete` | FAIL (1 wp) | FAIL (0 wp) | **PASS (5 wp)** |
| Path driven | 1.84 m | 6.59 m | 7.67 m |
| Max distance from origin | — | ~0.6 m | 1.2 m |
| Tracking lost | 30.3 s | **0.0 s** | 110.6 s |
| Working-memory nodes | 6 | **44** | 11 |
| Loop closure | no | **yes** | no |
| Final yaw error | −2.02 rad | **0.007 rad** | 0.094 rad |

### The finding: the route cannot be driven with the heading locked to +X

In attempt 3 the correlation is exact.

```
waypoint 1 (+1.2, 0) reached   1787578020.52
odometry collapsed             1787578021.0     0.5 s later
```

Tracking never recovered — `tracking_recovery_events: 0` — so waypoints 2-5 were
driven blind. `rgbd_odometry` reported `Registration failed: Not enough inliers
0/15 (matches=10)` continuously from that moment. Quality by 30 s bucket was
91-106 with 99-100% healthy frames for the first two minutes, then 0.5 and 0.0.

The arena's features are `red_gate` at (1.65, 1.55), `yellow_pillars` at
(1.75, -1.60) and `floor_markers` at (0, 2.55), against a wall at x = 3.5. The
robot spawns at world (0, 0) with yaw -0.09 rad, so **body frame equals world
frame** and the waypoint coordinates are world coordinates. With the heading held
at +X the camera faces the wall throughout. From the origin the landmarks are in
peripheral view and tracking is perfect; from (+1.2, 0) they are beside and
behind the robot, and the camera sees blank wall 2.3 m away.

**Attempt 2 is the control.** It held heading, stayed inside ~0.6 m, lost zero
tracking, built 44 nodes and closed the loop — but never reached a waypoint.
Attempt 3 held heading, reached every waypoint, and lost tracking at the first
one. The acceptance protocol asks for both at once and this arena cannot supply
them.

This is a defect in the acceptance setup, not an operator error and not an Araco
defect. It was not visible before because no attempt had previously completed
the ordered route.

### Resolved: drive with body yaw following the direction of travel

**Option 1 was chosen and it works.** `final_yaw_returned` scores the final pose
only, so turning en route is permitted; the operator turns to face each leg,
keeping the landmarks in frame, then rotates back to +X at the origin before
holding still. Attempt 5 lost **zero** tracking across the whole route and
finished 0.0035 rad off the starting heading.

The evidence was unambiguous even before the scored run completed: in the
abandoned attempt 4, odometry past waypoint 1 held **100% healthy frames at mean
quality 99.3, peaking at 128**, where attempt 3 had been dead 0.5 s past that
same point.

**The protocol line "do not move the gimbal, hold the starting heading" is
therefore wrong for this arena and should be corrected** to "turn to face the
direction of travel, and return to +X at the origin". Holding the heading is
what made the route undrivable.

Rejected alternatives, kept so they are not retried:

1. *(chosen — see above)*
2. **Pan the gimbal instead.** **Not viable as configured.** The gimbal joint
   allows +/- 1.571 rad, but `body_envelope.gimbal_yaw_normal_rad` caps it at
   0.314 rad (18 deg) and the teleop mapping matches. From waypoint 1 the
   landmarks lie at +73.8 deg (`red_gate`), -71.0 deg (`yellow_pillars`) and
   +115.2 deg (`floor_markers`) — far outside 18 deg. Gimbal yaw also shares
   joystick axis 4 with posture yaw, so panning disturbs the body heading the
   protocol wants held. Pursuing this would mean widening a safety envelope
   fivefold to make an acceptance test pass, which is the wrong direction.
3. **Add features to the arena** in the +X region so the route is drivable as
   specified. Changes `rgbd_validation_v0` and invalidates comparison with
   earlier trials.
4. **Reduce the waypoint radius** below the range where the landmarks leave
   frame. Weakens the test — 0.6 m is proven to work, 1.2 m is proven not to.

Options 1 and 2 change the operator protocol only. Options 3 and 4 change scored
artifacts and need a `DECISIONS.md` entry.

### Also observed

- The 300 s wall budget was never the binding constraint. Attempt 3 completed
  the ordered route in 169 s; the remaining 131 s went to a convergence window
  that could not succeed with tracking dead.
- The perception profile launches its own RViz from the profile manifest
  (`presentation.rviz: true`). Starting one by hand as well produces two
  instances. Let the launch own it.

## Remaining risks

- ~~A complete route has not yet passed with the corrected estimator and
  scorer.~~ **Closed 2026-08-24: route 09 passed 12/12.**
- Visual odometry still accumulates roughly 8.2 cm translation error over a
  controlled 58.6 cm translation. **Loop closure was shown on 2026-08-24 to
  correct this to 2.6 cm over a 7.12 m route**, inside the acceptance bound, so
  the requirement is met — but the raw drift itself is unchanged and still
  matters for any path without closure opportunities.
- The camera IMU is not qualified for operational fusion until a timestamped
  transform/preprocessing path is implemented and retested. The physical
  Gemini driver, calibration, latency, and gimbal-angle feedback also remain
  unimplemented.
- Saved-database relocalization and Nav2 were blocked on a clean route pass.
  **That block is lifted.** The passing map is the database from the attempt 5
  run; preserve it out of `/tmp` before relying on it.
- The Gate 1-6 shutdown-defect classification added by `8865e3c` has now run
  live, across the 2026-08-22 campaign and the 2026-08-23 Gate 6 run. Real logs
  matched the intended signatures on all three variants of the defect, and
  `no_unclassified_error_or_fatal` passed over a whole Gate 6 log tree. The
  earlier note that it had never run live is withdrawn.
- `suite_wall_budget` is decided and **twice measured inside its limit**, at
  313.2 s and 293.2 s against 350.0 s. Three repetitions in a single run are
  still needed to discharge the check formally.
- **An intermittent spurious `FAULT_HOLD` blocks Gate 6 and can interrupt any
  run**, including route 09, since condition evaluation stays active in
  `MOTION_ENABLED`. Measured at 5.8% of gate 1-4 launches since 2026-08-22. The
  cause is measured — `/joint_states` can gap 335 ms against a 100 ms watchdog —
  but the *frequency* of the stall is not, being one observation. At 5.8% per
  launch this is a relaunch for an operator trial and a 71% chance of losing a
  21-launch Gate 6 attempt.
- **Machine load makes it worse but does not cause it.** Two of the four
  2026-08-23 attempts were lost with every sub-gate running 8-59% slower than
  the `forcekill_01` baseline; the other two ran on an idle machine and failed
  the same way. Still check the machine is idle before a long run, and treat a
  materially slower sub-gate as a starved run rather than a finding — but do not
  attribute the fault itself to load.
- Gate 6's orphan reaper can report a killed-but-unreaped server as `SURVIVED`,
  because `_process_alive()` uses `os.kill(pid, 0)`, which succeeds on a zombie.
  It overstates leakage rather than hiding it. One such record appears in
  `log/gate_6_20260822_forcekill_01`.
- The 2026-08-23 Gate 6 run was made from a dirty tree: `git_revision` records
  `37e1f12` with five modified files, so it reports
  `source_revision: unreported-dirty-or-installed-tree`. Those five files — the
  Gate 5 forced-kill fix, the 137 classification, its tests, and these two
  documents — are **uncommitted**; no commit was authorized by the request that
  made them. Fingerprints are unaffected — the run reproduced every recorded
  fingerprint across three repetitions, which is what
  `identical_behavior_fingerprints` checks.

## Exact next step

**Route 09 passed on 2026-08-24, twelve checks of twelve.** The acceptance trial
is done. `log/route09_pass/metrics.json` holds the result.

**The map is preserved.** RTAB-Map was stopped with SIGINT and finalised its
database cleanly — `Saving database/long-term memory...done! (78 MB)` — and the
file is copied to **`log/route09_pass/araco_rgbd_acceptance_09.db`** (79 MB).
`log/` is git-ignored, so that copy is durable on disk but not in the
repository. **A verified backup exists off the system disk** at
`/media/stevw-s14/DATA-ST/araco-shared/slam-maps/route09_pass_20260824/`
(external drive `DATA-ST`), with `metrics.json` and a `README.txt` recording
provenance. The copy was checked by SHA-256 against the source. **It is the input to
saved-database relocalization**, which this pass unblocked.

Scorer metrics for the pass and the three archived failures are committed under
`.agent/evidence/`, since they are small and are the proof of the milestone.
Note this departs from the usual convention of referencing `log/` paths without
committing them.

Then, in any order:

- **Saved-database relocalization**, using the preserved map.
- **Nav2**, also unblocked by the pass.
- **Gate 6**, still at 20 of 21 checks and still worth closing for
  repeatability, gated on the spurious-`FAULT_HOLD` decision recorded in
  `DECISIONS.md` on 2026-08-23.

### Correct the route 09 protocol before anyone repeats it

The written procedure said to hold the starting heading and keep the gimbal
centred. **Holding the heading makes the route undrivable in this arena** — the
camera faces a blank wall from the waypoints and odometry dies within a second
of arriving at the first one. The working procedure is:

> Turn to face the direction of travel on each leg, keeping the landmarks in
> frame. At the origin, rotate back to +X, align with the floor arrow, and hold
> still. `final_yaw_returned` scores only the final pose, so turning en route
> costs nothing.

Gimbal stays centred; that part of the protocol was right, and panning it is not
a workable alternative — see the route 09 section for why.

### Repeating the run

Prerequisite: the **LiteStar PXN-2113 Pro** gamepad connected. `joy_node` is
pinned to that exact `device_name` and `gazebo_perception_v0` has no keyboard
path. Check `ls /dev/input/js0` first.

A non-interactive shell does not read `~/.bashrc`, so tooling-started launches
must export the NVIDIA EGL selection or the cameras render on the CPU:

```bash
export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia
```

Terminal one — the profile launches its own RViz, so do not start a second:

```bash
ros2 launch araco_bringup gazebo.launch.py \
  profile:=gazebo_perception_v0 \
  database_path:=/tmp/araco_rgbd_acceptance_09.db
```

Terminal two, once `joystick_adapter completed activate` appears:

```bash
ros2 run araco_system_tests araco_slam_score \
  /tmp/araco_slam_acceptance_score_09
```

Use a **fresh database and score directory each attempt**; a stale database lets
RTAB-Map relocalize against the previous map and invalidates the result.

The robot spawns at world (0, 0) with yaw -0.09 deg, so **body frame equals
world frame** and the waypoints are world coordinates: (+1.2, 0), (0, +1.2),
(-1.2, 0), (0, -1.2), (0, 0), tolerance 0.35 m. The Gazebo Component Inspector
shows the `araco` pose live. Wall budget is 300 s; the passing run used 265 s.

Required order:

1. Done 2026-08-18. Both test failures fixed; `colcon build` clean and
   `colcon test` reports `424 tests, 0 errors, 0 failures, 26 skipped`,
   independently reproduced by Gate 6's package-test stage.
2. Done 2026-08-18. Gates 0-6 run into `log/`. Results, fingerprints, and the
   three defects are recorded above. Gates 0 and 3 pass. Gates 1 and 2 pass
   every scored check but fail teardown. Gates 4 and 6 fail; Gate 5 now fails
   only on Defect C.
3. Done 2026-08-19. Regression A was root-caused to software GL rendering and
   fixed by selecting the NVIDIA EGL vendor. Gate 4 scoring now passes all
   eight cases. Decide how to make those environment variables durable.
4. Done 2026-08-18. Regression B was root-caused to a lost execute bit on
   `araco_joint_state_relay` and fixed. Gate 5 now passes 28 of 29 scorer
   checks; its last failure is Defect C. The supervision-change hypothesis was
   disproved, not merely superseded.
5. Done 2026-08-20 as `8865e3c`. Defect C was handled by option 3: the
   upstream gz-sim teardown crash/hang is recorded as a named non-blocking
   condition in Gates 1-6 instead of failing `launch_exit` and
   `launch_log_clean`. It is not fixed and filing upstream remains open.
   See the Defect C section and the `DECISIONS.md` entry of the same date.
6. Done 2026-08-22 for Gates 0-5: all six PASS, every fingerprint reproduced,
   and the classification exercised live on all three variants of the defect.
   Three defects were found and fixed along the way — stale renamed installs,
   unlinted code in `8865e3c`, and a contaminated first attempt caused by
   orphaned servers. Gate 6 improved from one passing check to seven.
7. Done 2026-08-22/23. Gate 6's sub-gates were isolated by reaping plus
   explicit domains (`8463d3d`), and Gate 5's scored quiesce check was fixed by
   forcing the backend dead when the graceful stop hangs. Gate 6 now reaches
   twenty of twenty-one checks with three complete repetitions.
8. Done 2026-08-23. `suite_wall_budget` was decided: the planned simulated
   duration was raised to its measured 145.0 s, nothing else changed. Gate 3
   now reports `simulated_s` so the number stays auditable.
9. Done 2026-08-23 22:05, and it changed the problem. Preflight gates 0-5 all
   passed, repetition 1 passed all six sub-gates in 313.2 s inside the 350.0 s
   limit, and repetition 2 died at gate 2 on a spurious `FAULT_HOLD` with the
   robot behaving perfectly. `suite_wall_budget` is no longer the blocker; the
   intermittent warm-up fault is.
10. Done 2026-08-23 23:2x. The cause was **measured, not inferred**: the
   simulator stalls about 335 ms roughly once per launch, against a 0.1 s
   joint-state watchdog. Two launch changes made earlier that evening rest on a
   hypothesis this disproved; they are harmless but fix nothing.
11. Reverted 2026-08-23. Both launch changes were backed out — neither was
   proven and the measurement disproved the hypothesis behind them. The tree is
   clean apart from this document.
12. **Current step: run route 09.** Gate 6 is *not* a technical prerequisite,
   and the note that route 09 was "blocked on Gate 6" was a policy recorded in
   an earlier handoff, not a dependency. Gate 6 certifies harness
   repeatability; route 09 is a separate operator trial with its own scorer.
   Requires the **LiteStar PXN-2113 Pro** gamepad connected — `joy_node` is
   pinned to that `device_name` and `gazebo_perception_v0` has no keyboard
   path.
13. Deferred until a symptom motivates it: **sizing the simulation watchdogs**
   from the measured distribution — median 8 ms, p99 16 ms, worst 335 ms —
   keeping the physical contract at 0.1 s. If a route run is interrupted by a
   spurious `FAULT_HOLD`, that is the trigger. It is a safety-contract change
   needing a `DECISIONS.md` entry, and `maximum_detection_s` must move with the
   watchdogs or Gate 5's detection assertions will contradict them.
14. Deferred: rerun Gate 6 for three clean repetitions. At the 5.8% per-launch
   fault rate, 21 consecutive launches survive only 29% of the time, so this is
   not worth attempting until the watchdog question is settled. Gates 0-5 do not need
   rerunning unless their inputs change. Before any sequential run, and after
   it, check `pgrep -f '^gz sim'` and SIGKILL what it finds — and check `uptime`
   and `ps -eo pcpu,pid,args --sort=-pcpu | head`, because a gate suite starved
   of CPU fails in ways that look like Araco defects. This is how both the 11:48
   and the 19:57 attempts were lost on 2026-08-23. The run needs roughly 35
   minutes with nothing else competing for the machine — no browser start, no
   build, no second agent. A non-interactive shell does not read `~/.bashrc`, so
   export `__EGL_VENDOR_LIBRARY_FILENAMES`, `__NV_PRIME_RENDER_OFFLOAD` and
   `__GLX_VENDOR_LIBRARY_NAME` explicitly or gates render on the CPU.
15. Route 09 acceptance closes the SLAM correction.

Reproduction for Defect C, which does not need the gate harness:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch araco_bringup gazebo.launch.py profile:=gazebo_ci_v0
```

Once holding, send the orderly shutdown and then the server stop. With the
shutdown first, the server never exits; without it, the server exits in under
a second.

```bash
ros2 action send_goal /araco/safety/transition \
  araco_interfaces/action/SafetyTransition "{request: 4}"
gz service -s /server_control --reqtype gz.msgs.ServerControl \
  --reptype gz.msgs.Boolean --timeout 3000 --req 'stop: true'
```

Route 09 procedure, once the gates above pass:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch araco_bringup gazebo.launch.py \
  profile:=gazebo_perception_v0 \
  database_path:=/tmp/araco_rgbd_acceptance_09.db
```

In a second terminal:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run araco_system_tests araco_slam_score \
  /tmp/araco_slam_acceptance_score_09
```

Drive east/red, north/blue, west/green, south/yellow, then origin/white. At the
origin, align with the +X floor arrow and keep the robot stationary until the
scorer reports convergence. Do not move the gimbal during this first acceptance
route, even though the isolated visual-only gimbal trial was clean.
