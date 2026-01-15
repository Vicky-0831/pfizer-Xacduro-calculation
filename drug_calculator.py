import streamlit as st
import pandas as pd
import altair as alt

# 设置网页标题和布局
st.set_page_config(page_title="鼎优乐价格模拟器", layout="wide")

# 标题 (无Emoji)
st.title("辉瑞鼎优乐 - 费用模拟计算器")
st.markdown("---")

# 创建两列布局
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("A. 用药与保障参数")
    
    # 1. 用药参数
    st.info("基础信息设置")
    price_per_box = st.number_input("药品单价 (元/盒)", value=3179)
    daily_usage = st.number_input("一日使用盒数", value=4) 
    days_per_year = st.number_input("年用药天数", value=365)
    
    # 计算总费用
    total_cost = price_per_box * daily_usage * days_per_year
    st.write(f"**年用药总费用:** ¥{total_cost:,.0f}")
    
    st.markdown("---")
    
    # 2. 保障参数
    st.info("报销项目设置")
    
    # 第一重：双坦同行
    st.write("**第1重保障：双坦同行项目**")
    is_shuangtan = st.checkbox("参加双坦同行项目", value=True)
    shuangtan_rate = 0.5 if is_shuangtan else 0.0
    
    # 第二重：惠民保
    st.write("**第2重保障：惠民保**")
    is_huiminbao = st.checkbox("购买惠民保", value=True)
    
    if is_huiminbao:
        huiminbao_amt = st.number_input("请输入惠民保报销金额 (元)", value=0, step=1000, help="此处没有公式，请根据实际保单手动填写")
    else:
        huiminbao_amt = 0

with col2:
    st.subheader("结果输出 (模拟测算)")
    
    # 计算逻辑
    jianmian_shuangtan = total_cost * shuangtan_rate
    jianmian_huiminbao = huiminbao_amt
    total_reimburse = jianmian_shuangtan + jianmian_huiminbao
    final_cost = total_cost - total_reimburse
    monthly_cost = final_cost / 12 if final_cost > 0 else 0
    
    # 展示核心大数字
    m1, m2, m3 = st.columns(3)
    m1.metric("年总费用", f"¥{total_cost:,.0f}")
    m2.metric("报销合计", f"¥{total_reimburse:,.0f}", delta=f"- 减免 {total_reimburse/total_cost:.1%}")
    m3.metric("患者年自付", f"¥{final_cost:,.0f}", delta_color="inverse")
    
    st.divider()
    
    st.success(f"患者月自付费用 (平均): ¥{monthly_cost:,.0f}")

    # 制作可视化图表
    st.write("### 费用构成分析")
    
    # 准备数据
    data = pd.DataFrame({
        '项目': ['双坦同行减免', '惠民保减免', '患者自付'],
        '金额': [jianmian_shuangtan, jianmian_huiminbao, final_cost]
    })
    
    # 使用 Altair 制作三色图表
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('项目', sort=None),
        y='金额',
        # 颜色代码：蓝色、绿色、红色
        color=alt.Color('项目', scale=alt.Scale(
            domain=['双坦同行减免', '惠民保减免', '患者自付'],
            range=['#3498db', '#2ecc71', '#e74c3c'] 
        )),
        tooltip=['项目', '金额']
    ).properties(
        height=400
    )

    st.altair_chart(chart, use_container_width=True)
