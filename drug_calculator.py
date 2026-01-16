# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import altair as alt

# 页面配置
st.set_page_config(page_title="X药2026模拟器", layout="wide")

# --- CSS 样式 ---
st.markdown("""
    <style>
    div[data-baseweb="input"] {
        background-color: #EBF5FB !important;
        border: 1px solid #AED6F1 !important;
        border-radius: 5px !important;
    }
    div[data-baseweb="input"] > div,
    div[data-baseweb="input"] input {
        background-color: transparent !important;
        color: #000000 !important;
        font-weight: 500;
    }
    div[data-baseweb="input"]:has(input:disabled) {
        background-color: #f0f2f6 !important;
        border: 1px solid rgba(49, 51, 63, 0.2) !important;
        opacity: 0.6;
    }
    div[data-baseweb="input"] input:disabled {
        color: #666666 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("X药2026多重支付商保模拟计算器")
st.markdown("---")

col1, col2 = st.columns([1, 1.5])

with col1:
    # --- A. 用药参数 ---
    st.subheader("A. 用药参数")
    st.info("基础信息设置")
    
    price_per_box = st.number_input("药品单价 (元/盒)", value=3179, disabled=True, help="单价已锁定标准价格")
    
    daily_usage = st.number_input("一日使用盒数", value=4) 
    days_usage = st.number_input("用药天数", value=7, step=1)
    
    total_cost = price_per_box * daily_usage * days_usage
    # 注意：这里去掉了Markdown里的加粗星号，改用普通文本，防止冲突
    st.write(f"当前周期总费用: ¥{total_cost:,.0f}")
    
    st.markdown("---")
    
    # --- B. 保障参数 ---
    st.subheader("B. 保障参数")
    st.info("多重支付设置")
    
    st.write("第1重保障：惠民保")
    is_huiminbao = st.checkbox("参加当地惠民保", value=True)
    
    c1, c2 = st.columns(2)
    with c1:
        hmb_deductible = st.number_input("惠民保起付线", value=20000.0, step=1000.0)
    with c2:
        hmb_rate_input = st.number_input("报销比例 (%)", value=60.0, step=5.0)
        hmb_rate = hmb_rate_input / 100.0
        
    st.markdown("---")

    st.write("第2重保障：双坦同行项目")
    is_shuangtan = st.checkbox("参加双坦同行项目", value=True)
    shuangtan_rate = 0.5 
    st.caption("说明：双坦项目直接报销总费用的 50%")

with col2:
    st.subheader("结果输出 (模拟测算)")
    
    # --- 计算逻辑 ---
    if total_cost > hmb_deductible:
        reimburse_hmb_val = (total_cost - hmb_deductible) * hmb_rate
    else:
        reimburse_hmb_val = 0.0

    reimburse_st_val = total_cost * shuangtan_rate
    
    # --- 准备图表数据 ---
    cost_scenario_1 = total_cost
    
    cost_scenario_2 = total_cost - reimburse_hmb_val
    if cost_scenario_2 < 0: cost_scenario_2 = 0
    
    total_reimb_both = reimburse_hmb_val + reimburse_st_val
    cost_scenario_3 = total_cost - total_reimb_both
    if cost_scenario_3 < 0: cost_scenario_3 = 0
    
    # --- 顶部大数字 ---
    current_reimburse = 0
    if is_huiminbao: current_reimburse += reimburse_hmb_val
    if is_shuangtan: current_reimburse += reimburse_st_val
    
    if current_reimburse > total_cost: current_reimburse = total_cost
    current_final_cost = total_cost - current_reimburse
    
    # 计算日均费用
    daily_avg_cost = current_final_cost / days_usage if days_usage > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("本周期总费用", f"¥{total_cost:,.0f}")
    m2.metric("当前报销合计", f"¥{current_reimburse:,.0f}", delta=f"省下 {current_reimburse/total_cost:.1%}")
    m3.metric("患者最终自付", f"¥{current_final_cost:,.0f}", delta_color="inverse")
    
    # --- 结论行 ---
    # 改用了纯 HTML 渲染，避开 Markdown 的正则解析风险
    st.markdown(f"""
    <div style='background-



