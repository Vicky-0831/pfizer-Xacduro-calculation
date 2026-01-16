import streamlit as st
import pandas as pd
import altair as alt

# 设置网页配置
st.set_page_config(page_title="X药2026模拟器", layout="wide")

# 1. 修改标题
st.title("X药2026多重支付商保模拟计算器")
st.markdown("---")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("A. 用药与保障参数")
    
    # --- 用药参数 ---
    st.info("基础信息设置")
    # 为了方便演示，这里默认值还是辉瑞那个，您可以自己改
    price_per_box = st.number_input("药品单价 (元/盒)", value=3179)
    daily_usage = st.number_input("一日使用盒数", value=4) 
    days_per_year = st.number_input("年用药天数", value=365)
    
    # 计算年总费用
    total_cost = price_per_box * daily_usage * days_per_year
    st.write(f"**年用药总费用:** ¥{total_cost:,.0f}")
    
    st.markdown("---")
    
    # --- 保障参数 ---
    st.info("多重支付设置")
    
    # 第1重：双坦同行
    st.write("**第1重保障：双坦同行项目**")
    is_shuangtan = st.checkbox("参加双坦同行项目", value=True)
    shuangtan_rate = 0.5 if is_shuangtan else 0.0
    
    # 第2重：惠民保 (逻辑大改)
    st.write("**第2重保障：惠民保**")
    is_huiminbao = st.checkbox("参加当地惠民保", value=True)
    
    huiminbao_deductible = 0.0
    huiminbao_rate = 0.0
    
    if is_huiminbao:
        # 这里做成两列，显得紧凑点
        c1, c2 = st.columns(2)
        with c1:
            huiminbao_deductible = st.number_input("起付线 (元)", value=20000.0, step=1000.0)
        with c2:
            rate_input = st.number_input("报销比例 (%)", value=60.0, step=5.0)
            huiminbao_rate = rate_input / 100.0
        
        st.caption(f"说明：将在第1重保障后，对超过 {huiminbao_deductible:,.0f} 元的部分按 {rate_input}% 报销")

with col2:
    st.subheader("结果输出 (模拟测算)")
    
    # --- 计算核心逻辑 ---
    
    # 1. 计算双坦减免
    jianmian_shuangtan = total_cost * shuangtan_rate
    
    # 2. 计算惠民保减免 (关键逻辑：基于双坦减免后的剩余金额计算)
    remaining_after_layer1 = total_cost - jianmian_shuangtan
    
    # 如果剩余金额大于起付线，才进行报销计算，否则报销为0
    if is_huiminbao and remaining_after_layer1 > huiminbao_deductible:
        calculable_amount = remaining_after_layer1 - huiminbao_deductible
        jianmian_huiminbao = calculable_amount * huiminbao_rate
    else:
        jianmian_huiminbao = 0.0
        
    # 3. 汇总
    total_reimburse = jianmian_shuangtan + jianmian_huiminbao
    final_cost = total_cost - total_reimburse
    monthly_cost = final_cost / 12 if final_cost > 0 else 0
    
    # --- 顶部大数字展示 ---
    m1, m2, m3 = st.columns(3)
    m1.metric("年总费用", f"¥{total_cost:,.0f}")
    m2.metric("报销合计", f"¥{total_reimburse:,.0f}", delta=f"总报销比例 {total_reimburse/total_cost:.1%}")
    m3.metric("患者年自付", f"¥{final_cost:,.0f}", delta_color="inverse")
    
    st.divider()
    st.success(f"患者月自付费用 (平均): ¥{monthly_cost:,.0f}")

    # --- 图表：单柱堆叠图 (层层递减效果) ---
    st.write("### 费用分担构成 (层层支付)")
    
    # 准备数据：把三个部分叠在一起
    # 注意顺序：我们希望 自付在最下面，惠民保在中间，双坦在最上面
    chart_data = pd.DataFrame({
        '费用类型': ['1. 双坦同行支付', '2. 惠民保报销', '3. 患者自付'], 
        '金额': [jianmian_shuangtan, jianmian_huiminbao, final_cost],
        '项目': ['X药总费用'] * 3  # 只要一根柱子，所以这里名字要一样
    })
    
    # 颜色定义
    # 双坦(蓝)，惠民保(绿)，患者自付(红)
    domain_ = ['1. 双坦同行支付', '2. 惠民保报销', '3. 患者自付']
    range_ = ['#3498db', '#2ecc71', '#e74c3c'] 

    chart = alt.Chart(chart_data).mark_bar(size=100).encode(
        x=alt.X('项目', title=None, axis=None), # 不显示X轴标题，简洁
        y=alt.Y('金额', title='金额 (元)'),
        color=alt.Color('费用类型', scale=alt.Scale(domain=domain_, range=range_), legend=alt.Legend(title="支付方")),
        tooltip=['费用类型', '金额'],
        order=alt.Order('费用类型', sort='ascending') # 控制堆叠顺序
    ).properties(
        height=400
    )

    st.altair_chart(chart, use_container_width=True)
