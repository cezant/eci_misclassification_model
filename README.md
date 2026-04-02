# eci_misclassification_model
Simulation of occupational misclassification bias in the Employment Cost Index (ECI) using BLS OEWS data, validation against official wage growth estimates.

# 📊 ECI Misclassification Impact Model (OEWS + Simulation)

## 🔍 Overview

This project estimates how occupational misclassification can bias the **Employment Cost Index (ECI)** using publicly available data from the U.S. Bureau of Labor Statistics (BLS).

The model simulates classification errors in occupational wage data and evaluates how those errors propagate into distortions in aggregate wage measures.

---

## 🎯 Research Question

> How much of observed wage growth in the Employment Cost Index (ECI) could be explained by occupational misclassification?

---

## 📦 Data Sources

* **OEWS (Occupational Employment and Wage Statistics)**

  * National occupational employment and wage estimates
  * Provides employment counts and mean wages by SOC occupation

* **ECI (Employment Cost Index)**

  * Official BLS wage growth measure
  * Used as a benchmark for validation

---

## 🧠 Methodology

### 1. Construct Wage Index (ECI-style)

A weighted wage index is built using OEWS data:

Weighted Wage = (Employment × Average Wage)

Index = Total Weighted Wage / Total Employment

---

### 2. Misclassification Simulation

Two approaches were implemented:

#### 🔹 Random Misclassification (Baseline)

* Any occupation can be misclassified as any other
* Produces upper-bound estimates of distortion

#### 🔹 Structured Misclassification (Improved Model)

* Misclassification restricted within SOC major groups
* Reflects realistic survey coding errors
* Reduces extreme and implausible outcomes

---

### 3. Monte Carlo Simulation

* 1,000+ simulations performed
* Each run randomly introduces misclassification
* Generates distribution of wage index distortion

---

### 4. Bias Measurement

For each simulation:

Bias (%) = (Distorted Index - True Index) / True Index

Bias Share = Bias (%) / ECI Growth (%)

---

## 📈 Key Results

* **Average Bias Share:** ~14%
* **90% Confidence Interval:** -21% to +74%
* **Standard Deviation:** ~34%

### Interpretation

* Misclassification can explain a **non-trivial portion of observed wage growth**
* Results vary depending on which occupations are misclassified
* Structured misclassification significantly reduces unrealistic volatility

---

## ⚠️ Limitations

* Misclassification is simulated, not observed directly
* Wage substitution is simplified
* Does not yet incorporate industry (NAICS) structure
* Assumes static employment weights

---

## 🚀 Future Enhancements

* ✅ Industry (NAICS) misclassification modeling
* 🔄 Probability-weighted misclassification
* 📉 Regression-based bias estimation
* 📊 Time-series alignment with ECI
* 📄 Full research paper version

---

## 🧰 Tech Stack

* Python
* pandas
* numpy
* matplotlib

---

## 📁 Project Structure

```text
.
├── data/
│   └── oews_data.xlsx
├── src/
│   ├── eci_testing
│   
├── outputs/
│   ├── charts/
│   
├── README.md
```

---

## 🧪 How to Run

1. Download OEWS data from BLS
2. Place file in `/data/`
3. Run the main script or notebook:

```bash
python src/simulation.py
```

---

## 🧠 Key Insight

> Measurement error in occupational classification can materially distort official wage statistics, potentially accounting for a meaningful share of observed ECI growth.

---

## 👤 Author

Cesar

---

## 📌 Notes

This project is intended as a demonstration of applied econometrics, labor economics, and statistical modeling using publicly available government data.

---
