import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="IFCT 2017 Master",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme Selection in Sidebar
theme_choice = st.sidebar.radio("🎨 Select Theme", ["Dark (Executive)", "Light (Clean)"], horizontal=True)

# Define Theme Variables with Gradients
if "Dark" in theme_choice:
    theme_css = """
        --bg-gradient: linear-gradient(135deg, #0a0b10 0%, #1c212c 100%);
        --sidebar-gradient: linear-gradient(180deg, #12141a 0%, #0a0b10 100%);
        --card-bg: rgba(26, 29, 36, 0.75);
        --text-primary: #E2E8F0;
        --text-muted: #A0AEC0;
        --accent-color: #E6C27A;
        --border-color: rgba(45, 49, 58, 0.8);
        --chart-grid: #2D313A;
    """
    chart_font = '#A0AEC0'
    chart_grid = '#2D313A'
    chart_bg = 'rgba(0,0,0,0)'
else:
    theme_css = """
        --bg-gradient: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        --sidebar-gradient: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%);
        --card-bg: rgba(255, 255, 255, 0.85);
        --text-primary: #0F172A;
        --text-muted: #475569;
        --accent-color: #B45309;
        --border-color: rgba(226, 232, 240, 0.8);
        --chart-grid: #E2E8F0;
    """
    chart_font = '#475569'
    chart_grid = '#E2E8F0'
    chart_bg = 'rgba(0,0,0,0)'

