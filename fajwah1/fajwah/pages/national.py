import streamlit as st
from src.national_data import (CATALOG, NATIONALITIES, SEXES, SOURCE, load_national_table, select_values)
from src.national_views import national_figure, describe_national, national_table

from src.snow_shell import shell
shell('المؤشرات الوطنية')
st.title('المؤشرات الوطنية')
st.caption('إحصاءات وطنية مجمعة للأفراد بعمر 60 سنة فأكثر · كل مؤشر يُقرأ ضمن مجتمعه المرجعي ووحدته')
section = st.selectbox('انتقل إلى قسم', list(CATALOG), format_func=lambda key: CATALOG[key].label, key='national_section')
spec = CATALOG[section]
st.subheader(spec.label)
st.write(spec.description)
filters = st.columns(2)
with filters[0]:
    if spec.saudi_only:
        nationality = 'saudi'
        st.info('نطاق جدول السكن: السعوديون فقط. لا تتوفر بيانات جميع الجنسيات أو غير السعوديين لهذا الجدول.')
    else:
        nationality = st.selectbox('الجنسية', list(NATIONALITIES), format_func=lambda key: NATIONALITIES[key], key='national_nationality')
with filters[1]:
    sex = st.selectbox('الجنس', list(SEXES), format_func=lambda key: SEXES[key], key='national_sex')
try:
    raw = load_national_table(section)
    selected = select_values(raw, section, nationality, sex)
except Exception as exc:
    st.error(f'توقف عرض هذا المؤشر لحين مراجعة بياناته: {exc}')
    st.stop()

cards = st.columns(4)
for card, label, value in zip(cards, ['سنة المسح', 'العمر', 'نطاق الفئة', 'وحدة القياس'],
    [str(spec.year), '60 سنة فأكثر', NATIONALITIES[nationality], spec.unit]):
    card.metric(label, value)
st.caption(f'الفئة المعروضة: {NATIONALITIES[nationality]} · {SEXES[sex]} · نطاق وطني، دون تفصيل إقليمي')
st.caption(f'المصدر: {SOURCE} · {spec.sheet} · رقم الجدول داخل الورقة: {spec.table_number}')

chart, explanation = st.columns([1.8, 1], gap='medium')
with chart:
    with st.container(border=True):
        st.plotly_chart(national_figure(selected, section), key=f'national_plot_{section}',
            width='stretch', config={'displayModeBar': False})
        st.caption(f'القيم الأصلية المنشورة · {spec.unit} · {NATIONALITIES[nationality]} · {SEXES[sex]} · {spec.year}')
with explanation:
    with st.container(border=True):
        st.subheader('قراءة وصفية')
        st.write(describe_national(selected, section))
        st.caption(spec.caveat)
        st.caption('ألوان الأعمدة للتمييز البصري فقط؛ لا تمثل حكمًا على جودة أو سوء الحالة.')

with st.expander('القيم المعروضة ومواقعها في Excel'):
    table = national_table(selected)
    st.dataframe(table.style.format({'القيمة':'{:,.1f}' if spec.unit == 'نسبة مئوية' else '{:,.0f}', 'السنة':'{:.0f}'}),
        hide_index=True, width='stretch')
    st.caption('القيم المئوية مخزنة كما في المصدر (مثل 46.5 تعني 46.5%)؛ لا تُضرب في 100. الفراغ لا يُعرض بصفر. الصفر الصريح في المصدر يبقى صفرًا.')
with st.expander('حدود التحليل والمصادر'):
    st.write('أحجام العينات وأوزانها غير مرفقة؛ تختلف المقامات بحسب الجدول، ولا تُستنتج أعداد أفراد من النسب.')
    st.write(f'المصدر المحلي: elderly_by_region_2025.xlsx.xlsx · الورقة {spec.sheet} · {spec.year}. {SOURCE}.')
    st.write('أُخذت النسب من أعمدة الإجمالي أو الفئة المختارة مباشرة دون متوسط حسابي بين الجنسين أو الجنسيات. لا تُجمع النسب بين الجداول. لم تُحوّل أعداد حيازة المسكن إلى نسب.')
    st.write('تحقق البرنامج من مجموع فئات التوزيعات التي تحتوي على صف إجمالي منشور مع سماح بتقريب المصدر إلى منزلة واحدة؛ ولا يفرض مجموع 100% على أبعاد الاندماج الرقمي.')
    st.write(spec.caveat)
    st.write('لا توجد بيانات مناسبة لنوع المبنى في الجداول المفحوصة. يظهر قسم السكن حيازة المسكن فقط. كما لم يُستخدم جدول أنواع الأمراض المزمنة بسبب عدم وضوح مقامه بما يكفي؛ يعرض القسم جدول حالة المرض العام.')
    st.write('الصفحة الوطنية مستقلة عن فجوات التوزيع الإقليمية. لا تُربط هذه النسب بالمناطق، ولا تدخل معادلات الفجوة أو رتب المناطق.')
