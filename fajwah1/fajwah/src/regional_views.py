"""Presentation only; the approved results stay unchanged."""
import plotly.graph_objects as go
import json
from urllib.parse import quote
from .data import METRICS, POP, ORGS, ELDERLY
from .regions import REGIONS
from .presentation import fields, ensure_prepared, DENSITY

TEAL, RED, INK = '#147D70', '#B84E47', '#1C1C1C'
SCALE = [[0, RED], [.5, '#DDE1E7'], [1, TEAL]]

def ordered(frame, metric, basis=DENSITY):
    frame, m = ensure_prepared(frame), fields(metric, basis)
    return frame.sort_values([m['value'], 'Region'], ascending=[basis != DENSITY, True])

def gap_color(value, basis=DENSITY):
    return RED if (value > 0 if basis == DENSITY else value < 0) else TEAL

def selected_region(event, fallback):
    points = (event or {}).get('selection', {}).get('points', [])
    inverse = {code: name for name, code in REGIONS.items()}
    for point in reversed(points):
        if point.get('location') in inverse:
            return inverse[point['location']]
    return fallback

def style(fig, height=490):
    fig.update_layout(template='plotly_white', height=height, font=dict(family='Tahoma, Arial', color=INK, size=12),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=15, r=15, t=35, b=30), legend=dict(orientation='h', y=1.15, x=1, xanchor='right'))
    fig.update_xaxes(tickfont=dict(color='#626975'), gridcolor='#E9EAED', linecolor='#DDE1E7')
    fig.update_yaxes(tickfont=dict(color='#626975'), gridcolor='#E9EAED', linecolor='#DDE1E7')
    return fig

def map_figure(frame, geo, metric, region, basis=DENSITY, compact=False):
    frame, m = ensure_prepared(frame), fields(metric, basis)
    limit = max(abs(frame[m['value']]).max(), 1e-6)
    fig = go.Figure(go.Choroplethmap(
        geojson=geo, featureidkey='id', locations=frame.region_id.tolist(),
        z=frame[m['value']].tolist(), zmin=-limit, zmax=limit, zmid=0,
        colorscale=list(reversed([[1-p, color] for p, color in SCALE])) if basis == DENSITY else SCALE,
        customdata=frame[['Region', ORGS, m['expected'], m['active_rank'], m['density'], m['national']]].to_numpy(),
        marker_line_color='#FFFFFF', marker_line_width=1.1,
        colorbar=dict(title=dict(text=m['value_unit'], side='top', font=dict(size=10)),
            thickness=10, len=.9, orientation='h', y=0, yanchor='top', tickformat=',.2f'),
        hovertemplate='<b>%{customdata[0]}</b><br>'+m['title']+': %{z:+,.2f}<br>'+m['value_unit']+
            '<br>الفعلي: %{customdata[1]:,} جهة<br>المرجعي: %{customdata[2]:,.2f} جهة<br>الرتبة: %{customdata[3]}'
            '<br>كثافة المنطقة: %{customdata[4]:,.2f}<br>المعدل الوطني: %{customdata[5]:,.2f}<br>'+m['unit']+'<extra></extra>',
        selectedpoints=[frame.Region.tolist().index(region)],
        selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=1))))
    row = frame.loc[frame.Region == region].iloc[0]
    fig.add_trace(go.Choroplethmap(geojson=geo, featureidkey='id', locations=[row.region_id], z=[0],
        colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']], showscale=False,
        marker_line_color='#292D38', marker_line_width=3.5, hoverinfo='skip', showlegend=False))
    background_map = {'version': 8, 'sources': {}, 'layers': [
        {'id': 'fajwah-background', 'type': 'background', 'paint': {'background-color': '#F7F9FB'}}]}
    # Keep the style local while avoiding object-style initialization differences
    # in Streamlit's packaged Plotly renderer (which can interrupt event binding).
    style_url = 'data:application/json;charset=utf-8,' + quote(json.dumps(background_map))
    fig.update_layout(map=dict(style=style_url, center=dict(lat=24.2, lon=45), zoom=2.95 if compact else 4.05),
                      clickmode='event+select', uirevision=f'saudi-regions-{compact}',
                      hoverlabel=dict(bgcolor='#FFFFFF', bordercolor='#DDE1E7', font=dict(color=INK,size=13), align='right'))
    style(fig, 460 if compact else 620)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=60))
    return fig

