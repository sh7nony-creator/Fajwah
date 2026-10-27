import streamlit as st

st.set_page_config(page_title='فَجْوَة', page_icon='🇸🇦', layout='wide', initial_sidebar_state='collapsed')
navigation = st.navigation([
    st.Page('pages/regional.py', title='التحليل الإقليمي', default=True),
    st.Page('pages/national.py', title='المؤشرات الوطنية'),
    st.Page('pages/methodology.py', title='المنهجية والمصادر'),
])
navigation.run()
