import numpy as np
import pandas as pd
import json
import time
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
import shap

TARGET = "TotalCost"


def mape(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def split_80_10_10(df, target=TARGET, seed=42, stratify_col=None):
    strat = df[stratify_col] if stratify_col and stratify_col in df.columns else None
    train, temp = train_test_split(df, test_size=0.20, random_state=seed, stratify=strat)
    strat2 = temp[stratify_col] if stratify_col and stratify_col in temp.columns else None
    val, test = train_test_split(temp, test_size=0.50, random_state=seed, stratify=strat2)
    return train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)


def get_model(algo, seed=42):
    if algo == "XGBoost":
        return xgb.XGBRegressor(
            n_estimators=400, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, tree_method="hist",
            random_state=seed, n_jobs=1, verbosity=0
        )
    if algo == "LightGBM":
        return lgb.LGBMRegressor(
            n_estimators=400, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            random_state=seed, n_jobs=1, verbosity=-1
        )
    if algo == "CatBoost":
        return CatBoostRegressor(
            iterations=400, depth=6, learning_rate=0.05,
            random_state=seed, thread_count=1, verbose=False
        )
    raise ValueError(algo)


def train_eval_one(algo, feature_cols, train, val, test, log_transform, seed=42):
    Xtr, ytr = train[feature_cols], train[TARGET].values
    Xva, yva = val[feature_cols], val[TARGET].values
    Xte, yte = test[feature_cols], test[TARGET].values

    if log_transform:
        ytr_fit = np.log1p(ytr)
        yva_fit = np.log1p(yva)
    else:
        ytr_fit = ytr
        yva_fit = yva

    model = get_model(algo, seed)
    t0 = time.time()
    if algo == "XGBoost":
        model.set_params(early_stopping_rounds=30)
        model.fit(Xtr, ytr_fit, eval_set=[(Xva, yva_fit)], verbose=False)
    elif algo == "LightGBM":
        model.fit(Xtr, ytr_fit, eval_set=[(Xva, yva_fit)],
                   callbacks=[lgb.early_stopping(30, verbose=False)])
    elif algo == "CatBoost":
        model.fit(Xtr, ytr_fit, eval_set=(Xva, yva_fit), early_stopping_rounds=30, verbose=False)
    train_time = time.time() - t0

    pred_test_raw = model.predict(Xte)
    if log_transform:
        pred_test = np.expm1(pred_test_raw)
        pred_test = np.clip(pred_test, 0, None)
    else:
        pred_test = pred_test_raw

    metrics = {
        "MAE": float(mean_absolute_error(yte, pred_test)),
        "RMSE": float(np.sqrt(mean_squared_error(yte, pred_test))),
        "MAPE": mape(yte, pred_test),
        "R2": float(r2_score(yte, pred_test)),
        "train_time_sec": round(train_time, 2),
    }

    # SHAP on a sample of the test set (TreeExplainer, fast for GBMs)
    shap_sample = Xte.sample(min(500, len(Xte)), random_state=seed)
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(shap_sample)
        mean_abs_shap = pd.Series(np.abs(shap_values).mean(axis=0), index=feature_cols) \
            .sort_values(ascending=False)
    except Exception as e:
        shap_values = None
        mean_abs_shap = pd.Series(dtype=float)
        print("SHAP failed for", algo, log_transform, ":", e)

    return model, metrics, shap_values, shap_sample, mean_abs_shap
