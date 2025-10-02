import streamlit as st
import pandas as pd
import numpy as np

st.title('简单的 Streamlit 应用')

st.write('这是一个不需要网络连接的演示应用。')

# 生成一些示例数据
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c']
)

st.line_chart(chart_data)

# 添加一些交互元素
name = st.text_input('输入你的名字：')
if name:
    st.write(f'你好，{name}！')

# 滑块
value = st.slider('选择一个数值', 0, 100, 50)
st.write(f'你选择的数值是：{value}')

# 按钮
if st.button('点击我'):
    st.balloons()
    st.success('恭喜！你点击了按钮！')