"""Regional dashboard styling and escaped markup; no indicator calculations."""
from html import escape
from .presentation import DENSITY

# SnowUI's light dashboard shell, adapted to the existing Arabic content.
# Kept in the regional page only; no global Streamlit theme or data changes.
CSS = '''<style>
:root {--fg:#1C1C1C;--muted:#60646C;--line:#E9EAED;--panel:#F7F9FB;--teal:#147D70;--red:#B84E47;}
.stApp {background:#FFFFFF;color:var(--fg);font-family:Tahoma,Arial,sans-serif;}
[data-testid="stHeader"] {display:none;}
[data-testid="stToolbar"] {visibility:hidden;}
[data-testid="stSidebar"] {display:none;}
[data-testid="stMain"] {direction:rtl;text-align:right;margin-right:202px;width:calc(100% - 202px);max-width:calc(100% - 202px);}
[data-testid="stMainBlockContainer"] {max-width:1600px;padding:2.2rem 28px 32px;}
.stApp:before {content:'';position:fixed;inset:0 0 0 auto;width:202px;background:#FFF;border-left:1px solid var(--line);z-index:50;pointer-events:none;}
h1,h2,h3,p,label,[data-testid="stDataFrame"] {font-family:Tahoma,Arial,sans-serif;text-align:right;}
h1,h2,h3,[data-testid="stMarkdownContainer"],[data-testid="stWidgetLabel"],label {color:var(--fg)!important;}
h1 {font-size:22px!important;font-weight:600!important;padding:16px 0 8px!important;}
h3 {font-size:14px!important;font-weight:600!important;}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p {color:var(--muted)!important;font-size:11px;line-height:1.85;}
[data-testid="stVerticalBlock"] {gap:12px;}
.brand {position:fixed;top:32px;right:22px;width:160px;z-index:51;font-family:Tahoma,Arial;}
.brand-name {font-size:24px;font-weight:700;line-height:1.4;color:#1C1C1C;}
.brand-sub {font-size:10px;line-height:1.9;color:#60646C;margin-top:6px;}
.st-key-top_nav {position:fixed;top:140px;right:14px;width:174px;z-index:51;}
.st-key-top_nav:before {content:'لوحات التحليل';display:block;font-size:11px;color:#737781;padding:0 10px 14px;}
.st-key-top_nav [data-testid="stHorizontalBlock"] {flex-direction:column;gap:6px;}
.st-key-top_nav [data-testid="stColumn"] {width:100%!important;flex:1 1 100%!important;}
[data-testid="stPageLink"] a {background:transparent;border:0;border-radius:8px;padding:9px 12px;color:#1C1C1C!important;justify-content:flex-start;transition:background .16s ease;}
[data-testid="stPageLink"] a:hover,[data-testid="stPageLink"] a:focus-visible {background:#F1F2F4;}
.st-key-top_nav [data-testid="stColumn"]:first-child a {background:#F1F2F4;font-weight:600;border-right:3px solid #1C1C1C;}
.dashboard-crumb {font-size:11px;color:#737781;padding:3px 0 17px;border-bottom:1px solid var(--line);}
.dashboard-crumb b {font-weight:400;color:#1C1C1C;margin-right:10px;}
.sidebar-note {position:fixed;bottom:24px;right:24px;width:154px;z-index:51;color:#737781;font-size:10px;line-height:1.9;}
.sidebar-note strong {display:block;color:#41464F;font-size:11px;margin-bottom:4px;}
.react-aria-ComboBox > [role="group"],[data-baseweb="select"] > div {background:#F7F9FB!important;border:1px solid #E5E7EB!important;border-radius:8px!important;color:#1C1C1C!important;}
.react-aria-ComboBox input,.react-aria-ComboBox button,[data-testid="stSelectbox"] input,[data-testid="stSelectbox"] [role="combobox"] {background:transparent!important;color:#1C1C1C!important;}
[role="listbox"],[data-baseweb="popover"] {background:#FFF!important;color:#1C1C1C!important;}
[role="option"] {background:#FFF;color:#1C1C1C;}
[role="option"][aria-selected="true"] {background:#E8EEF8!important;}
[data-testid="stRadio"] [role="radiogroup"] {gap:6px;}
[data-testid="stRadio"] [role="radiogroup"] label {border:1px solid transparent;border-radius:8px;padding:9px 12px;background:#F7F9FB;}
[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {background:#EDEDFA;border-color:#D8D8EE;}
label:has(input[role="switch"]) > div:first-of-type {direction:ltr!important;}
[data-testid="stExpander"] {background:#F7F9FB;border:0;border-radius:12px;}
[data-testid="stExpander"] summary {color:#1C1C1C!important;}
[data-testid="stAlert"] {background:#EAF3FA;color:#2E455B;border:0;border-radius:12px;}
.st-key-map_surface,.st-key-insight_surface,.st-key-ranking_surface,.st-key-comparison_surface,.st-key-table_surface {background:var(--panel);border:0!important;border-radius:16px!important;box-shadow:none;}
.st-key-insight_surface {background:#FFF;border:1px solid #E9EAED!important;}
.kpi-grid {display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px;margin:8px 0 16px;direction:rtl;}
.kpi {background:#EDEDFA;border:0;border-radius:16px;padding:20px;min-width:0;font-family:Tahoma,Arial;}
.kpi:nth-child(even) {background:#E6F1FD;}
.kpi-label {color:#33383F;font-size:11px;line-height:1.7;min-height:20px;}
.kpi-number {font-size:clamp(20px,2.05vw,30px);font-weight:600;color:#1C1C1C;margin:14px 0 8px;direction:ltr;text-align:right;white-space:nowrap;}
.kpi-foot {font-size:10px;color:#5C626C;line-height:1.7;}
.section-kicker {font-size:10px;font-weight:400;color:#6F7580;line-height:1.8;}
.map-heading {display:flex;align-items:center;justify-content:space-between;gap:12px;margin:7px 0;}
.map-heading h2 {font-size:16px;font-weight:600;margin:0;}
.map-heading .tag {font-size:10px;color:#555D68;background:#FFF;padding:5px 9px;border-radius:6px;white-space:nowrap;}
.color-guide {display:flex;gap:14px;flex-wrap:wrap;padding:8px 0;color:#515965;font-size:10px;}
.dot {display:inline-block;width:7px;height:7px;border-radius:50%;margin-left:5px;}
.insight-heading {display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:7px;}
.insight-heading h2 {margin:6px 0;font-size:24px;font-weight:600;}
.status-badge {font:10px Tahoma;padding:6px 8px;border:1px solid currentColor;border-radius:7px;white-space:nowrap;}
.main-indicator {padding:16px 0 12px;border-bottom:1px solid #E9EAED;margin-bottom:14px;}
.gap-label {font-size:11px;color:#535B65;}
.gap-value {font-family:Tahoma,Arial;font-size:44px;font-weight:600;direction:ltr;text-align:right;letter-spacing:-.025em;margin:8px 0;}
.gap-unit {font-size:10px;color:#616974;line-height:1.8;}
.mini-grid {display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:4px 0 15px;}
.mini {padding:12px;background:#F7F9FB;border:0;border-radius:10px;}
.mini-label {font-size:10px;color:#626975;}
.mini-value {font-size:17px;font-weight:600;color:#1C1C1C;margin-top:8px;direction:ltr;text-align:right;}
.panel-section {font-size:11px;font-weight:600;color:#30363E;margin:16px 0 10px;}
.compare-line {display:flex;justify-content:space-between;color:#606875;font-size:10px;margin:7px 0;gap:10px;}
.compare-line b {color:#30363E;font-size:12px;font-variant-numeric:tabular-nums;direction:ltr;}
.track {height:5px;border-radius:8px;background:#EEF0F3;overflow:hidden;margin-bottom:10px;}
.track span {height:100%;display:block;border-radius:8px;}
.density-grid {display:grid;grid-template-columns:1fr 1fr 1fr;gap:5px;margin-top:8px;}
.density-cell {padding:10px 4px;background:#F7F9FB;border-radius:8px;text-align:center;}
.density-cell span {display:block;font-size:9px;color:#606875;}
.density-cell b {display:block;margin-top:7px;font-size:16px;direction:ltr;color:#1C1C1C;}
.analysis-copy {color:#515965;font-size:11px;line-height:1.95;border-right:2px solid #B0C9BD;padding:0 10px;margin:10px 0 2px;}
.subtle {color:#626975;font-size:10px;line-height:1.8;}
.design-credit {color:#626975;font-size:10px;line-height:1.8;margin:18px 0;}
.design-credit a {color:#515965;}
@media(max-width:1250px) and (min-width:951px) {.kpi-grid {gap:10px;}.kpi {padding:15px 12px;}.kpi-number {font-size:22px;}}
@media(max-width:950px) {
 .stApp:before,.sidebar-note {display:none;}
 [data-testid="stMain"] {margin-right:0;width:100%;max-width:100%;}
 .brand {position:static;width:auto;}.st-key-top_nav {position:static;width:auto;}
 .st-key-top_nav:before {display:none;}
 .st-key-top_nav [data-testid="stHorizontalBlock"] {flex-direction:row;}
 .st-key-top_nav [data-testid="stColumn"] {width:auto!important;flex:1 1 0!important;}
 .kpi-grid {grid-template-columns:repeat(3,minmax(0,1fr));}
}
@media(max-width:750px) {
 [data-testid="stHorizontalBlock"] {flex-direction:column!important;}
 [data-testid="stColumn"] {width:100%!important;flex:1 1 100%!important;min-width:0!important;}
 .st-key-top_nav [data-testid="stHorizontalBlock"] {flex-direction:row!important;gap:4px;}
 .st-key-top_nav [data-testid="stColumn"] {width:auto!important;flex:1 1 0!important;}
 .st-key-top_nav [data-testid="stPageLink"] a {font-size:10px;padding:9px 6px;}
 .kpi-grid {grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;}
 .kpi:last-child {grid-column:1/-1;}.kpi {padding:15px;}.kpi-number {font-size:23px;}
 [data-testid="stMainBlockContainer"] {padding:2rem 16px;}
 .map-heading h2 {font-size:14px;}.map-heading .tag {font-size:9px;}
}
</style>'''

