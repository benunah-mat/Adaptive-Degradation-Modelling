import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rms_health_indicator import rms_health_indicator

DATA_DIR = PROJECT_ROOT / "data" / "PRONOSTIA"
LEARNING_DIR = DATA_DIR / "Learning_set"
TEST_DIR = DATA_DIR / "Test_set"
OUTPUT_DIR = SCRIPT_DIR


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RMS_HEALTHY_BASELINE_SNAPSHOTS = 100
RMS_FAILURE_THRESHOLD = 2.0  # g

FITTING_BEARINGS = [
    "Bearing1_1", "Bearing1_2",
    "Bearing2_1", "Bearing2_2",
    "Bearing3_2",
]

EXCLUDED_BEARINGS = {
    "Bearing3_1": "premature step-failure with insufficient degradation precursor",
    "Bearing2_3": "early-life vibration spike with no subsequent typical degradation",
    "Bearing2_4": "flat throughout — likely truncated very early in life",
}

PREDICTION_BEARINGS = [
    name for name in [
        "Bearing1_3", "Bearing1_4", "Bearing1_5", "Bearing1_6", "Bearing1_7",
        "Bearing2_5", "Bearing2_6", "Bearing2_7",
        "Bearing3_3",
    ]
    if name not in EXCLUDED_BEARINGS
]

OPERATING_CONDITIONS = {
    1: {"speed_rpm": 1800, "load_N": 4000},
    2: {"speed_rpm": 1650, "load_N": 4200},
    3: {"speed_rpm": 1500, "load_N": 5000},
}

ALL_BEARINGS = {
    "Bearing1_1": {"condition": 1, "set": "learning"},
    "Bearing1_2": {"condition": 1, "set": "learning"},
    "Bearing1_3": {"condition": 1, "set": "test"},
    "Bearing1_4": {"condition": 1, "set": "test"},
    "Bearing1_5": {"condition": 1, "set": "test"},
    "Bearing1_6": {"condition": 1, "set": "test"},
    "Bearing1_7": {"condition": 1, "set": "test"},
    "Bearing2_1": {"condition": 2, "set": "learning"},
    "Bearing2_2": {"condition": 2, "set": "learning"},
    "Bearing2_3": {"condition": 2, "set": "test"},
    "Bearing2_4": {"condition": 2, "set": "test"},
    "Bearing2_5": {"condition": 2, "set": "test"},
    "Bearing2_6": {"condition": 2, "set": "test"},
    "Bearing2_7": {"condition": 2, "set": "test"},
    "Bearing3_1": {"condition": 3, "set": "learning"},
    "Bearing3_2": {"condition": 3, "set": "learning"},
    "Bearing3_3": {"condition": 3, "set": "test"},
}

PUBLISHED_REMAINING_LIFE = {
    "Bearing1_3": 573,
    "Bearing1_4": 34,
    "Bearing1_5": 161,
    "Bearing1_6": 146,
    "Bearing1_7": 757,
    "Bearing2_3": 753,
    "Bearing2_4": 139,
    "Bearing2_5": 309,
    "Bearing2_6": 129,
    "Bearing2_7": 58,
    "Bearing3_3": 82,
}

N_MC_RUNS = 500
MAX_SIM_LENGTH = 10000
DAMAGE_SMOOTH_WINDOW = 50


# ---------------------------------------------------------------------------
# Function definitions
# ---------------------------------------------------------------------------

def compute_rms_for_file(filepath):
    df = pd.read_csv(
        filepath,
        header=None,
        names=["hour", "minute", "second", "microsec", "h_accel", "v_accel"],
    )
    accel_magnitude = np.sqrt(df["h_accel"] ** 2 + df["v_accel"] ** 2).values
    rms_segments = rms_health_indicator(accel_magnitude)
    return float(np.mean(rms_segments))


def load_bearing_trajectory(bearing_dir):
    acc_files = sorted(bearing_dir.glob("acc_*.csv"))
    print(f"  {bearing_dir.name}: processing {len(acc_files)} files...")
    rms_trajectory = []
    for f in acc_files:
        rms_trajectory.append(compute_rms_for_file(f))
    return np.array(rms_trajectory)


