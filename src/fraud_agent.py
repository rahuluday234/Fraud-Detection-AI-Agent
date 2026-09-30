import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sqlalchemy import create_engine
import datetime

# --- Load Dataset from Excel ---
def load_data(file_path=r"C:\Users\Rahul\OneDrive\Desktop\Fraud Detection Dataset.xlsx"):
    print("🚀 Fraud Agent Script Started")
    df = pd.read_excel(file_path)
    print("✅ Dataset loaded. Shape:", df.shape)
    return df

# --- Train Model ---
def train_model(df, target_col="is_fraud"):
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found. Available columns: {df.columns.tolist()}")

    # Separate features and target
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Drop ID-like columns that don’t help prediction
    id_columns = [
        column for column in X.columns
        if column.lower().replace("_", "") in {"transactionid", "txnid"}
    ]
    X = X.drop(columns=id_columns)

    # Identify categorical columns
    categorical_columns = X.select_dtypes(include=["object", "category"]).columns.tolist()

    # Force categorical columns to string type (avoids int/str mix error)
    for col in categorical_columns:
        X[col] = X[col].astype(str)

    # Drop high-cardinality columns (too many unique values)
    high_cardinality_columns = [
        column for column in categorical_columns
        if X[column].nunique(dropna=False) > len(X) * 0.5
    ]
    X = X.drop(columns=high_cardinality_columns)

    # Update categorical list after dropping
    categorical_columns = [
        column for column in categorical_columns
        if column not in high_cardinality_columns
    ]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Preprocessor
    preprocessor = ColumnTransformer(
        [("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_columns)],
        remainder="passthrough",
    )

    # Model pipeline
    model = make_pipeline(
        preprocessor,
        RandomForestClassifier(class_weight="balanced", random_state=42, n_estimators=100),
    )
    model.fit(X_train, y_train)

    print("\n📊 Model Evaluation Summary:")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    return model, X_test, y_test

# --- Predict Fraud for Test Set ---
def predict_and_highlight(model, X_test, y_test, threshold=0.8):
    y_proba = model.predict_proba(X_test)[:, 1]
    suspected = []

    for i, prob in enumerate(y_proba):
        if prob > threshold:
            suspected.append((i, prob, y_test.iloc[i]))

    print(f"\n⚠️ Suspected Fraud Transactions (probability > {threshold}):")
    if suspected:
        for idx, prob, actual in suspected[:20]:  # show only first 20 to keep output clean
            print(f"Row {idx} → Probability: {prob:.2f}, Actual Label: {actual}")
    else:
        print("No suspected fraud transactions found above threshold.")

    return suspected

# --- Log Audit Trail ---
engine = create_engine("sqlite:///audit_trail.db")

def log_audit(suspected):
    timestamp = datetime.datetime.now()
    audit_entries = pd.DataFrame([{
        "row_index": idx,
        "probability": prob,
        "actual_label": actual,
        "timestamp": timestamp
    } for idx, prob, actual in suspected])
    audit_entries.to_sql("audit_logs", engine, if_exists="append", index=False)
    print(f"\n📝 {len(suspected)} suspected fraud transactions logged to audit_trail.db")

# --- Export Suspected Frauds to CSV ---
def export_suspected_to_csv(suspected, filename="suspected_frauds.csv"):
    audit_entries = pd.DataFrame([{
        "row_index": idx,
        "probability": prob,
        "actual_label": actual
    } for idx, prob, actual in suspected])
    audit_entries.to_csv(filename, index=False)
    print(f"📂 Suspected frauds exported to {filename}")

# --- Main Script ---
if __name__ == "__main__":
    df = load_data()
    model, X_test, y_test = train_model(df, target_col="is_fraud")

    suspected = predict_and_highlight(model, X_test, y_test, threshold=0.8)
    if suspected:
        log_audit(suspected)
        export_suspected_to_csv(suspected)

