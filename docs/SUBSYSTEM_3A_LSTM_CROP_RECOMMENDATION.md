# Deep Learning Subsystem 3A — LSTM Crop Recommendation AI

## 1. Subsystem Objective
Deep Learning Subsystem 3A provides probabilistic multi-class crop suitability recommendations across 22 major Indian agricultural crop species based on 7 biochemical soil properties and environmental meteorological metrics.

$$\text{Input: } [N, P, K, \text{temperature}, \text{humidity}, \text{pH}, \text{rainfall}] \xrightarrow{\text{StandardScaler}} \mathbf{z} \in \mathbb{R}^{7} \xrightarrow{\text{Reshape}} (7, 1) \xrightarrow{\text{Bi-LSTM}} \mathbf{p} \in \Delta^{22}$$

Where $\mathbf{p} = [p_1, p_2, \dots, p_{22}]$ represents the softmax probability distribution across all 22 crop classes, with $\sum_{i=1}^{22} p_i = 1.0$.

---

## 2. Dataset & Provenance
- **Dataset File**: `ml/crop_recommendation/data/raw/crop_recommendation.csv`
- **Total Samples**: 2,200 records
- **Class Balance**: 22 unique crop species, exactly 100 samples per class (perfectly balanced 4.545% per class).
- **Missing Values / Nulls**: 0 (Complete data integrity).
- **Duplicate Rows**: 0.