# Inject Dynamic CSS
st.markdown(f"""
<style>
    :root {{ {theme_css} }}
    
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{ 
        background: var(--bg-gradient) !important;
        background-attachment: fixed !important;
        color: var(--text-primary) !important; 
        font-family: 'Inter', sans-serif; 
    }}
    
    h1, h2, h3, h4, p, span {{ color: var(--text-primary) !important; }}
    h1, h2, h3, h4 {{ color: var(--accent-color) !important; font-weight: 600 !important; letter-spacing: 0.5px; }}
    
    div[data-testid="stMetric"] {{ 
        background: var(--card-bg) !important; 
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--border-color); 
        border-radius: 12px; 
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease-in-out, border-color 0.2s ease-in-out;
        overflow: hidden;
    }}
    div[data-testid="stMetric"]:hover {{ transform: translateY(-3px); border-color: var(--accent-color); }}
    div[data-testid="stMetricLabel"] {{ 
        color: var(--text-muted) !important; 
        font-size: 0.9rem; 
        font-weight: 500; 
        margin-bottom: 4px; 
        white-space: normal; 
        overflow-wrap: break-word; 
    }}
    div[data-testid="stMetricValue"] {{ 
        color: var(--text-primary) !important; 
        font-size: 1.4rem; 
        font-weight: 700; 
        white-space: normal; 
        overflow-wrap: break-word; 
    }}
    
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; background-color: transparent; padding-bottom: 5px; flex-wrap: wrap; }}
    .stTabs [data-baseweb="tab"] {{ background: var(--card-bg); border-radius: 6px; padding: 10px 24px; border: 1px solid var(--border-color); color: var(--text-muted); white-space: nowrap; }}
    .stTabs [aria-selected="true"] {{ background-color: var(--accent-color) !important; color: #FFFFFF !important; font-weight: 700; border-color: var(--accent-color); }}
    
    [data-testid="stSidebar"] {{ background: var(--sidebar-gradient) !important; border-right: 1px solid var(--border-color); }}
    [data-testid="stSidebarNav"] {{ background: transparent !important; }}
    hr {{ border-color: var(--border-color); opacity: 0.8; }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA PROCESSING
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("extracted_ifct_data.csv")
        code_map = {
            'A': 'Cereals & Millets', 'B': 'Grain Legumes', 'C': 'Green Leafy Veg',
            'D': 'Other Veg', 'E': 'Fruits', 'F': 'Roots & Tubers',
            'G': 'Condiments & Spices', 'H': 'Nuts & Oil Seeds', 'I': 'Sugars',
            'J': 'Mushrooms', 'K': 'Misc', 'L': 'Milk & Dairy',
            'M': 'Egg Products', 'N': 'Poultry', 'O': 'Animal Meat',
            'P': 'Marine Fish', 'Q': 'Marine Shellfish', 'R': 'Marine Mollusks',
            'S': 'Freshwater Fish'
        }
        df['Group_Code'] = df['code'].astype(str).str[0].str.upper()
        df['Group'] = df['Group_Code'].map(code_map).fillna('Other')
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        return df
    except FileNotFoundError:
        st.error("File 'extracted_ifct_data.csv' not found. Please make sure it is in the same folder.")
        return pd.DataFrame()

df = load_data()

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def format_val(item, col, unit=""):
    val = item.get(col, 0)
    err = item.get(f"{col}_e", 0)
    
    if isinstance(val, float): val = round(val, 2)
    if isinstance(err, float): err = round(err, 2)
    
    val_str = f"{int(val)}" if val == int(val) else f"{val}"
    err_str = f"{int(err)}" if err == int(err) else f"{err}"
    
    if err and float(err) != 0:
        return f"{val_str} ± {err_str} {unit}".strip()
    return f"{val_str} {unit}".strip()

def format_sum_val(item, cols, unit=""):
    val = sum(item.get(c, 0) for c in cols)
    err = math.sqrt(sum(item.get(f"{c}_e", 0)**2 for c in cols))
    
    if isinstance(val, float): val = round(val, 2)
    if isinstance(err, float): err = round(err, 2)
    
    val_str = f"{int(val)}" if val == int(val) else f"{val}"
    err_str = f"{int(err)}" if err == int(err) else f"{err}"
    
    if err and float(err) != 0:
        return f"{val_str} ± {err_str} {unit}".strip()
    return f"{val_str} {unit}".strip()

def plot_radar(values, labels, title, color):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=labels, fill='toself', name=title,
        line=dict(color=color, width=2),
        fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}",
        marker=dict(size=6)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, showticklabels=False, gridcolor=chart_grid, linecolor=chart_grid),
                   angularaxis=dict(gridcolor=chart_grid, linecolor=chart_grid)),
        paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, font=dict(color=chart_font, size=12),
        showlegend=False, margin=dict(t=50, b=50, l=50, r=50)
    )
    return fig

# -----------------------------------------------------------------------------
# 4. APP LAYOUT
# -----------------------------------------------------------------------------
if not df.empty:
    with st.sidebar:
        st.markdown("---")
        st.title("🥗 IFCT Explorer")
        st.caption(f"**Database Size:** {len(df)} curated items")
        st.markdown("---")
        
        all_groups = ["All"] + sorted(list(df['Group'].unique()))
        selected_group = st.selectbox("Filter by Category", all_groups)
        
        if selected_group != "All":
            filtered_df = df[df['Group'] == selected_group]
        else:
            filtered_df = df
            
        selected_item = st.selectbox("Select Food Item", filtered_df['name'].unique())
        st.markdown("---")
        st.info("📊 Values standard per **100g** edible portion.")

    if selected_item:
        item = df[df['name'] == selected_item].iloc[0]
        
        # Header
        c1, c2 = st.columns([3, 1])
        with c1:
            st.title(item['name'])
            st.markdown(f"<span style='color:var(--text-muted); font-size:1.1rem;'><i>{item['scie']}</i> • {item['regn']}</span>", unsafe_allow_html=True)
        with c2:
            st.metric("Total Energy", format_val(item, 'enerc', 'kcal'))
        
        st.markdown("---")

        tabs = st.tabs([
            "🍽️ Proximates & Fibre", "🍬 Starch & Sugars", "💎 Minerals", 
            "💧 Water Soluble Vits", "🛢️ Fat Soluble Vits", "🥑 Fats & Lipids", 
            "🧬 Amino Acids", "🌿 Bioactives", "🥕 Carotenoids"
        ])

        # --- TAB 1: PROXIMATES & FIBRE ---
        with tabs[0]:
            st.write("")
            st.markdown("#### Proximate Principles")
            c1, c2, c3 = st.columns(3)
            c1.metric("Moisture (Water)", format_val(item, 'water', 'g'))
            c2.metric("Protein", format_val(item, 'protcnt', 'g'))
            c3.metric("Ash", format_val(item, 'ash', 'g'))
            
            st.write("")
            c4, c5, c6 = st.columns(3)
            c4.metric("Total Fat", format_val(item, 'fatce', 'g'))
            c5.metric("Carbs (Avail)", format_val(item, 'choavldf', 'g'))
            c6.metric("Energy", format_val(item, 'enerc', 'kcal'))

            st.markdown("---")
            st.markdown("#### Dietary Fibre Breakdown")
            fc1, fc2, fc3 = st.columns(3)
            fc1.metric("Total Dietary Fibre", format_val(item, 'fibtg', 'g'))
            fc2.metric("Insoluble Fibre", format_val(item, 'fibins', 'g'))
            fc3.metric("Soluble Fibre", format_val(item, 'fibsol', 'g'))

            st.markdown("<br>", unsafe_allow_html=True)
            c_left, c_chart, c_right = st.columns([1, 2, 1])
            with c_chart:
                fig = px.pie(
                    names=['Protein', 'Carbohydrates', 'Fat', 'Moisture', 'Ash'],
                    values=[item.get('protcnt', 0), item.get('choavldf', 0), item.get('fatce', 0), item.get('water', 0), item.get('ash', 0)],
                    hole=0.65,
                    color_discrete_sequence=['#48BB78', '#E6C27A', '#F56565', '#4299E1', '#A0AEC0']
                )
                border_color = '#1c212c' if "Dark" in theme_choice else '#ffffff'
                fig.update_traces(textinfo='percent+label', textfont_size=13, hoverinfo='label+percent+value', marker=dict(line=dict(color=border_color, width=2)))
                fig.update_layout(showlegend=False, paper_bgcolor=chart_bg, font=dict(color=chart_font), margin=dict(t=30, b=30, l=30, r=30), height=350)
                fig.add_annotation(text="Proximates", x=0.5, y=0.5, font_size=18, showarrow=False, font_color=chart_font)
                st.plotly_chart(fig, use_container_width=True)

        # --- TAB 2: STARCH & SUGARS ---
        with tabs[1]:
            st.write("")
            c1, c2 = st.columns([1, 1.2])
            with c1:
                st.markdown("#### Starch & Available CHO")
                st.metric("Total Available CHO", format_val(item, 'choavldf', 'g'))
                st.metric("Total Starch", format_val(item, 'starch', 'g'))
                st.metric("Total Free Sugars", format_val(item, 'fsugar', 'g'))
                
            with c2:
                st.markdown("#### Individual Sugars (g)")
                sugars = {
                    "Fructose": 'frus', 
                    "Glucose": 'glus', 
                    "Sucrose": 'sucs', 
                    "Maltose": 'mals',
                    "Lactose": 'lactose'
                }
                
                sy_vals = [item.get(v, 0) for v in sugars.values()]
                se_vals = [item.get(f"{v}_e", 0) for v in sugars.values()]
                
                fig_sugars = px.bar(x=list(sugars.keys()), y=sy_vals, error_y=se_vals, text_auto='.2s')
                fig_sugars.update_traces(marker_color='#9F7AEA', textfont_size=12, textangle=-45, textposition="outside", cliponaxis=False)
                fig_sugars.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, xaxis=dict(automargin=True), yaxis=dict(showgrid=True, gridcolor=chart_grid, automargin=True), xaxis_title="", yaxis_title="g", font=dict(color=chart_font), height=400, margin=dict(t=30, b=50))
                st.plotly_chart(fig_sugars, use_container_width=True)

        # --- TAB 3: MINERALS ---
        with tabs[2]:
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Macro Minerals (mg)")
                mins_keys = {"Calcium": 'ca', "Magnesium": 'mg', "Phosphorus": 'p', "Sodium": 'na', "Potassium": 'k'}
                y_vals = [item.get(k, 0) for k in mins_keys.values()]
                e_vals = [item.get(f"{k}_e", 0) for k in mins_keys.values()]
                
                fig_macro = px.bar(x=list(mins_keys.keys()), y=y_vals, error_y=e_vals, text_auto='.2s')
                fig_macro.update_traces(marker_color='#E6C27A' if "Dark" in theme_choice else '#B45309', textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                fig_macro.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, xaxis=dict(automargin=True), yaxis=dict(showgrid=True, gridcolor=chart_grid, automargin=True), xaxis_title="", yaxis_title="mg", font=dict(color=chart_font), margin=dict(t=30, b=50))
                st.plotly_chart(fig_macro, use_container_width=True)
                
                st.markdown("#### Heavy & Other Metals")
                heavy_keys = {"Aluminum": 'al', "Arsenic": 'as', "Cadmium": 'cd', "Lead": 'pb', "Mercury": 'hg'}
                hy_vals = [item.get(k, 0) for k in heavy_keys.values()]
                he_vals = [item.get(f"{k}_e", 0) for k in heavy_keys.values()]
                
                fig_heavy = px.bar(x=list(heavy_keys.keys()), y=hy_vals, error_y=he_vals, text_auto='.2s')
                fig_heavy.update_traces(marker_color='#718096', textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                fig_heavy.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, xaxis=dict(automargin=True), yaxis=dict(showgrid=True, gridcolor=chart_grid, automargin=True), xaxis_title="", yaxis_title="Amount", font=dict(color=chart_font), margin=dict(t=30, b=50))
                st.plotly_chart(fig_heavy, use_container_width=True)
            
            with c2:
                st.markdown("#### Trace Elements")
                trace_keys = {
                    "Iron": 'fe', "Zinc": 'zn', "Copper": 'cu', "Manganese": 'mn',
                    "Selenium": 'se', "Chromium": 'cr', "Molybdenum": 'mo',
                    "Cobalt": 'co', "Nickel": 'ni', "Lithium": 'li'
                }
                ty_vals = [item.get(k, 0) for k in trace_keys.values()]
                te_vals = [item.get(f"{k}_e", 0) for k in trace_keys.values()]
                
                fig_trace = px.bar(x=list(trace_keys.keys()), y=ty_vals, error_y=te_vals, text_auto='.2s')
                fig_trace.update_traces(marker_color='#4299E1', textfont_size=12, textangle=-45, textposition="outside", cliponaxis=False)
                fig_trace.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, xaxis=dict(automargin=True), yaxis=dict(showgrid=True, gridcolor=chart_grid, automargin=True), xaxis_title="", yaxis_title="Amount", font=dict(color=chart_font), height=550, margin=dict(t=30, b=80))
                st.plotly_chart(fig_trace, use_container_width=True)

        # --- TAB 4: WATER SOLUBLE VITAMINS ---
        with tabs[3]:
            st.write("")
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown("#### Vitamin C & Others")
                st.metric("Total Vitamin C", format_val(item, 'vitc', 'mg'))
                st.metric("Total Folates", format_val(item, 'folsum', 'µg'))
                st.metric("Biotin (B7)", format_val(item, 'biot', 'µg'))
                
            with c2:
                st.markdown("#### B-Complex Profile")
                b_vits = {
                    "Thiamine (B1)": 'thia', 
                    "Riboflavin (B2)": 'ribf', 
                    "Niacin (B3)": 'nia', 
                    "Pantothenic Acid (B5)": 'pantac',
                    "Total B6": 'vitb6c'
                }
                by_vals = [item.get(v, 0) for v in b_vits.values()]
                be_vals = [item.get(f"{v}_e", 0) for v in b_vits.values()]
                
                fig_b = px.bar(x=list(b_vits.keys()), y=by_vals, error_y=be_vals, text_auto='.2s')
                fig_b.update_traces(marker_color='#68D391', textfont_size=12, textangle=-45, textposition="outside", cliponaxis=False)
                fig_b.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, xaxis=dict(automargin=True), yaxis=dict(showgrid=True, gridcolor=chart_grid, automargin=True), xaxis_title="", yaxis_title="mg", font=dict(color=chart_font), height=350, margin=dict(t=30, b=80))
                st.plotly_chart(fig_b, use_container_width=True)

        # --- TAB 5: FAT SOLUBLE VITAMINS ---
        with tabs[4]:
            st.write("")
            c1, c2, c3 = st.columns(3)
            c1.metric("Retinol (Vit A)", format_val(item, 'retol', 'µg'))
            c2.metric("Ergocalciferol (D2)", format_val(item, 'ergcal', 'µg'))
            c3.metric("Cholecalciferol (D3)", format_val(item, 'chocal', 'µg'))
            
            st.write("")
            c4, c5, c6 = st.columns(3)
            c4.metric("Total Vitamin E", format_val(item, 'vite', 'mg'))
            c5.metric("Phylloquinones (K1)", format_val(item, 'vitk1', 'µg'))
            c6.metric("Menaquinones (K2)", format_val(item, 'vitk2', 'µg'))
            
            st.markdown("---")
            st.markdown("#### Vitamin E Profile (mg)")
            
            vit_e_keys = {
                "α-Tocopherol": 'tocpha', "β-Tocopherol": 'tocphb', "γ-Tocopherol": 'tocphg', "δ-Tocopherol": 'tocphd',
                "α-Tocotrienol": 'toctra', "β-Tocotrienol": 'toctrb', "γ-Tocotrienol": 'toctrg', "δ-Tocotrienol": 'toctrd'
            }
            ey_vals = [item.get(k, 0) for k in vit_e_keys.values()]
            ee_vals = [item.get(f"{k}_e", 0) for k in vit_e_keys.values()]
            
            fig_vite = px.bar(x=list(vit_e_keys.keys()), y=ey_vals, error_y=ee_vals, text_auto='.2s')
            fig_vite.update_traces(marker_color='#F6E05E', textfont_size=12, textangle=-45, textposition="outside", cliponaxis=False)
            fig_vite.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, xaxis=dict(automargin=True), yaxis=dict(showgrid=True, gridcolor=chart_grid, automargin=True), xaxis_title="", yaxis_title="mg", font=dict(color=chart_font), height=400, margin=dict(t=30, b=80))
            st.plotly_chart(fig_vite, use_container_width=True)

        # --- TAB 6: FATS & LIPIDS ---
        with tabs[5]:
            st.write("")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Saturated (SFA)", format_val(item, 'fasat', 'g'))
            c2.metric("Monounsat (MUFA)", format_val(item, 'fams', 'g'))
            c3.metric("Polyunsat (PUFA)", format_val(item, 'fapu', 'g'))
            c4.metric("Cholesterol", format_val(item, 'cholc', 'mg'))
            
            st.markdown("---")
            
            c_sfa, c_ufa = st.columns(2)
            
            with c_sfa:
                st.markdown("#### Saturated Fatty Acids (g)")
                sfa_keys = {
                    "Capric (10:0)": 'f10d0', "Undecanoic (11:0)": 'f11d0', "Lauric (12:0)": 'f12d0',
                    "Myristic (14:0)": 'f14d0', "Pentadecanoic (15:0)": 'f15d0', "Palmitic (16:0)": 'f16d0',
                    "Stearic (18:0)": 'f18d0', "Arachidic (20:0)": 'f20d0', "Behenic (22:0)": 'f22d0',
                    "Lignoceric (24:0)": 'f24d0'
                }
                sy_vals = [item.get(k, 0) for k in sfa_keys.values()]
                se_vals = [item.get(f"{k}_e", 0) for k in sfa_keys.values()]
                
                fig_sfa = px.bar(x=list(sfa_keys.keys()), y=sy_vals, error_y=se_vals, text_auto='.2s')
                fig_sfa.update_traces(marker_color='#F56565', textfont_size=12, textangle=-45, textposition="outside", cliponaxis=False)
                fig_sfa.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, xaxis=dict(automargin=True), yaxis=dict(showgrid=True, gridcolor=chart_grid, automargin=True), xaxis_title="", yaxis_title="g", font=dict(color=chart_font), height=450, margin=dict(t=30, b=100))
                st.plotly_chart(fig_sfa, use_container_width=True)
            
            with c_ufa:
                st.markdown("#### Unsaturated Fatty Acids (g)")
                ufa_keys = {
                    "Myristoleic (14:1)": 'f14d1cn5', "Palmitoleic (16:1)": 'f16d1cn7', "Oleic (18:1)": 'f18d1cn9',
                    "Eicosenoic (20:1)": 'f20d1cn9', "Erucic (22:1)": 'f22d1cn9', "Nervonic (24:1)": 'f24d1cn9',
                    "Linoleic (18:2)": 'f18d2cn6', "ALA (18:3 n-3)": 'f18d3n3', "Eicosadienoic (20:2)": 'f20d2n6',
                    "Arachidonic (20:4)": 'f20d4n6', "EPA (20:5 n-3)": 'f20d5n3'
                }
                uy_vals = [item.get(k, 0) for k in ufa_keys.values()]
                ue_vals = [item.get(f"{k}_e", 0) for k in ufa_keys.values()]
                
                fig_ufa = px.bar(x=list(ufa_keys.keys()), y=uy_vals, error_y=ue_vals, text_auto='.2s')
                fig_ufa.update_traces(marker_color='#48BB78', textfont_size=12, textangle=-45, textposition="outside", cliponaxis=False)
                fig_ufa.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, xaxis=dict(automargin=True), yaxis=dict(showgrid=True, gridcolor=chart_grid, automargin=True), xaxis_title="", yaxis_title="g", font=dict(color=chart_font), height=450, margin=dict(t=30, b=100))
                st.plotly_chart(fig_ufa, use_container_width=True)

        # --- TAB 7: AMINO ACIDS ---
        with tabs[6]:
            st.write("")
            st.markdown("#### Amino Acid Profile (mg/g N)")
            st.info("Values are generally expressed in mg per gram of Nitrogen.")
            
            eaa_keys = {
                'Histidine': 'his', 'Isoleucine': 'ile', 'Leucine': 'leu', 'Lysine': 'lys', 
                'Methionine': 'met', 'Phenylalanine': 'phe', 'Threonine': 'thr', 'Tryptophan': 'trp', 'Valine': 'val'
            }
            naa_keys = {
                'Alanine': 'ala', 'Arginine': 'arg', 'Aspartic Acid': 'asp', 'Cystine': 'cys', 
                'Glutamic Acid': 'glu', 'Glycine': 'gly', 'Proline': 'pro', 'Serine': 'ser', 'Tyrosine': 'tyr'
            }
            
            c_eaa, c_naa = st.columns(2)
            
            with c_eaa:
                st.markdown("##### Essential Amino Acids")
                eaa_vals = [item.get(v, 0) for v in eaa_keys.values()]
                st.plotly_chart(plot_radar(eaa_vals, list(eaa_keys.keys()), "Essential", "#48BB78"), use_container_width=True)
                
                eaa_data = [{"Amino Acid": k, "Value (mg)": format_val(item, v, "")} for k, v in eaa_keys.items()]
                st.dataframe(pd.DataFrame(eaa_data), hide_index=True, use_container_width=True)

            with c_naa:
                st.markdown("##### Non-Essential / Conditionally Essential")
                naa_vals = [item.get(v, 0) for v in naa_keys.values()]
                st.plotly_chart(plot_radar(naa_vals, list(naa_keys.keys()), "Non-Essential", "#4299E1"), use_container_width=True)
                
                naa_data = [{"Amino Acid": k, "Value (mg)": format_val(item, v, "")} for k, v in naa_keys.items()]
                st.dataframe(pd.DataFrame(naa_data), hide_index=True, use_container_width=True)

        # --- TAB 8: BIOACTIVES ---
        with tabs[7]:
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Polyphenols & Antioxidants")
                st.metric("Total Polyphenols", format_val(item, 'polyph', 'mg'))
                st.markdown("##### Specific Phenolics")
                st.markdown(f"**Gallic Acid:** <span style='color:var(--text-muted);'>{format_val(item, 'gallac', 'mg')}</span>", unsafe_allow_html=True)
                st.markdown(f"**Quercetin:** <span style='color:var(--text-muted);'>{format_val(item, 'querce', 'mg')}</span>", unsafe_allow_html=True)
            
            with c2:
                st.markdown("#### Anti-Nutrients")
                st.metric("Phytate", format_val(item, 'phytac', 'mg'))
                st.metric("Total Oxalates", format_val(item, 'oxalt', 'mg'))
                st.metric("Saponins", format_val(item, 'sapon', 'mg'))

        # --- TAB 9: CAROTENOIDS ---
        with tabs[8]:
            st.write("")
            c1, c2 = st.columns([1, 1.5])
            with c1:
                st.markdown("#### Total Carotenoids")
                st.metric("Total Carotenoids", format_val(item, 'cartoid', 'µg'))
                
                st.markdown("#### Key Provitamin A")
                st.metric("Beta-Carotene", format_val(item, 'cartb', 'µg'))
                st.metric("Alpha-Carotene", format_val(item, 'carta', 'µg'))
                st.metric("Beta-Cryptoxanthin", format_val(item, 'crypxb', 'µg'))
                
            with c2:
                st.markdown("#### Carotenoid Profile (µg)")
                carot_keys = {
                    "Lutein": 'lutn', 
                    "Zeaxanthin": 'zea', 
                    "Lycopene": 'lycpn', 
                    "Gamma-Carotene": 'cartg',
                    "Alpha-Carotene": 'carta',
                    "Beta-Carotene": 'cartb',
                    "Beta-Cryptoxanthin": 'crypxb'
                }
                cy_vals = [item.get(k, 0) for k in carot_keys.values()]
                ce_vals = [item.get(f"{k}_e", 0) for k in carot_keys.values()]
                
                fig_carot = px.bar(x=list(carot_keys.keys()), y=cy_vals, error_y=ce_vals, text_auto='.2s')
                fig_carot.update_traces(marker_color='#ED8936', textfont_size=12, textangle=-45, textposition="outside", cliponaxis=False)
                fig_carot.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, xaxis=dict(automargin=True), yaxis=dict(showgrid=True, gridcolor=chart_grid, automargin=True), xaxis_title="", yaxis_title="µg", font=dict(color=chart_font), height=450, margin=dict(t=30, b=80))
                st.plotly_chart(fig_carot, use_container_width=True)
