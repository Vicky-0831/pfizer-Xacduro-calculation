import streamlit as st
import pandas as pd
import altair as alt

# 页面配置
st.set_page_config(page_title="X药2026模拟器", layout="wide")

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
    st.write(f"**当前周期总费用:** ¥{total_cost:,.0f}")
    
    st.markdown("---")
    
    # --- B. 保障参数 ---
    st.subheader("B. 保障参数")
    st.info("多重支付设置")
    
    st.write("**第1重保障：惠民保**")
    is_huiminbao = st.checkbox("参加当地惠民保", value=True)
    
    c1, c2 = st.columns(2)
    with c1:
        hmb_deductible = st.number_input("惠民保起付线", value=20000.0, step=1000.0)
    with c2:
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
    # 情景1：无保障
    cost_scenario_1 = total_cost
    
    # 情景2：仅惠民保
    cost_scenario_2 = total_cost - reimburse_hmb_val
    if cost_scenario_2 < 0: cost_scenario_2 = 0
    
    # 情景3：惠民保 + 双坦同行
    total_reimb_both = reimburse_hmb_val + reimburse_st_val
    cost_scenario_3 = total_cost - total_reimb_both
    if cost_scenario_3 < 0: cost_scenario_3 = 0
    
    # --- 顶部大数字 ---
    current_reimburse = 0
    if is_huiminbao: current_reimburse += reimburse_hmb_val
    if is_shuangtan: current_reimburse += reimburse_st_val
    
    if current_reimburse > total_cost: current_reimburse = total_cost
    current_final_cost = total_cost - current_reimburse

    m1, m2, m3 = st.columns(3)
    m1.metric("本周期总费用", f"¥{total_cost:,.0f}")
    m2.metric("当前报销合计", f"¥{current_reimburse:,.0f}", delta=f"省下 {current_reimburse/total_cost:.1%}")
    m3.metric("患者最终自付", f"¥{current_final_cost:,.0f}", delta_color="inverse")
    
    st.divider()
    
    # --- 图表：层层保障对比图 ---
    st.write("### 📊 费用分担对比 (层层保障)")
    
    chart_data = pd.DataFrame({
        '情景': ['无保障', '仅有惠民保', '惠民保+双坦同行'],
        '患者自付费用': [cost_scenario_1, cost_scenario_2, cost_scenario_3],
        '标签': [f'¥{cost_scenario_1:,.0f}', f'¥{cost_scenario_2:,.0f}', f'¥{cost_scenario_3:,.0f}']
    })
    
    # 设置横轴的最大值，让文字能显示出来（留出20%的空间）
    max_val = chart_data['患者自付费用'].max() * 1.2

    base = alt.Chart(chart_data).encode(
        x=alt.X('患者自付费用', title='患者自付费用（元）', scale=alt.Scale(domain=[0, max_val])),
        y=alt.Y('情景', sort=None, title=None), 
        tooltip=['情景', '患者自付费用']
    )

    # 柱状图
    bars = base.mark_bar(size=40).encode(
        color=alt.Color('情景', scale=alt.Scale(
            domain=['无保障', '仅有惠民保', '惠民保+双坦同行'],
            range=['#e74c3c', '#3498db', '#27ae60']  # 红色 -> 蓝色 -> 绿色
        ), legend=None) # 隐藏图例，因为Y轴已经写得很清楚了
    )
    
    # 文字标签
    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=5,  # 偏移量
        color='black'
    ).encode(
        text='标签'
    )

    final_chart = (bars + text).properties(height=300)

    st.altair_chart(final_chart, use_container_width=True)
    
    st.info(f"💡 **结论：** 参加双重保障后，对比无保障，您本周期预计可节省 **¥{(cost_scenario_1 - cost_scenario_3):,.0f}** 元。")

