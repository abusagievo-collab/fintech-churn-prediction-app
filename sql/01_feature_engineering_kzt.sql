-- ============================================================================
-- Проект: Скоринг оттока держателей карт (Рынок РК, KZT)
-- Описание: Сборка поведенческих признаков за скользящие окна 30 и 90 дней
-- ============================================================================

WITH client_activity AS (
    SELECT
        client_id,
        city_name,
        SUM(CASE WHEN tx_date >= CURRENT_DATE - INTERVAL '30 days' THEN amount_kzt ELSE 0 END) AS spend_30d_kzt,
        SUM(CASE WHEN tx_date >= CURRENT_DATE - INTERVAL '90 days'
                  AND tx_date < CURRENT_DATE - INTERVAL '30 days' THEN amount_kzt ELSE 0 END) / 2.0 AS avg_spend_prev_60d_kzt,
        COUNT(CASE WHEN tx_date >= CURRENT_DATE - INTERVAL '30 days' AND payment_method = 'QR' THEN 1 END) AS qr_tx_cnt_30d,
        COUNT(CASE WHEN tx_date >= CURRENT_DATE - INTERVAL '30 days' AND payment_method = 'P2P' THEN 1 END) AS p2p_tx_cnt_30d,
        MAX(CURRENT_DATE - tx_date::DATE) AS days_since_last_tx
    FROM card_transactions_kzt
    GROUP BY client_id, city_name
)
SELECT
    client_id,
    city_name,
    spend_30d_kzt,
    avg_spend_prev_60d_kzt,
    ROUND(
        (spend_30d_kzt - avg_spend_prev_60d_kzt) / NULLIF(avg_spend_prev_60d_kzt, 0) * 100.0,
        2
    ) AS spend_change_pct,
    qr_tx_cnt_30d,
    p2p_tx_cnt_30d,
    days_since_last_tx,
    CASE WHEN days_since_last_tx > 45 THEN 1 ELSE 0 END AS is_churned
FROM client_activity;