def kpi_cards(items):
    return '<div class="kpi-grid">' + ''.join(
        f'<div class="kpi"><div class="kpi-label">{escape(label)}</div><div class="kpi-number">{escape(value)}</div><div class="kpi-foot">{escape(foot)}</div></div>'
        for label, value, foot in items) + '</div>'

def status(details):
    # A neutral badge means the density difference rounds to zero in the display;
    # it adds no tolerance to the calculations, rankings or color domain.
    if round(details['density_gap'], 2) == 0:
        return 'قريب من المرجع', '#626975'
    return ('أقل من المرجع', '#B84E47') if details['density_gap'] > 0 else ('أعلى من المرجع', '#147D70')

def insight_head(details, m, basis, color):
    label, badge_color = status(details)
    return f'''<div class="section-kicker">رؤى المنطقة المختارة</div>
<div class="insight-heading"><h2>{escape(details['region'])}</h2><span class="status-badge" style="color:{badge_color}">{label}</span></div>
<div class="main-indicator"><div class="gap-label">{escape(m['title'])}</div><div class="gap-value" style="color:{color}">{details['value']:+,.2f}</div><div class="gap-unit">{escape(m['value_unit'])} · {'الوطني − المنطقة' if basis == DENSITY else 'الفعلي − المرجعي'}</div></div>'''

