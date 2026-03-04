# Adaptive Degradation Modelling

## Overview

This repository documents the progressive development of an adaptive statistical framework for modelling and detecting degradation in rolling element bearings using the NASA IMS dataset.

The project evolved through multiple modelling paradigms:

1. Deterministic degradation modelling (DHDE)
2. Adaptive local exponential growth modelling
3. Statistical instability detection (in progress)

Rather than presenting a single final model, this repository captures the research trajectory — including structural validation, model limitations, and refinement.

---

## Research Motivation

Traditional vibration-based prognostics often rely on:

- RMS thresholding
- Global curve fitting
- Deterministic degradation laws

However, bearing degradation typically exhibits:

- Long stationary phases
- Rapid late-stage acceleration
- Non-global model consistency

This project investigates whether degradation should be modelled as:

- A deterministic health-state process (Phase 1)
- A locally exponential acceleration process (Phase 2)
- A statistically detectable instability transition (Phase 3)

---

# Phase 1 — Deterministic DHDE Model

### Assumption
Degradation follows a power-law dynamic:

dH/dt = -α V^m

Where:
- H(t) is normalized health
- V(t) is RMS vibration
- α, m are model parameters

### Method
- Health-state transformation
- Log–log regression for parameter estimation
- Structural validation using R²

### Findings
- Low structural R² on IMS data
- Global power-law assumption not strongly supported
- Early RUL prediction unstable

This phase established modelling limitations.

---

# Phase 2 — Adaptive Exponential Growth Model

### Assumption
Late-stage degradation follows local exponential growth:

V(t) = A exp(λ t)

### Method
- Log-linear sliding window regression
- Adaptive estimation of growth rate λ(t)
- Short-horizon analytical failure projection

### Key Insight
Degradation is better represented as a *locally exponential acceleration process*, rather than a globally deterministic law.

Short-horizon predictions converge near failure.

---

# Phase 3 — Statistical Instability Detection (In Progress)

Instead of predicting failure time directly, we investigate:

When does the system transition from stationary stochastic behaviour to structured exponential growth?

We define:

λ(t) = d/dt log V(t)

Under healthy conditions:
λ(t) ~ N(0, σ²)

Under degradation:
λ(t) ~ N(μ, σ²), μ > 0

We implement sequential change detection (CUSUM) to detect statistically significant mean shifts in λ.

Goal:
Detect degradation instability earlier than RMS threshold crossing.

---

# Dataset

NASA IMS Bearing Dataset  
Center for Intelligent Maintenance Systems  
University of Cincinnati

---

# Repository Structure

/Phase1_DHDE_Model  
/Phase2_Adaptive_Exponential_Model  
/Phase3_Statistical_Instability_Detection (in development)  

---

# Current Status

- Phase 1 complete
- Phase 2 complete
- Phase 3 under development

Future work includes:

- False-alarm control analysis
- Multi-bearing validation
- Detection lead-time benchmarking
- Confidence interval estimation

---

# Research Direction

This work is evolving toward a statistically rigorous early-instability detection framework for rotating machinery, grounded in change-detection theory rather than threshold heuristics.

---

Author: Benjamin Unah  