### 2.1 Feature Definitions & Training Distributions
| Feature Name | Agronomic Definition | Units | Min | Mean ($\mu$) | Max | Std Dev ($\sigma$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `N` | Available soil Nitrogen | kg/ha | 0.00 | 50.46 | 140.00 | 37.02 |
| `P` | Available soil Phosphorus | kg/ha | 5.00 | 53.29 | 145.00 | 32.83 |
| `K` | Available soil Potassium | kg/ha | 5.00 | 48.13 | 205.00 | 50.70 |
| `temperature` | Ambient temperature | °C | 8.83 | 25.58 | 43.68 | 5.12 |
| `humidity` | Relative atmospheric humidity | % | 14.26 | 71.44 | 99.98 | 22.28 |
| `ph` | Soil pH level | pH (0-14) | 3.50 | 6.47 | 9.94 | 0.78 |
| `rainfall` | Seasonal crop-cycle precipitation | mm | 20.21 | 103.35 | 298.56 | 54.95 |

---

## 3. Preprocessing Pipeline & Feature Ordering
Strict chronological and stratified partition isolation is maintained to prevent data leakage:
- **Splits**: Stratified Train (70% = 1,540 samples), Validation (15% = 330 samples), Test (15% = 330 samples).
- **Feature Order**: `['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']` (Invariance enforced across training, FastAPI service, and Angular UI).
- **Feature Scaling**: Scikit-Learn `StandardScaler` fitted strictly on the 70% training split:
  $$\mathbf{z}_j = \frac{x_j - \mu_{\text{train}, j}}{\sigma_{\text{train}, j}}$$
- **Sequence Reshaping**: Continuous 7-dimensional tabular vectors are mapped into temporal sequence arrays of dimension `(batch_size, timesteps=7, features=1)` to permit recurrent contextual modeling across biochemical and meteorological gradients.

---

## 4. Deep Learning Architecture (Bidirectional LSTM)
The neural network employs a 2-layer stacked Bidirectional Long Short-Term Memory (Bi-LSTM) network serialized in Keras format (`crop_recommendation_lstm.keras`):

```text
Input Layer: Shape (None, 7, 1)
   │
   ▼
Bidirectional LSTM (Layer 1): 64 units per direction (128 total), return_sequences=True
   │
   ▼
Batch Normalization + Dropout (rate=0.2)
   │
   ▼
Bidirectional LSTM (Layer 2): 32 units per direction (64 total), return_sequences=False
   │
   ▼
Batch Normalization + Dropout (rate=0.2)
   │
   ▼
Dense Hidden Layer: 64 units, ReLU activation + L2 regularization
   │
   ▼
Dense Output Layer: 22 units, Softmax activation
```

- **Loss Function**: Categorical Crossentropy ($-\sum_{c=1}^{22} y_c \log p_c$)
- **Optimizer**: Adam ($\eta = 0.001$, $\beta_1=0.9, \beta_2=0.999$)
- **Output Constraint**: $\sum_{i=1}^{22} P(\text{crop}_i | \mathbf{x}) = 1.000000$

---

## 5. Crop Classes & Category Taxonomy
The model recommends across 22 classes:
1. **Cereals / Grains**: `rice`, `maize`
2. **Pulses & Legumes**: `chickpea`, `kidneybeans`, `pigeonpeas`, `mothbeans`, `mungbean`, `blackgram`, `lentil`
3. **Commercial Cash Crops**: `cotton`, `jute`, `coffee`
4. **Horticultural Fruits**: `pomegranate`, `banana`, `mango`, `grapes`, `apple`, `orange`, `papaya`, `coconut`
5. **Cucurbits / Summer Crops**: `watermelon`, `muskmelon`

---

## 6. Dynamic Top-5 Inference & Ranking Methodology
1. Raw inputs $[N, P, K, T, H, \text{pH}, R]$ undergo bounds verification against agronomic constraints.
2. The vector is standardized via `scaler.transform()` and reshaped to `(1, 7, 1)`.
3. The neural network computes $\mathbf{p} = \text{Softmax}(\text{LSTM}(\mathbf{x}))$.
4. Output probabilities are sorted descending ($\text{argsort}(\mathbf{p})[::-1]$).
5. The top 5 ranked indices are mapped to species names with rank $r \in \{1, 2, 3, 4, 5\}$, confidence probabilities, and agronomic metadata.

> [!NOTE]
> Probabilities represent **AI Model Suitability Scores** derived from the trained conditional distribution $P(C=c | \mathbf{X}=\mathbf{x})$ and should not be construed as absolute harvest guarantees.

---

## 7. India-Wide Architecture & Geographic Scope
- **Location-Agnostic Core**: The core LSTM model operates exclusively on biochemical soil properties and meteorological variables. It contains no hardcoded regional rules or state overrides (e.g. `if state == "Maharashtra"`).
- **Contextual Metadata**: State and District inputs are accepted solely as descriptive metadata for agronomic context.
- **Geographic Honesty**: The underlying dataset captures 22 crop agro-climatic envelopes prevalent across India. It applies to diverse agro-climatic zones (Gangetic plains, Deccan plateau, Western Ghats, Himalayan valleys, and semi-arid zones) within the observed physiological envelopes.

---

## 8. Out-of-Distribution (OOD) Diagnostics
When inputs deviate from the training distribution envelope ($N > 140$, $P > 145$, $K > 205$, $T \notin [8.8, 43.7]$, $H < 14.3$, $\text{pH} \notin [3.5, 9.9]$, $\text{Rainfall} > 298.6\text{ mm}$), the backend flags `out_of_distribution: true` and generates descriptive warnings:
- **Rainfall Cycle Warning**: Clarifies that the model expects seasonal crop-cycle precipitation ($20 - 300\text{ mm}$), not cumulative annual rainfall ($1000+\text{ mm}$).
- **High Potassium Warning**: Identifies that $K \ge 190\text{ kg/ha}$ is characteristic of plantation fruits (`apple`, `grapes`), whereas field crops (`cotton`, `maize`) require $15 - 30\text{ kg/ha}$.

---

## 9. API Specification
- **Endpoint**: `POST /api/v1/crop/recommend`
- **Request Body**:
```json
{
  "N": 90.0,
  "P": 42.0,
  "K": 43.0,
  "temperature": 20.87,
  "humidity": 82.00,
  "ph": 6.50,
  "rainfall": 202.93,
  "top_k": 5,
  "country": "India",
  "state": "West Bengal",
  "district": "Burdwan"
}
```
- **Response Body**:
```json
{
  "success": true,
  "data": {
    "recommended_crop": "rice",
    "confidence": 0.9412,
    "recommendations": [
      { "crop": "rice", "probability": 0.9412, "rank": 1 },
      { "crop": "jute", "probability": 0.0321, "rank": 2 },
      { "crop": "papaya", "probability": 0.0156, "rank": 3 },
      { "crop": "coconut", "probability": 0.0078, "rank": 4 },
      { "crop": "maize", "probability": 0.0033, "rank": 5 }
    ],
    "execution_time_ms": 8.4,
    "model_type": "Bidirectional LSTM (22 classes)",
    "out_of_distribution": false,
    "ood_warnings": [],
    "location_context": {
      "country": "India",
      "state": "West Bengal",
      "district": "Burdwan"
    }
  }
}
```
