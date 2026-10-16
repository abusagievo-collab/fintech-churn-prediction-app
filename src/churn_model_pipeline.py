"""
Пайплайн обучения модели оттока и расчета оптимального порога удержания в тенге (KZT).
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score


def train_and_optimize_threshold(df: pd.DataFrame, bonus_cost_kzt: int = 3000, retention_rate: float = 0.35) -> dict:
    """
    Обучает модель скоринга оттока и находит порог вероятности, максимизирующий
    чистую сохраненную прибыль банка в тенге (KZT).
    """
    features = ["spend_30d_kzt", "spend_change_pct", "qr_tx_cnt_30d", "p2p_tx_cnt_30d", "support_calls_30d"]
    X = df[features]
    y = df["is_churned"]

    model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42)
    model.fit(X, y)
    probs = model.predict_proba(X)[:, 1]
    df = df.copy()
    df["churn_prob"] = probs

    best_threshold = 0.5
    best_net_benefit_kzt = -np.inf

    for threshold in np.linspace(0.2, 0.8, 25):
        targeted = df[df["churn_prob"] >= threshold]
        campaign_cost = len(targeted) * bonus_cost_kzt
        saved_margin = (targeted["is_churned"] * targeted["monthly_ltv_margin_kzt"] * retention_rate).sum()
        net_benefit = saved_margin - campaign_cost

        if net_benefit > best_net_benefit_kzt:
            best_net_benefit_kzt = net_benefit
            best_threshold = threshold

    return {
        "roc_auc": round(roc_auc_score(y, probs), 3),
        "optimal_threshold": round(float(best_threshold), 2),
        "net_benefit_kzt": round(float(best_net_benefit_kzt), 0),
    }


if __name__ == "__main__":
    sample_df = pd.read_csv("data/processed/bank_churn_sample_kzt.csv")
    result = train_and_optimize_threshold(sample_df)
    print(f"Метрики модели и оптимизации (KZT): {result}")
