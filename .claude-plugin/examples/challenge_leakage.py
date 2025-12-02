"""
🔓 CHALLENGE: Find the Data Leakage

This code trains a model to predict house prices. The test accuracy looks
great at 95%! But there's a subtle bug that makes the benchmark unreliable.

Can you spot it before running demyst?

Run: demyst analyze challenge_leakage.py

Hint: The bug is in the preprocessing pipeline.
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Simulated house price data
np.random.seed(42)
n_samples = 1000

# Features: size, bedrooms, neighborhood (categorical)
size = np.random.uniform(500, 5000, n_samples)
bedrooms = np.random.randint(1, 6, n_samples)
neighborhoods = np.random.choice(["urban", "suburban", "rural"], n_samples)

# Target: price (correlated with features)
price = size * 100 + bedrooms * 10000 + np.random.randn(n_samples) * 50000

# Create feature matrix
X = np.column_stack([size, bedrooms])

# ========================================
# BUG IS SOMEWHERE IN THIS SECTION
# ========================================

# Encode categorical feature using ALL data
le = LabelEncoder()
neighborhood_encoded = le.fit_transform(neighborhoods)  # 🤔 Hmm...
X = np.column_stack([X, neighborhood_encoded])

# Normalize features using ALL data
scaler = StandardScaler()
X_normalized = scaler.fit_transform(X)  # 🤔 Hmm...

# NOW split the data
X_train, X_test, y_train, y_test = train_test_split(
    X_normalized, price, test_size=0.2, random_state=42
)

# ========================================
# END OF BUG SECTION
# ========================================

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)

print(f"Test R² Score: {r2:.3f}")  # Looks great! But is it honest?

# The "fix" would be to encode and scale AFTER splitting,
# fitting only on training data.
"""
SOLUTION (don't peek until you've tried!):

The bug: Both LabelEncoder and StandardScaler are fit on ALL data
before the train/test split. This means:
1. The encoder "knows" all neighborhood categories (including test)
2. The scaler "knows" the mean/std of ALL data (including test)

This is data leakage! The test metrics are inflated.

Correct approach:
1. Split first
2. Fit encoder and scaler on TRAINING data only
3. Transform both train and test using the fitted transformers
"""