def mini_cards(row, details, pop_col, elderly_col):
    items = [('السكان · نسمة', f'{int(row[pop_col]):,}'), ('الجهات · جهة', f'{details["actual"]:,}'),
             ('كبار السن · فرد', f'{int(row[elderly_col]):,}'), ('رتبة العرض · من 13', str(details['rank']))]
    return '<div class="mini-grid">' + ''.join(f'<div class="mini"><div class="mini-label">{label}</div><div class="mini-value">{value}</div></div>' for label,value in items) + '</div>'

def count_comparison(details, color):
    maximum = max(details['actual'], details['expected'], 1)
    actual_width, expected_width = details['actual']/maximum*100, details['expected']/maximum*100
    return f'''<div class="panel-section">الفعلي مقابل المرجعي <span class="subtle">· جهة</span></div>
<div class="compare-line"><span>العدد الفعلي</span><b>{details['actual']:,}</b></div><div class="track"><span style="width:{actual_width}%;background:{color}"></span></div>
<div class="compare-line"><span>العدد المرجعي</span><b>{details['expected']:,.2f}</b></div><div class="track"><span style="width:{expected_width}%;background:#879DB7"></span></div>
<div class="compare-line"><span>فرق الجهات</span><b>{details['count_gap']:+,.2f}</b></div>'''

def density_cells(details, unit, color):
    return f'''<div class="panel-section">الكثافة في سياقها الوطني</div><div class="density-grid">
<div class="density-cell"><span>المنطقة</span><b>{details['density']:,.2f}</b></div>
<div class="density-cell"><span>المعدل الوطني</span><b>{details['national']:,.2f}</b></div>
<div class="density-cell"><span>فجوة الكثافة</span><b style="color:{color}">{details['density_gap']:+,.2f}</b></div>
</div><div class="subtle" style="margin-top:7px">{escape(unit)} · الفجوة = الوطني − المنطقة</div>'''
