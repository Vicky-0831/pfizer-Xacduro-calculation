import streamlit as st
import pandas as pd
import altair as alt

# 页面配置
st.set_page_config(page_title="X药2026模拟器", layout="wide")

# --- 终极 CSS 样式 ---
st.markdown("""
    <style>
    /* 1. 【核心】针对所有启用的输入框容器：设置统一浅蓝色背景 */
    /* data-baseweb="input" 是整个输入控件的最外层盒子 */
    div[data-baseweb="input"] {
        background-color: #EBF5FB !important; /* 浅蓝色底 */
        border: 1px solid #AED6F1 !important; /* 浅蓝色边框 */
        border-radius: 5px !important;
    }
    
    /* 2. 【关键】强制内部所有子元素背景透明 */
    /* 这样无论是数字输入区，还是右边的加减号区域，都会透出上面的浅蓝色 */
    div[data-baseweb="input"] > div,
    div[data-baseweb="input"] input {
        background-color: transparent !important;
        color: #000000 !important; /* 文字黑色 */
        font-weight: 500;
    }

    /* 3. 【锁定框】针对被禁用(Locked)的输入框，强制改回灰色 */
    /* 使用 :has 选择器：如果这个盒子里包含 disabled 的 input，就变灰 */
    div[data-baseweb="input"]:has(input:disabled) {
        background-color: #f0f2f6 !important; /* 灰色底 */
        border: 1px solid rgba(49, 51, 63, 0.2) !important;
        opacity: 0.6;
    }
    
    /* 4. 锁定框里的文字颜色变浅 */
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
    
    # 单价锁定 -> 灰色
    price_per_box = st.number_input("药品单价 (元/盒)", value=3179, disabled=True, help="单价已锁定标准价格")
    
    # 启用 -> 全蓝 (包括加减号)
    daily_usage = st.number_input("一日使用盒数", value=4) 
    days_usage = st.number_input("用药天数", value=7, step=1)
    
    total_cost = price_per_box * daily_usage * days_usage
    st.write(f"**当前周期总费用:** ¥{total_cost:,.0f}")
    
    st.markdown("---")
    
    # --- B. 保障参数 ---
    st.subheader("B. 保障参数")
    st.info("多重支付设置")
    
    st.write("**第1重保障：惠民保**")
    is_huiminbao = st.checkbox("参加当地惠民保", value=True)
    
    c1, c2 = st.columns(2)
    with c1:
        # 启用 -> 全蓝
        hmb_deductible = st.number_input("惠民保起付线", value=20000.0, step=1000.0)
    with c2:
        # 启用 -> 全蓝
        hmb_rate_input = st.number_input("报销比例 (%)", value=60.0, step=5.0)
        hmb_rate = hmb_rate_input / 100.0
        
    st.markdown("---")

    st.write("**第2重保障：双坦同行项目**")
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
    
    # --- 结论行 (颜色修正版) ---
    # 天数和金额都使用绿色 #27ae60
    st.markdown(f"""
    <div style='background-color: #EBF5FB; padding: 10px; border-radius: 5px; margin-top: 10px; text-align: center; color: #0e1117;'>
        <span style='font-size: 16px; font-weight: bold;'>
            💡 多重保障后，患者用药治疗 <span style='color:#27ae60'>{int(days_usage)}</span> 天，日治疗费用：<span style='color:#27ae60'>¥{daily_avg_cost:,.0f}</span> 元
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # --- 图表：费用分担对比 ---
    st.write("### 📊 费用分担对比 (双重保障)")
    
    label_1 = '全额自费'
    label_2 = '参加地方惠民保'
    label_3 = '惠民保+双坦同行'
    
    chart_data = pd.DataFrame({
        '情景': [label_1, label_2, label_3],
        '患者自付费用': [cost_scenario_1, cost_scenario_2, cost_scenario_3],
        '标签': [f'¥{cost_scenario_1:,.0f}', f'¥{cost_scenario_2:,.0f}', f'¥{cost_scenario_3:,.0f}']
    })
    
    max_val = chart_data['患者自付费用'].max() * 1.2

    base = alt.Chart(chart_data).encode(
        x=alt.X('患者自付费用', title='患者自付费用（元）', scale=alt.Scale(domain=[0, max_val])),
        y=alt.Y('情景', sort=None, title=None), 
        tooltip=['情景', '患者自付费用']
    )

    bars = base.mark_bar(size=40).encode(
        color=alt.Color('情景', scale=alt.Scale(
            domain=[label_1, label_2, label_3],
            range=['#e74c3c', '#3498db', '#27ae60'] 
        ), legend=None)
    )
    
    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=5,
        color='black'
    ).encode(
        text='标签'
    )

    final_chart = (bars + text).properties(height=300)

    st.altair_chart(final_chart, use_container_width=True)
    
    st.info(f"📉 **节省统计：** 相比全额自费，该方案预计共为您节省 **¥{(cost_scenario_1 - cost_scenario_3):,.0f}** 元。")



