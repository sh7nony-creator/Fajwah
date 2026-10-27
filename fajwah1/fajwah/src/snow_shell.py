"""Snow dashboard shell. Layout and markup only; all values come from the engine."""
from pathlib import Path
from html import escape
import base64
import streamlit as st
from .regional_ui import CSS, insight_head, mini_cards, count_comparison, status
from .data import POP, ELDERLY

ASSETS = Path(__file__).resolve().parents[1] / 'assets'

def icon(name):
    path = ASSETS / (name + '.svg')
    return '<img alt="" src="data:image/svg+xml;base64,' + base64.b64encode(path.read_bytes()).decode() + '">'

def _shell_content(title):
    st.html(CSS)
    st.html('<style>' + (ASSETS/'snow.css').read_text(encoding='utf-8') + '</style>')
    st.markdown(f'''<div class="brand"><div class="brand-name">{icon('imgChartPieSlice')} فَجْوَة</div><div class="brand-sub">توزيع الجهات غير الربحية</div></div>
<div class="snow-favorites"><span>نظرة عامة</span><span>المصادر</span><p>• المملكة العربية السعودية</p><p>• 13 منطقة إدارية</p></div>''', unsafe_allow_html=True)
    with st.container(key='top_nav'):
        st.page_link('pages/regional.py', label='التحليل الإقليمي')
        st.page_link('pages/national.py', label='المؤشرات الوطنية')
        st.page_link('pages/methodology.py', label='المنهجية والمصادر')
    st.markdown(f'''<header class="snow-header"><div class="snow-breadcrumb">{icon('imgSidebar')}{icon('imgStar')}<span>لوحات التحليل</span><i>/</i><b>{escape(title)}</b></div><div class="snow-header-info">المملكة العربية السعودية</div></header>
<div class="sidebar-note"><strong>فَجْوَة</strong>البيانات والمصادر المعتمدة<br>السكان 2024 · كبار السن 2025</div>''', unsafe_allow_html=True)
    if title != 'التحليل الإقليمي':
        st.markdown('<style>[data-testid="stMain"]{margin-left:0;width:calc(100% - 212px);max-width:calc(100% - 212px)}.snow-header{left:0}@media(max-width:1100px){[data-testid="stMain"]{width:100%;max-width:100%;margin:0}}</style>',unsafe_allow_html=True)

def shell(title):
    with st.container(key='shell_mount'):
        _shell_content(title)

def insight_rail(frame, details, m, metric, basis):
    row = frame.loc[frame.Region == details['region']].iloc[0]
    tone = status(details)[1]
    text = 'أقل' if details['density_gap'] > 0 else 'أعلى'
    reading = f'كثافة الجهات {text} من المعدل الوطني بنسبة {abs(details["relative_pct"]):,.2f}%.' if round(details['density_gap'],2) else 'كثافة المنطقة عند المعدل الوطني تقريبًا.'
    markup = '<aside class="snow-rail" aria-label="رؤى المنطقة">'
    markup += insight_head(details,m,basis,tone)
    markup += mini_cards(row,details,POP,ELDERLY)
    markup += count_comparison(details,tone)
    markup += f'<div class="panel-section">قراءة التوزيع</div><p class="rail-reading">{reading}</p>'
    markup += f'<div class="rail-source"><b>الرتب التحليلية</b><p>ضعف الكثافة <strong>{details["density_rank"]}</strong></p><p>الفرق العددي <strong>{details["count_rank"]}</strong></p></div>'
    markup += '<div class="rail-source"><b>مصادر البيانات</b><p>السكان <small>2024</small></p><p>مسح كبار السن <small>2025</small></p><p>سجل الجهات غير الربحية <small>المركز الوطني</small></p></div></aside>'
    st.markdown(markup,unsafe_allow_html=True)