def normalize_to_damage(rms_trajectory, baseline_window=RMS_HEALTHY_BASELINE_SNAPSHOTS,
                        failure_threshold=RMS_FAILURE_THRESHOLD):
    n = min(baseline_window, len(rms_trajectory))
    baseline_rms = float(np.median(rms_trajectory[:n]))
    damage = (rms_trajectory - baseline_rms) / (failure_threshold - baseline_rms)
    damage = np.clip(damage, 0.0, 1.0)
    return damage, baseline_rms


def damage_evolution_deterministic(t_array, load_N, speed_rpm, k, a, c, beta,
                                   D0=1e-4, dt=1.0):
    """
    Deterministic damage evolution — power-law form.
    dD/dt = k * L^a * S^c * D^beta
    """
    n = len(t_array)
    D = np.zeros(n)
    D[0] = D0
    base_rate = k * (load_N ** a) * (speed_rpm ** c)
    for i in range(1, n):
        growth = base_rate * (D[i - 1] ** beta)
        D[i] = D[i - 1] + growth * dt
        if D[i] >= 1.0:
            D[i:] = 1.0
            break
        if D[i] < D0:
            D[i] = D0
    return D


def smooth_damage(damage, window=DAMAGE_SMOOTH_WINDOW):
    series = pd.Series(damage)
    return series.rolling(window=window, center=True, min_periods=1).mean().values


def fit_residuals(params, fitting_data):
    k, a, c, beta = params
    all_residuals = []
    for entry in fitting_data:
        n = len(entry["damage_smooth"])
        t_array = np.arange(n)
        predicted = damage_evolution_deterministic(
            t_array=t_array,
            load_N=entry["load_N"],
            speed_rpm=entry["speed_rpm"],
            k=k, a=a, c=c, beta=beta,
        )
        residuals = predicted - entry["damage_smooth"]
        all_residuals.append(residuals)
    return np.concatenate(all_residuals)


def estimate_sigma(fitting_data, k, a, c, beta):
    """
    Estimate the bearing-to-bearing rate variability σ as the standard
    deviation of log-rate ratios across fitting bearings.
    """
    log_rate_ratios = []
    for entry in fitting_data:
        damage = entry["damage_smooth"]
        actual_cycles = float(len(damage))

        long_t_array = np.arange(int(actual_cycles * 5))
        det_traj = damage_evolution_deterministic(
            t_array=long_t_array,
            load_N=entry["load_N"],
            speed_rpm=entry["speed_rpm"],
            k=k, a=a, c=c, beta=beta,
        )
        det_failure_idx = np.where(det_traj >= 1.0)[0]
        if len(det_failure_idx) == 0:
            continue
        det_cycles = float(det_failure_idx[0])

        log_rate_ratios.append(np.log(actual_cycles / det_cycles))

    if len(log_rate_ratios) == 0:
        return 0.1
    return float(np.std(log_rate_ratios))


def damage_evolution_stochastic(t_array, load_N, speed_rpm, k, a, c, beta, sigma,
                                D0=1e-4, dt=1.0, rng=None):
    """
    Stochastic damage evolution with bearing-specific random rate constant.

    Each call samples K_i ~ LogNormal(ln k, sigma), representing the
    individual bearing's manufacturing variability. Then:

        dD/dt = K_i * L^a * S^c * D^beta

    runs deterministically for that bearing.
    """
    if rng is None:
        rng = np.random.default_rng()

    K_i = float(np.exp(np.log(k) + sigma * rng.standard_normal()))

    n = len(t_array)
    D = np.zeros(n)
    D[0] = D0
    base_rate = K_i * (load_N ** a) * (speed_rpm ** c)
    for i in range(1, n):
        growth = base_rate * (D[i - 1] ** beta)
        D[i] = D[i - 1] + growth * dt
        if D[i] >= 1.0:
            D[i:] = 1.0
            return D, i
        if D[i] < D0:
            D[i] = D0
    return D, None


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

