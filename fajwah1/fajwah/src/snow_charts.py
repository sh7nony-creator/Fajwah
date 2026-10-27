"""Snow overview chart slots using existing, unmodified regional columns."""
import plotly.graph_objects as go
from .data import ORGS
from .presentation import fields

PALETTE=['#95A4FC','#BAEDBD','#1C1C1C','#B1E3FF','#A8C5DA','#A1E3CB','#C6C7F8','#8A8CD9','#C8DCEC','#DDEBCB','#7E9DB4','#C7D8CF','#DDD9F5']
def style(fig, height):
    fig.update_layout(template='plotly_white',height=height,font=dict(family='Arial, Tahoma',size=10,color='#1C1C1C'),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',margin=dict(l=15,r=10,t=28,b=25),legend=dict(orientation='h',x=1,xanchor='right',y=1.2),colorway=PALETTE)
    fig.update_xaxes(gridcolor='rgba(28,28,28,.05)',linecolor='rgba(28,28,28,.2)',tickfont=dict(color='#888',size=9))
    fig.update_yaxes(gridcolor='rgba(28,28,28,.05)',tickfont=dict(color='#888',size=9),zeroline=False)
    return fig

def comparison_overview(frame,metric):
    m=fields(metric)
    fig=go.Figure()
    for col,label,color in [(ORGS,'العدد الفعلي','#1C1C1C'),(m['expected'],'العدد المرجعي','#A8C5DA')]:
        fig.add_scatter(x=frame.Region.tolist(),y=frame[col].tolist(),name=label,mode='lines+markers',line=dict(color=color,width=2),marker=dict(size=4),hovertemplate='%{x}<br>'+label+': %{y:,.2f}<extra></extra>')
    return style(fig,245)

def density_overview(frame,metric):
    m=fields(metric)
    fig=go.Figure(go.Bar(x=frame.Region.tolist(),y=frame[m['density']].tolist(),marker_color=PALETTE,hovertemplate='%{x}<br>%{y:,.2f} '+m['unit']+'<extra></extra>'))
    fig.update_layout(bargap=.55)
    return style(fig,220)

def distribution_overview(frame):
    fig=go.Figure(go.Pie(labels=frame.Region.tolist(),values=frame[ORGS].tolist(),hole=.72,sort=False,direction='clockwise',marker=dict(colors=PALETTE,line=dict(color='#F7F9FB',width=3)),textinfo='none',hovertemplate='%{label}<br>%{value:,} جهة · %{percent}<extra></extra>'))
    style(fig,220)
    fig.update_layout(margin=dict(l=0,r=0,t=10,b=10),legend=dict(orientation='v',x=1.02,y=.5,yanchor='middle',font=dict(size=9)),showlegend=True)
    return fig
