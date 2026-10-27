from html import escape
import streamlit as st
from src.data import load_regional_bundle, METRICS, POP, ORGS, ELDERLY
from src.presentation import prepare_regional, fields, row_details, interpretation, BASES, DENSITY, ELDERLY_NOTE
from src.regional_views import (map_figure, ranking_figure, comparison_figure, results_table,
                                selected_region, gap_color, density_comparison)
from src.regional_ui import CSS, kpi_cards, insight_head, mini_cards, count_comparison, density_cells, status

from src.snow_shell import shell, insight_rail
shell('التحليل الإقليمي')
st.title('التحليل الإقليمي')
try:
    approved, boundaries = load_regional_bundle()
    frame = prepare_regional(approved)
except Exception as exc:
    st.error(f'توقف اعتماد النتائج: فشل التحقق من البيانات أو الحسابات. يلزم مراجعة الاختلاف قبل العرض: {exc}')
    st.stop()

with st.container(key='analysis_filters'):
    st.caption('إعدادات التحليل')
    metric = st.radio('المؤشر النشط', list(METRICS), format_func=lambda key: METRICS[key]['label'], key='metric')
    basis = st.selectbox('معيار الترتيب والعرض', list(BASES), format_func=lambda key: BASES[key], key='basis')
m = fields(metric, basis)
if metric == 'elderly':
    st.caption(ELDERLY_NOTE)
st.markdown(kpi_cards([
    ('إجمالي السكان', f'{frame[POP].sum():,}', 'نسمة · بيانات 2024'),
    ('الجهات غير الربحية', f'{frame[ORGS].sum():,}', 'جهة · كامل السجل المعتمد'),
    ('كبار السن', f'{frame[ELDERLY].sum():,}', 'فرد بعمر 60+ · بيانات 2025'),
    ('مناطق أقل من المرجع', f'{(frame[m["density_gap"]] > 0).sum()} / 13', 'كثافة أقل من المعدل الوطني'),
]), unsafe_allow_html=True)

from src.snow_charts import comparison_overview, density_overview, distribution_overview
with st.container(key='snow_overview'):
    main_chart, summary_chart = st.columns([3.3, 1], gap='medium')
    with main_chart:
        with st.container(border=True, key='overview_line'):
            st.subheader('توزيع الجهات · الفعلي والمرجعي')
            st.plotly_chart(comparison_overview(frame, metric), key=f'overview_line_{metric}', width='stretch', config={'displayModeBar': False})
    with summary_chart:
        with st.container(border=True, key='overview_summary'):
            st.subheader('الكثافة الوطنية')
            st.markdown(f"<div class='rail-number'>{frame[m['national']].iloc[0]:,.2f}</div>", unsafe_allow_html=True)
            st.caption(m['unit'])
            rows = ''.join(f"<div class='snow-density-row'><span>{escape(name)}</span><b>{value:,.2f}</b></div>" for name, value in frame[['Region', m['density']]].itertuples(index=False, name=None))
            st.markdown(rows, unsafe_allow_html=True)
    bars, donut = st.columns(2, gap='medium')
    with bars:
        with st.container(border=True, key='overview_bars'):
            st.subheader('كثافة الجهات حسب المنطقة')
            st.plotly_chart(density_overview(frame, metric), key=f'overview_bars_{metric}', width='stretch', config={'displayModeBar': False})
    with donut:
        with st.container(border=True, key='overview_donut'):
            st.subheader('توزيع الجهات غير الربحية')
            st.plotly_chart(distribution_overview(frame), key='overview_donut_chart', width='stretch', config={'displayModeBar': False})

if 'region' not in st.session_state:
    st.session_state.region = 'الرياض'
chooser, map_view = st.columns([2, 1], gap='large', vertical_alignment='bottom')
with chooser:
    st.selectbox('اختر المنطقة', frame.Region.tolist(), key='region')
with map_view:
    compact = st.toggle('ملاءمة الخريطة للشاشات الصغيرة', value=False, key='compact_map',
        help='يعرض المملكة كاملة في مساحة الهاتف. يمكن السحب والتكبير داخل الخريطة أيضًا.')
region = st.session_state.region
details = row_details(frame, metric, region, basis)
map_key = f'region_map_{metric}_{basis}_{compact}'

def map_selected():
    st.session_state.region = selected_region(st.session_state.get(map_key), st.session_state.region)

insight_rail(frame, details, m, metric, basis)
map_col, detail_col = st.columns([3.3, 1], gap='medium')
with map_col:
    with st.container(border=True, key='map_surface'):
        st.markdown(f'''<div class="section-kicker">الاستكشاف الجغرافي</div><div class="map-heading"><h2>{escape(METRICS[metric]['label'])}</h2><span class="tag">المملكة · 13 منطقة</span></div>''', unsafe_allow_html=True)
        st.caption(m['title']+' · '+m['value_unit'])
        map_chart = map_figure(frame, boundaries, metric, region, basis, compact)
        map_chart.update_layout(height=270, map_zoom=2.8 if compact else 3.25)
        st.plotly_chart(map_chart, key=map_key,
            on_select=map_selected, selection_mode='points', width='stretch',
            config={'displayModeBar': False, 'scrollZoom': False, 'locale': 'ar'})
        st.markdown('''<div class="color-guide"><span><i class="dot" style="background:#B84E47"></i>أقل من المرجع</span><span><i class="dot" style="background:#DDE1E7"></i>عند المرجع</span><span><i class="dot" style="background:#147D70"></i>أعلى من المرجع</span></div>''', unsafe_allow_html=True)
        st.caption('الفجوة = الوطني − المنطقة؛ الموجب كثافة أقل، والسالب كثافة أعلى.' if basis == DENSITY else 'فرق الجهات = الفعلي − المرجعي؛ السالب أقل عددًا، والموجب أعلى منه.')
        st.caption('اضغط منطقة لاختيارها · الإطار الداكن يحدد الاختيار دون إخفاء اللون · اسحب أو انقر مرتين للتكبير. نطاق الألوان ثابت لكل قياس ومتماثل حول الصفر.')