print("=" * 60)
print("PHASE 1: PRONOSTIA validation pipeline")
print("=" * 60)

print("\nDIAGNOSTIC — folder check:")
print(f"  Learning_set exists: {LEARNING_DIR.exists()}")
print(f"  Test_set exists:     {TEST_DIR.exists()}")

print(f"\nValidation scope:")
print(f"  Fitting:     {len(FITTING_BEARINGS)} bearings — {FITTING_BEARINGS}")
print(f"  Prediction:  {len(PREDICTION_BEARINGS)} bearings — {PREDICTION_BEARINGS}")
print(f"  Excluded:    {len(EXCLUDED_BEARINGS)} bearings:")
for name, reason in EXCLUDED_BEARINGS.items():
    print(f"    {name}: {reason}")

print("\n" + "-" * 60)
print("Loading all 17 bearings (5–10 minutes)")
print("-" * 60)

bearing_data = {}
for bearing_name, info in ALL_BEARINGS.items():
    set_dir = LEARNING_DIR if info["set"] == "learning" else TEST_DIR
    bearing_path = set_dir / bearing_name
    if not bearing_path.exists():
        print(f"  WARNING: {bearing_path} not found — skipping")
        continue
    trajectory = load_bearing_trajectory(bearing_path)
    cond = OPERATING_CONDITIONS[info["condition"]]
    bearing_data[bearing_name] = {
        "trajectory": trajectory,
        "condition_id": info["condition"],
        "speed_rpm": cond["speed_rpm"],
        "load_N": cond["load_N"],
        "set": info["set"],
        "n_snapshots": len(trajectory),
        "lifespan_seconds": len(trajectory) * 10,
    }

print(f"\nLoaded {len(bearing_data)} bearings")

# Plot raw RMS trajectories grouped by condition
fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=False)
for ax, condition_id in zip(axes, [1, 2, 3]):
    bearings_in_cond = [
        (name, info) for name, info in bearing_data.items()
        if info["condition_id"] == condition_id
    ]
    cond_info = OPERATING_CONDITIONS[condition_id]
    for name, info in bearings_in_cond:
        linestyle = "-" if info["set"] == "learning" else "--"
        ax.plot(info["trajectory"], linestyle, label=f"{name} ({info['set']})",
                alpha=0.7, linewidth=1)
    ax.set_title(f"Condition {condition_id}: {cond_info['speed_rpm']} rpm, "
                 f"{cond_info['load_N']} N — {len(bearings_in_cond)} bearings",
                 fontsize=11)
    ax.set_ylabel("RMS vibration (g)")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
axes[-1].set_xlabel("Snapshot index (10 s each)")
plt.suptitle("PRONOSTIA: All 17 Bearing Run-to-Failure Trajectories", fontsize=13, y=1.00)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "all_bearings_trajectories.png", dpi=150)
plt.close()
print(f"Raw trajectories chart saved to {OUTPUT_DIR / 'all_bearings_trajectories.png'}")

# Normalize all bearings to damage D ∈ [0, 1]
print("\n" + "-" * 60)
print("Normalizing trajectories to damage D ∈ [0, 1]")
print("-" * 60)

for name, info in bearing_data.items():
    damage, baseline = normalize_to_damage(info["trajectory"])
    info["damage"] = damage
    info["baseline_rms"] = baseline
    failure_indices = np.where(damage >= 1.0)[0]
    info["failure_snapshot"] = int(failure_indices[0]) if len(failure_indices) > 0 else None

print(f"\n{'Bearing':<14} {'Cond':>4} {'Baseline RMS':>13} {'Reached D=1':>12} {'Failed at':>11}")
for name in sorted(bearing_data.keys()):
    info = bearing_data[name]
    fail_status = "yes" if info["failure_snapshot"] is not None else "no"
    fail_at = f"snap {info['failure_snapshot']}" if info["failure_snapshot"] is not None else "—"
    print(f"{name:<14} {info['condition_id']:>4} "
          f"{info['baseline_rms']:>13.3f} {fail_status:>12} {fail_at:>11}")

