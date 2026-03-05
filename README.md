# Adaptive Bearing Degradation and Failure Prediction Framework

## Overview

This project develops a vibration-based prognostics framework for detecting degradation and predicting failure in rolling element bearings using the NASA IMS bearing dataset.

The goal is to transform raw vibration measurements into actionable reliability insights by identifying degradation regimes and estimating the Remaining Useful Life (RUL) of the system.

The model combines signal processing, degradation modelling, and statistical change detection to build a complete predictive maintenance pipeline.

---

# Project Objectives

* Extract a meaningful health indicator from raw vibration signals.
* Model degradation dynamics in rotating machinery.
* Detect statistical instability in degradation behaviour.
* Identify degradation regimes automatically.
* Predict failure time and estimate Remaining Useful Life (RUL).

---

# Dataset

This project uses the **NASA IMS Bearing Dataset**, which contains vibration measurements collected from a bearing test rig until failure.

The dataset includes thousands of vibration signals recorded over time, allowing analysis of degradation behaviour leading up to bearing failure.

Each vibration file represents accelerometer data collected from the test rig at a specific time interval.

---

# Methodology

The model follows a multi-stage predictive maintenance pipeline:

```
Raw vibration signals
↓
Health indicator extraction (RMS)
↓
Log degradation modelling
↓
Degradation velocity estimation
↓
Residual dynamics analysis
↓
Sequential change detection (CUSUM)
↓
Regime identification
↓
Accelerated degradation modelling
↓
Failure prediction
↓
Remaining Useful Life estimation
```

---

# Phase 1: Deterministic Degradation Modelling

The vibration signals are transformed into a degradation indicator using Root Mean Square (RMS) vibration energy.

The RMS signal captures the increasing vibration energy associated with bearing damage.

Key concept:

RMS measures vibration energy and acts as a proxy for damage accumulation in rotating machinery.

---

# Phase 2: Adaptive Exponential Degradation Modelling

Bearing degradation often follows exponential growth behaviour.
To linearise this behaviour, the degradation signal is transformed using a logarithmic model:

g(t) = log(D(t))

This allows the degradation dynamics to be analysed using velocity-based modelling.

The degradation velocity is estimated as the difference between successive log degradation states.

---

# Phase 3: Statistical Instability Detection (CUSUM)

Sequential hypothesis testing is used to detect changes in degradation behaviour.

The Cumulative Sum (CUSUM) algorithm monitors residual dynamics to detect deviations from expected degradation behaviour.

CUSUM statistic:

S_t = max(0, S_(t-1) + ε_t − k)

When the statistic exceeds a threshold, a degradation regime transition is detected.

This allows the model to identify when the system transitions from healthy behaviour to degradation.

---

# Phase 4: Regime-Aware Failure Prediction

Once the accelerated degradation regime is identified, a quadratic degradation model is fitted to the late-stage degradation region.

The model predicts the failure time by solving:

g(t) = a + bt + ct²

The predicted failure time is used to estimate Remaining Useful Life:

RUL = predicted failure time − current time

---

# Results

Using the NASA IMS bearing dataset:

* Early degradation detection occurred at sample ~156
* True failure occurred at sample 2156
* Predicted failure occurred at sample ~2245
* Prediction error ≈ 89 samples (~4%)

This demonstrates that the model can detect degradation early and predict failure with reasonable accuracy.

---

# Key Concepts Used

This project integrates principles from several fields:

**Vibration Mechanics**

* Bearing fault dynamics
* Impact-induced vibration energy

**Signal Processing**

* RMS energy extraction
* Log transformation

**Reliability Engineering**

* Degradation modelling
* Remaining Useful Life prediction

**Statistical Process Monitoring**

* Sequential hypothesis testing
* CUSUM change detection

---

# Tools and Technologies

* MATLAB
* Signal Processing
* Time Series Analysis
* Statistical Change Detection
* Degradation Modelling

---

# Applications

This framework is relevant to predictive maintenance in industries such as:

* Oil and Gas
* Aerospace
* Manufacturing
* Energy and Power Systems
* Wind Turbines

Predictive maintenance systems built on similar principles are used to monitor rotating machinery and prevent unexpected equipment failures.

---

# Future Improvements

Potential extensions of this work include:

* Testing across multiple bearings in the dataset
* Uncertainty-aware RUL prediction
* Monte Carlo degradation modelling
* Multi-sensor fusion
* Real-time online prediction

---

# Author
Benjamin Unah

