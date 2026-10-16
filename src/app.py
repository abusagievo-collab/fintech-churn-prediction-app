import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Fintech Churn ROI Calculator (KZT)", layout="wide")

st.title("Калькулятор ROI удержания клиентов банка (Рынок РК, ₸)")
st.markdown(
    "Интерактивный симулятор для выбора оптимального порога запуска кэшбэк-кампании "
    "на основе ML-скоринга вероятности оттока."
)

df = pd.read_csv("data/processed/bank_churn_sample_kzt.csv")

st.sidebar.header("Параметры кампании (KZT)")
bonus_kzt = st.sidebar.slider("Размер кэшбэк-бонуса на 1 клиента (₸)", 1000, 10000, 3000, step=500)
retention_uplift = st.sidebar.slider("Ожидаемая конверсия в сохранение (%)", 10, 60, 35, step=5) / 100.0
threshold = st.sidebar.slider("Порог вероятности оттока для отправки оффера", 0.20, 0.90, 0.55, step=0.05)

targeted = df[df["predicted_churn_prob"] >= threshold]
cost_kzt = len(targeted) * bonus_kzt
saved_kzt = (targeted["is_churned"] * targeted["monthly_ltv_margin_kzt"] * retention_uplift).sum()
net_effect_kzt = saved_kzt - cost_kzt

col1, col2, col3 = st.columns(3)
col1.metric("Охват кампании (клиентов)", f"{len(targeted)}")
col2.metric("Затраты на кэшбэк-бонусы", f"{cost_kzt:,.0f} ₸")
col3.metric("Чистая выгода банка (Net ROI)", f"{net_effect_kzt:,.0f} ₸")

st.subheader("Список клиентов в зоне риска (приоритет реактивации)")
st.dataframe(
    targeted[["client_id", "city_name", "spend_30d_kzt", "qr_tx_cnt_30d", "predicted_churn_prob", "monthly_ltv_margin_kzt"]]
    .sort_values("predicted_churn_prob", ascending=False),
    use_container_width=True,
)