# Plot normalized damage trajectories
fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=False)
for ax, condition_id in zip(axes, [1, 2, 3]):
    bearings_in_cond = [
        (name, info) for name, info in bearing_data.items()
        if info["condition_id"] == condition_id
        and name not in EXCLUDED_BEARINGS
    ]
    cond_info = OPERATING_CONDITIONS[condition_id]
    for name, info in bearings_in_cond:
        in_fitting = name in FITTING_BEARINGS
        linestyle = "-" if in_fitting else "--"
        linewidth = 2.0 if in_fitting else 1.0
        label_set = "fit" if in_fitting else "predict"
        ax.plot(info["damage"], linestyle, label=f"{name} ({label_set})",
                alpha=0.8, linewidth=linewidth)
    ax.axhline(1.0, color="red", linestyle=":", linewidth=1, label="D = 1 (failure)")
    ax.set_title(f"Condition {condition_id}: {cond_info['speed_rpm']} rpm, "
                 f"{cond_info['load_N']} N", fontsize=11)
    ax.set_ylabel("Damage D")
    ax.set_ylim(-0.05, 1.1)
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
axes[-1].set_xlabel("Snapshot index (10 s each)")
plt.suptitle("Normalized Damage Trajectories — Validation Scope",
             fontsize=13, y=1.00)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "normalized_damage_trajectories.png", dpi=150)
plt.close()
print(f"\nNormalized trajectories chart saved to "
      f"{OUTPUT_DIR / 'normalized_damage_trajectories.png'}")


# ---------------------------------------------------------------------------
# PHASE 2: Fit the damage evolution model (power-law form)
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("PHASE 2: Fitting damage evolution model — power-law form")
print("=" * 60)

from scipy.optimize import least_squares

fitting_data = []
for name in FITTING_BEARINGS:
    info = bearing_data[name]
    fitting_data.append({
        "name": name,
        "load_N": info["load_N"],
        "speed_rpm": info["speed_rpm"],
        "damage_smooth": smooth_damage(info["damage"]),
    })

initial_guess = [1e-6, 1.0, 1.0, 2.0]
lower_bounds = [1e-15, 0.1, 0.1, 0.5]
upper_bounds = [1e-1,  6.0, 6.0, 5.0]

print(f"\nInitial guess:    k={initial_guess[0]:.2e}, a={initial_guess[1]:.2f}, "
      f"c={initial_guess[2]:.2f}, β={initial_guess[3]:.2f}")
print(f"Fitting on {len(fitting_data)} bearings, "
      f"{sum(len(e['damage_smooth']) for e in fitting_data)} total snapshots")
print("\nRunning least-squares optimization...")

result = least_squares(
    fit_residuals,
    x0=initial_guess,
    bounds=(lower_bounds, upper_bounds),
    args=(fitting_data,),
    method="trf",
    verbose=1,
)

k_fit, a_fit, c_fit, beta_fit = result.x

print("\n--- Fitted parameters ---")
print(f"  k     = {k_fit:.6e}")
print(f"  a     = {a_fit:.4f}    (load exponent)")
print(f"  c     = {c_fit:.4f}    (speed exponent)")
print(f"  β     = {beta_fit:.4f}    (damage-growth power)")
print(f"\nFinal residual cost: {result.cost:.4e}")
print(f"Optimization success: {result.success}")
print(f"Termination message: {result.message}")

# Plot fitted vs measured damage
fig, axes = plt.subplots(len(FITTING_BEARINGS), 1, figsize=(12, 3 * len(FITTING_BEARINGS)),
                        sharex=False)

