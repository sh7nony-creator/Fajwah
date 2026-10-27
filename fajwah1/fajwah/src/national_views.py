"""Descriptive charts and deterministic text; no cross-table aggregation."""
import plotly.graph_objects as go
from .national_data import CATALOG

TEAL, GOLD, INK = '#95A4FC', '#A8C5DA', '#1C1C1C'

def national_figure(selected, key):
    spec = CATALOG[key]
    percent = spec.unit == 'نسبة مئوية'
    suffix = '%' if percent else ' فردًا'
    fig = go.Figure(go.Bar(x=selected.value.tolist(), y=selected.category.tolist(), orientation='h',
        marker_color=[TEAL if i%2 == 0 else GOLD for i in range(len(selected))],
        text=[f'{v:,.1f}%' if percent else f'{v:,.0f}' for v in selected.value],
        textposition='auto', hovertemplate='%{y}<br>%{x:,.1f}'+suffix+'<extra></extra>' if percent else
        '%{y}<br>%{x:,.0f} فردًا<extra></extra>'))
    fig.update_layout(template='plotly_white', height=370 if len(selected) <= 5 else 420,
        font=dict(family='Tahoma, Arial', color=INK, size=13),
        margin=dict(l=10,r=15,t=15,b=55), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_yaxes(autorange='reversed', automargin=True, tickfont=dict(color=INK), title=None)
    fig.update_xaxes(title='النسبة المنشورة (%)' if percent else 'عدد الأفراد السعوديين (فرد)',
        range=[0,100] if percent else None, rangemode='tozero', tickformat='.0f' if percent else ',.0f',
        ticksuffix='%' if percent else '', tickfont=dict(color=INK))
    return fig

def describe_national(selected, key):
    spec = CATALOG[key]
    if key == 'digital':
        values = '، '.join(f'{row.category}: {row.value:,.1f}%' for row in selected.itertuples())
        return f'القيم المنشورة للفئة المختارة هي: {values}. كل بُعد يُعرض مستقلاً؛ لا تُجمع النسب ولا يُستنتج منها تسلسل استخدام.'
    max_value = selected.value.max()
    leaders = selected.loc[selected.value == max_value, 'category'].tolist()
    labels = '، '.join(leaders)
    amount = f'{max_value:,.1f}%' if spec.unit == 'نسبة مئوية' else f'{max_value:,.0f} فردًا'
    sentence = f'أكبر فئة في التوزيع المعروض للفئة المختارة هي «{labels}» بقيمة {amount}.'
    if spec.unit == 'فرد':
        sentence += f' مجموع الأفراد في هذا التوزيع {selected.value.sum():,.0f} فردًا؛ هذا إجمالي الجدول للفئة المختارة وليس حجم عينة موثقًا.'
    else:
        sentence += ' النسب من عمود المصدر مباشرة، وليست متوسطات للجنسين أو الجنسيات.'
    return sentence + ' هذه قراءة وصفية لا تفسر أسباب النتيجة.'

def national_table(selected):
    return selected[['category','value','unit','year','sheet','excel_cell']].rename(columns={
        'category':'الفئة', 'value':'القيمة', 'unit':'الوحدة', 'year':'السنة', 'sheet':'ورقة المصدر', 'excel_cell':'خلية Excel'})