with detail_col:
    with st.container(border=True, key='insight_surface'):
        st.subheader('كثافة الجهات')
        st.caption(region)
        st.markdown(density_cells(details, m['unit'], status(details)[1]), unsafe_allow_html=True)
        st.plotly_chart(density_comparison(details, metric), key=f'density_card_{metric}', width='stretch', config={'displayModeBar': False})
        st.caption('المعدل الوطني')
        st.markdown(f"<div class='rail-number'>{details['national']:,.2f}</div>", unsafe_allow_html=True)

st.caption('الرتبة 1 لأضعف كثافة في العرض النسبي، أو لأكثر فرق عددي سالب في عرض Excel. شارة «قريب» تعني أن فجوة الكثافة تُقرّب إلى صفر عند منزلتين؛ لا تغيّر الرتب أو الحسابات.')
left, right = st.columns(2, gap='medium')
with left:
    with st.container(border=True, key='ranking_surface'):
        st.subheader('ترتيب المناطق')
        st.caption(BASES[basis]+' · الرتبة 1 في أعلى الرسم')
        st.plotly_chart(ranking_figure(frame, metric, region, basis).update_layout(height=330), key=f'ranking_{metric}_{basis}', width='stretch', config={'displayModeBar': False})
with right:
    with st.container(border=True, key='comparison_surface'):
        st.subheader('الفعلي مقابل المرجعي')
        st.caption('مقارنة أعداد بوحدة جهة · الترتيب يطابق معيار العرض المختار')
        st.plotly_chart(comparison_figure(frame, metric, region, basis).update_layout(height=330), key=f'comparison_{metric}_{basis}', width='stretch', config={'displayModeBar': False})

with st.container(border=True, key='table_surface'):
    st.subheader('نتائج المناطق الثلاث عشرة')
    st.caption('الترتيب التحليلي: '+BASES[basis]+'. يمكنك فرز الأعمدة؛ تبقى أعمدة الرتب التحليلية ثابتة.')
    table = results_table(frame, metric, basis)
    formats = {col: ('{:,.0f}' if col in ['السكان', 'الجهات (جهة)', 'كبار السن (60+)', 'رتبة ضعف الكثافة', 'رتبة الفرق العددي (Excel)'] else '{:,.2f}')
               for col in table.columns if col != 'المنطقة'}
    styled = table.style.format(formats).set_properties(**{'background-color':'#F7F9FB','color':'#1C1C1C','font-family':'Tahoma'})
    st.dataframe(styled, hide_index=True, width='stretch', height=495)
    st.caption('دقة الحسابات كاملة؛ التقريب للعرض فقط. العدد المرجعي تناسبي وليس عدد جهات واجب إنشاؤها.')

with st.expander('قراءة تحليلية مفصلة للمنطقة'):
    st.markdown(interpretation(details, metric))
with st.expander('المنهجية والمصادر'):
    st.write('فجوة الكثافة = المعدل الوطني − كثافة المنطقة. كثافة المنطقة = إجمالي جهاتها ÷ عدد السكان المرجعي × أساس المعدل. المعدل الوطني = إجمالي الجهات ÷ إجمالي السكان المرجعي × أساس المعدل.')
    st.write('أساس المعدل السكاني: 100,000 نسمة؛ أساس كبار السن: 10,000 فرد بعمر 60+. الفرق النسبي = فجوة الكثافة ÷ المعدل الوطني × 100. الرتبة النسبية تنازلية حسب فجوة الكثافة، والتعادل يأخذ أصغر رتبة.')
    st.write('فرق الجهات = الفعلي − المرجعي. الرتب النسبية والعددية مستقلتان.')
    st.markdown('[المركز الوطني لتنمية القطاع غير الربحي](https://ncnp.gov.sa/ar/taxonomy/term/35)')
    st.markdown('[بيانات السعودية](https://datasaudi.sa/ar)')
    st.markdown('[الهيئة العامة للإحصاء](https://www.stats.gov.sa/ar)')
    st.caption('إسناد الخريطة: geoBoundaries / © OpenStreetMap contributors · ODbL 1.0.')
    st.markdown('[الإسناد والترخيص](https://www.openstreetmap.org/copyright)')

st.markdown('<div class="design-credit">التصميم البصري مقتبس ومكيّف من <a href="https://www.figma.com/community/file/1210542873091115123/dashboard-ui-kit-dashboard-free-admin-dashboard">SnowUI / Dashboard UI Kit — ByeWind</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. عُدّل لواجهة عربية وبيانات وخريطة فَجْوَة.</div>', unsafe_allow_html=True)