for ax, name in zip(axes, FITTING_BEARINGS):
    info = bearing_data[name]
    n = info["n_snapshots"]
    t_array = np.arange(n)
    predicted = damage_evolution_deterministic(
        t_array=t_array,
        load_N=info["load_N"],
        speed_rpm=info["speed_rpm"],
        k=k_fit, a=a_fit, c=c_fit, beta=beta_fit,
    )
    measured_smooth = smooth_damage(info["damage"])
    rmse = float(np.sqrt(np.mean((predicted - measured_smooth) ** 2)))

    ax.plot(t_array, info["damage"], color="lightgray", linewidth=0.8,
            label="Measured (raw)")
    ax.plot(t_array, measured_smooth, color="navy", linewidth=1.5,
            label="Measured (smoothed)")
    ax.plot(t_array, predicted, color="crimson", linewidth=2,
            label="Model prediction")
    ax.axhline(1.0, color="black", linestyle=":", linewidth=0.8)
    ax.set_title(f"{name}  (Cond {info['condition_id']}: "
                 f"{info['speed_rpm']} rpm, {info['load_N']} N)  —  "
                 f"trajectory RMSE = {rmse:.3f}", fontsize=10)
    ax.set_ylabel("Damage D")
    ax.set_ylim(-0.05, 1.1)
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

axes[-1].set_xlabel("Snapshot index (10 s each)")
plt.suptitle(f"Fitted Damage Model (Power-Law) vs Measured — Training Bearings\n"
             f"k={k_fit:.2e}, a={a_fit:.2f}, c={c_fit:.2f}, β={beta_fit:.2f}",
             fontsize=12, y=1.00)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "fit_vs_measured_training.png", dpi=150)
plt.close()
print(f"\nFit-vs-measured chart saved to {OUTPUT_DIR / 'fit_vs_measured_training.png'}")


# ---------------------------------------------------------------------------
# PHASE 3: Stochastic Monte Carlo failure-time validation
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("PHASE 3: Stochastic Monte Carlo failure-time validation")
print("=" * 60)

sigma_fit = estimate_sigma(fitting_data, k_fit, a_fit, c_fit, beta_fit)
print(f"\nEstimated relative noise scale (log-normal σ): {sigma_fit:.4f}")
print(f"\nRunning {N_MC_RUNS} Monte Carlo simulations per condition...")

mc_results = {}
rng = np.random.default_rng(seed=42)

for condition_id, cond in OPERATING_CONDITIONS.items():
    failure_cycles = []
    survived = 0
    for _ in range(N_MC_RUNS):
        t_array = np.arange(MAX_SIM_LENGTH)
        _, failure = damage_evolution_stochastic(
            t_array=t_array,
            load_N=cond["load_N"],
            speed_rpm=cond["speed_rpm"],
            k=k_fit, a=a_fit, c=c_fit, beta=beta_fit, sigma=sigma_fit,
            rng=rng,
        )
        if failure is not None:
            failure_cycles.append(failure)
        else:
            survived += 1

    failure_cycles = np.array(failure_cycles)
    mc_results[condition_id] = {
        "failure_cycles": failure_cycles,
        "n_failed": len(failure_cycles),
        "n_survived": survived,
        "mean": float(np.mean(failure_cycles)) if len(failure_cycles) > 0 else None,
        "median": float(np.median(failure_cycles)) if len(failure_cycles) > 0 else None,
        "p2_5": float(np.percentile(failure_cycles, 2.5)) if len(failure_cycles) > 0 else None,
        "p97_5": float(np.percentile(failure_cycles, 97.5)) if len(failure_cycles) > 0 else None,
    }

    print(f"  Condition {condition_id} ({cond['speed_rpm']} rpm, {cond['load_N']} N): "
          f"{len(failure_cycles)}/{N_MC_RUNS} simulated bearings failed within "
          f"{MAX_SIM_LENGTH} cycles")
    if len(failure_cycles) > 0:
        print(f"    Predicted failure cycle: median={mc_results[condition_id]['median']:.0f}, "
              f"95% CI=[{mc_results[condition_id]['p2_5']:.0f}, "
              f"{mc_results[condition_id]['p97_5']:.0f}]")

# Build empirical failure cycles list per condition
empirical_failures = {1: [], 2: [], 3: []}