def ranking_figure(frame, metric, region, basis=DENSITY):
    data, m = ordered(frame, metric, basis), fields(metric, basis)
    limit = max(abs(data[m['value']]).max(), 1e-6)
    inside = [abs(v) > limit * .25 for v in data[m['value']]]
    fig = go.Figure(go.Bar(x=data[m['value']].tolist(), y=data.Region.tolist(), orientation='h',
        text=[f'{v:+,.2f}' for v in data[m['value']]],
        textposition=['inside' if flag else 'outside' for flag in inside], insidetextanchor='end',
        textfont=dict(color=['#FFFFFF' if flag else INK for flag in inside]), cliponaxis=False,
        marker=dict(color=[gap_color(v, basis) for v in data[m['value']]],
            line=dict(color=INK, width=[2 if name == region else 0 for name in data.Region])),
        hovertemplate='%{y}<br>'+m['title']+': %{x:+,.2f}<br>'+m['value_unit']+'<extra></extra>'))
    fig.update_yaxes(autorange='reversed', title=None)
    fig.update_xaxes(title=m['title']+' · '+m['value_unit'], tickformat=',.2f', zeroline=True, zerolinecolor=INK)
    style(fig)
    fig.update_layout(margin=dict(l=65, r=65, t=25, b=70))
    return fig

def comparison_figure(frame, metric, region, basis=DENSITY):
    data, m = ordered(frame, metric, basis), fields(metric, basis)
    fig = go.Figure()
    for col, label, color in [(ORGS, 'العدد الفعلي', TEAL), (m['expected'], 'العدد المرجعي', '#879DB7')]:
        fig.add_bar(x=data[col].tolist(), y=data.Region.tolist(), name=label, orientation='h',
            marker=dict(color=color, line=dict(color=INK, width=[2 if name == region else 0 for name in data.Region])),
            hovertemplate='%{y}<br>'+label+': %{x:,.2f}<extra></extra>')
    fig.update_layout(barmode='group')
    fig.update_yaxes(autorange='reversed', title=None)
    fig.update_xaxes(title='عدد الجهات (جهة)', rangemode='tozero', tickformat=',.0f')
    return style(fig)

def results_table(frame, metric, basis=DENSITY):
    m = fields(metric, basis)
    return ordered(frame, metric, basis)[['Region', m['density_rank'], m['rank'], m['density_gap'],
        m['density'], m['national'], ORGS, m['expected'], m['gap'], POP, ELDERLY]].rename(columns={
        m['density_rank']: 'رتبة ضعف الكثافة', m['rank']: 'رتبة الفرق العددي (Excel)',
        'Region': 'المنطقة', POP: 'السكان', ORGS: 'الجهات (جهة)', ELDERLY: 'كبار السن (60+)',
        m['expected']: 'المرجع العددي (جهة)', m['gap']: 'فرق الجهات (جهة)',
        m['density']: 'كثافة المنطقة · '+m['unit'], m['national']: 'المعدل الوطني · '+m['unit'],
        m['density_gap']: 'فجوة الكثافة · '+m['unit']}).reset_index(drop=True)

def density_comparison(details, metric):
    fig = go.Figure(go.Bar(x=[details['density'], details['national']],
        y=['المنطقة', 'المعدل الوطني'], orientation='h', marker_color=[gap_color(details['density_gap']), '#879DB7'],
        text=[f'{details["density"]:,.2f}', f'{details["national"]:,.2f}'], textposition='auto',
        hovertemplate='%{y}: %{x:,.2f}<br>'+fields(metric)['unit']+'<extra></extra>'))
    fig.update_xaxes(title=None, rangemode='tozero', tickformat=',.1f')
    fig.update_yaxes(autorange='reversed')
    style(fig, 155)
    fig.update_layout(margin=dict(l=5,r=5,t=3,b=25))
    return fig
