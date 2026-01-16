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
    
    # 1. 单价锁定 (disabled=True)
    price_per_box = st.number_input("药品单价 (元/盒)", value=3179, disabled=True, help="单价已锁定标准价格")
    
    # 2. 用量设置
    daily_usage = st.number_input("一日使用盒数", value=4) 
    
    # 3. 天数 (默认改为了7)
    days_usage = st.number_input("用药天数", value=7, step=1)
    
    # 算一下总价
    total_cost = price_per_box * daily_usage * days_usage
    st.write(f"**当前周期总费用:** ¥{total_cost:,.0f}")
    
    st.markdown("---")
    
    # --- B. 保障参数 ---
    st.subheader("B. 保障参数")
    st.info("多重支付设置")
    
    # 调整顺序：先放惠民保
    st.write("**第1重保障：惠民保**")
    # 虽然图表会强制对比，但这里勾选影响顶部的数字计算
    is_huiminbao = st.checkbox("参加当地惠民保", value=True)
    
    c1, c2 = st.columns(2)
    with c1:
        hmb_deductible = st.number_input("惠民保起付线", value=20000.0, step=1000.0)
    with c2:
        hmb_rate_input = st.number_input("报销比例 (%)", value=60.0, step=5.0)
        hmb_rate = hmb_rate_input / 100.0
        
    st.markdown("---")

    # 再放双坦同行
    st.write("**第2重保障：双坦同行项目**")
    is_shuangtan = st.checkbox("参加双坦同行项目", value=True)
    shuangtan_rate = 0.5 # 固定50%
    st.caption("说明：双坦项目直接报销总费用的 50%")

with col2:
    st.subheader("结果输出 (模拟测算)")
    
    # --- 后台逻辑计算 ---
    # 这里的逻辑：两个保险是独立计算的，然后叠加
    
    # 1. 计算惠民保报销额 (独立逻辑：总价 - 起付线 * 比例)
    # 只要总价超过起付线，就开始算，不管双坦有没有报
    if total_cost > hmb_deductible:
        reimburse_hmb_val = (total_cost - hmb_deductible) * hmb_rate
    else:
        reimburse_hmb_val = 0.0

    # 2. 计算双坦报销额 (独立逻辑：总价 * 50%)
    reimburse_st_val = total_cost * shuangtan_rate
    
    # --- 准备图表需要的对比数据 (无论用户是否勾选，我们都算出三种情况给患者看) ---
    
    # 情况1：啥都没有
    cost_scenario_1 = total_cost
    
    # 情况2：只有惠民保
    cost_scenario_2 = total_cost - reimburse_hmb_val
    if cost_scenario_2 < 0: cost_scenario_2 = 0 # 防止负数
    
    # 情况3：双重保障 (惠民保 + 双坦)
    # 注意：这里假设两者可以叠加报销，直到患者自付为0为止
    total_reimb_both = reimburse_hmb_val + reimburse_st_val
    cost_scenario_3 = total_cost - total_reimb_both
    if cost_scenario_3 < 0: cost_scenario_3 = 0
    
    # --- 根据用户勾选展示顶部的“当前结果” ---
    current_reimburse = 0
    if is_huiminbao:
        current_reimburse += reimburse_hmb_val
    if is_shuangtan:
        current_reimburse += reimburse_st_val
        
    # 防止报销超过总价 (虽然实际上不太可能，但程序要严谨)
    if current_reimburse > total_cost:
        current_reimburse = total_cost
        
    current_final_cost = total_cost - current_reimburse

    # 展示大数字
    m1, m2, m3 = st.columns(3)
    m1.metric("本周期总费用", f"¥{total_cost:,.0f}")
    m2.metric("当前报销合计", f"¥{current_reimburse:,.0f}", delta=f"省下 {current_reimburse/total_cost:.1%}")
    m3.metric("患者最终自付", f"¥{current_final_cost:,.0f}", delta_color="inverse")
    
    st.divider()
    
    # --- 图表：层层保障对比图 ---
    st.write("### 📊 费用分担对比 (层层保障)")
    st.caption("直观对比：不参加保险 vs 仅参加惠民保 vs 参加双重保障的支付差异")
    
    # 构造数据
    chart_data = pd.DataFrame({
        '情景': ['1. 全自费 (无保障)', '2. 仅有惠民保', '3. 惠民保 + 双坦同行 (推荐)'],
        '患者支付金额': [cost_scenario_1, cost_scenario_2, cost_scenario_3],
        '说明': [f'¥{cost_scenario_1:,.0f}', f'¥{cost_scenario_2:,.0f}', f'¥{cost_scenario_3:,.0f}']
    })
    
    # 颜色设置：灰色(惨) -> 蓝色(还行) -> 绿色(最棒)
    # 这是一个横向条形图
    base = alt.Chart(chart_data).encode(
        x=alt.X('患者支付金额', title='患者需要掏腰包的钱 (元)'),
        y=alt.Y('情景', sort=None, title=None), # 不排序，按我们定义的顺序
        tooltip=['情景', '患者支付金额']
    )

    bars = base.mark_bar(size=40).encode(
        color=alt.Color('情景', scale=alt.Scale(
            domain=['1. 全自费 (无保障)', '2. 仅有惠民保', '3. 惠民保 + 双坦同行 (推荐)'],
            range=['#95a5a6', '#3498db', '#27ae60'] 
        ))
    )
    
    # 在柱子旁边加上具体的金额数字，更直观
    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=3  # 向右偏移一点点
    ).encode(
        text='说明'
    )

    final_chart = (bars + text).properties(height=300)

    st.altair_chart(final_chart, use_container_width=True)
    
    st.info(f"💡 **结论：** 参加双重保障后，对比全自费，您本周期预计可节省 **¥{(cost_scenario_1 - cost_scenario_3):,.0f}** 元。")

