"""
Classic ML Data Leakage Patterns
Demonstrates the most common forms of data leakage that LeakageHunter detects.

This file intentionally contains DATA LEAKAGE ERRORS for demonstration.
Running `demyst leakage examples/ml_data_leakage.py` will detect these issues.

The #1 error in machine learning: "If test data touches training, your benchmark is a lie."
"""

import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline


def load_medical_data():
    """Simulate medical diagnosis dataset (1000 patients, 20 features)."""
    np.random.seed(42)
    X = np.random.randn(1000, 20)
    # Target is a function of first two features (with noise)
    y = (X[:, 0] + X[:, 1] + np.random.randn(1000) * 0.5 > 0).astype(int)
    return X, y


# ==============================================================================
# ERROR 1: Preprocessing Leakage (Most Common)
# ==============================================================================

def train_with_preprocessing_leakage():
    """
    WRONG: fit_transform() is called BEFORE train_test_split.

    This means the scaler learns mean/std from ALL data including test.
    The model sees statistical properties of test data during training.

    LeakageHunter detects: preprocessing_leakage (CRITICAL)
    """
    X, y = load_medical_data()

    # ERROR: Fitting scaler on ALL data (including future test set)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)  # LeakageHunter flags this line

    # Split happens AFTER preprocessing - damage already done
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)

    # This accuracy is INFLATED - scaler saw test data statistics
    accuracy = model.score(X_test, y_test)
    return accuracy


# ==============================================================================
# ERROR 2: Feature Selection Leakage
# ==============================================================================

def train_with_feature_selection_leakage():
    """
    WRONG: SelectKBest uses target y to select features on ALL data.

    Feature selection on the full dataset means test data influences
    which features the model sees during training.

    LeakageHunter detects: preprocessing_leakage (CRITICAL)
    """
    X, y = load_medical_data()

    # ERROR: Feature selection on ALL data before split
    selector = SelectKBest(f_classif, k=10)
    X_selected = selector.fit_transform(X, y)  # LeakageHunter flags this

    # Split after feature selection - selected features are biased
    X_train, X_test, y_train, y_test = train_test_split(
        X_selected, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)

    # Accuracy is misleading - feature selection saw test labels
    return model.score(X_test, y_test)


# ==============================================================================
# ERROR 3: Test Data in Training (The Obvious One)
# ==============================================================================

def train_on_test_data():
    """
    WRONG: Explicitly training on test data.

    This seems obvious, but happens surprisingly often in complex codebases
    where variable names get confused or data is accidentally concatenated.

    LeakageHunter detects: test_in_training (CRITICAL)
    """
    X, y = load_medical_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=10, random_state=42)

    # ERROR: Training on test data!
    model.fit(X_test, y_test)  # LeakageHunter flags this line

    # Of course accuracy will be high - model memorized the test set
    return model.score(X_test, y_test)


# ==============================================================================
# CORRECT: Proper Pipeline (For Comparison)
# ==============================================================================

def train_correct_pipeline():
    """
    CORRECT: Split data FIRST, then fit preprocessing only on training set.

    The test set is never seen by any preprocessing or feature selection
    until final evaluation. This is the gold standard.
    """
    X, y = load_medical_data()

    # CORRECT: Split FIRST - test data is now isolated
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # CORRECT: Fit scaler on training data ONLY
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)  # fit on train
    X_test_scaled = scaler.transform(X_test)  # transform only (no fit!)

    # CORRECT: Feature selection on training data ONLY
    selector = SelectKBest(f_classif, k=10)
    X_train_selected = selector.fit_transform(X_train_scaled, y_train)
    X_test_selected = selector.transform(X_test_scaled)

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train_selected, y_train)

    # This accuracy is VALID - test data was never seen during training
    return model.score(X_test_selected, y_test)


def train_with_sklearn_pipeline():
    """
    BEST PRACTICE: Use sklearn Pipeline to guarantee no leakage.

    Pipeline automatically applies fit_transform on train and transform on test
    during cross_val_score, making leakage impossible.
    """
    X, y = load_medical_data()

    # Pipeline encapsulates all preprocessing
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('selector', SelectKBest(f_classif, k=10)),
        ('model', RandomForestClassifier(n_estimators=10, random_state=42))
    ])

    # cross_val_score handles train/test splitting correctly
    scores = cross_val_score(pipe, X, y, cv=5)

    return scores.mean()


if __name__ == "__main__":
    print("=" * 60)
    print("ML DATA LEAKAGE DEMONSTRATION")
    print("=" * 60)

    print("\n1. Preprocessing Leakage (fit_transform before split):")
    acc1 = train_with_preprocessing_leakage()
    print(f"   Accuracy: {acc1:.3f} (INFLATED - scaler saw test data)")

    print("\n2. Feature Selection Leakage:")
    acc2 = train_with_feature_selection_leakage()
    print(f"   Accuracy: {acc2:.3f} (INFLATED - selector saw test labels)")

    print("\n3. Training on Test Data:")
    acc3 = train_on_test_data()
    print(f"   Accuracy: {acc3:.3f} (MEANINGLESS - trained on test set)")

    print("\n4. Correct Pipeline (split first):")
    acc4 = train_correct_pipeline()
    print(f"   Accuracy: {acc4:.3f} (VALID - proper isolation)")

    print("\n5. sklearn Pipeline (best practice):")
    acc5 = train_with_sklearn_pipeline()
    print(f"   CV Accuracy: {acc5:.3f} (VALID - pipeline handles splits)")

    print("\n" + "=" * 60)
    print("Run: demyst leakage examples/ml_data_leakage.py")
    print("to see Demyst automatically detect these issues.")
    print("=" * 60)