for name, info in bearing_data.items():
    if name in EXCLUDED_BEARINGS:
        continue
    cond = info["condition_id"]
    if info["failure_snapshot"] is not None:
        empirical_failures[cond].append({
            "name": name,
            "failure_cycle": info["failure_snapshot"],
            "source": "observed",
        })
    elif name in PUBLISHED_REMAINING_LIFE:
        total_failure = info["n_snapshots"] + PUBLISHED_REMAINING_LIFE[name]
        empirical_failures[cond].append({
            "name": name,
            "failure_cycle": total_failure,
            "source": "published",
        })

print(f"\n--- Coverage analysis ---")
print(f"{'Cond':>4} {'Bearing':<14} {'Source':>10} {'Actual':>8} {'Predicted CI':>20} "
      f"{'In CI?':>6}")

total_in_ci = 0
total_count = 0
for cond_id in [1, 2, 3]:
    mc = mc_results[cond_id]
    if mc["p2_5"] is None:
        continue
    for empirical in empirical_failures[cond_id]:
        actual = empirical["failure_cycle"]
        in_ci = mc["p2_5"] <= actual <= mc["p97_5"]
        total_in_ci += int(in_ci)
        total_count += 1
        ci_str = f"[{mc['p2_5']:.0f}, {mc['p97_5']:.0f}]"
        in_ci_mark = "yes" if in_ci else "NO"
        print(f"{cond_id:>4} {empirical['name']:<14} {empirical['source']:>10} "
              f"{actual:>8} {ci_str:>20} {in_ci_mark:>6}")

coverage = (total_in_ci / total_count) * 100 if total_count > 0 else 0
print(f"\n95% CI coverage: {total_in_ci}/{total_count} bearings = {coverage:.1f}%")
print(f"(For a well-calibrated model, this should be close to 95%)")

# Plot Monte Carlo distributions with empirical failures overlaid
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=False)

for ax, cond_id in zip(axes, [1, 2, 3]):
    mc = mc_results[cond_id]
    cond = OPERATING_CONDITIONS[cond_id]

    if mc["p2_5"] is None:
        ax.set_title(f"Condition {cond_id}: no Monte Carlo failures within "
                     f"{MAX_SIM_LENGTH} cycles", fontsize=11)
        continue

    ax.hist(mc["failure_cycles"], bins=40, density=True, color="steelblue",
            alpha=0.6, edgecolor="white",
            label=f"Stochastic model ({len(mc['failure_cycles'])} runs)")

    ax.axvline(mc["p2_5"], color="navy", linestyle="--", linewidth=1.5,
               label=f"95% CI: [{mc['p2_5']:.0f}, {mc['p97_5']:.0f}]")
    ax.axvline(mc["p97_5"], color="navy", linestyle="--", linewidth=1.5)
    ax.axvline(mc["median"], color="navy", linestyle="-", linewidth=2,
               label=f"Median: {mc['median']:.0f}")

    for empirical in empirical_failures[cond_id]:
        marker = "o" if empirical["source"] == "observed" else "^"
        in_ci = mc["p2_5"] <= empirical["failure_cycle"] <= mc["p97_5"]
        color = "green" if in_ci else "red"
        ax.scatter(empirical["failure_cycle"], 0,
                   marker=marker, s=120, color=color, edgecolor="black",
                   zorder=5, clip_on=False)
        ax.annotate(empirical["name"], xy=(empirical["failure_cycle"], 0),
                    xytext=(0, 25), textcoords="offset points",
                    ha="center", fontsize=7, rotation=45)

    ax.set_title(f"Condition {cond_id}: {cond['speed_rpm']} rpm, {cond['load_N']} N — "
                 f"Predicted vs observed failure times", fontsize=10)
    ax.set_ylabel("Probability density")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)

axes[-1].set_xlabel("Failure cycle (snapshot index, 10 s each)")
plt.suptitle(f"Stochastic Monte Carlo Validation — Coverage = {coverage:.1f}%",
             fontsize=13, y=1.00)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "monte_carlo_validation.png", dpi=150)
plt.close()

print(f"\nMonte Carlo validation chart saved to "
      f"{OUTPUT_DIR / 'monte_carlo_validation.png'}")


print("\n" + "=" * 60)
print("Phases 1–3 complete.")
print("=" * 60)