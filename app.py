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
    }}
    div[data-testid="stMetric"]:hover {{ transform: translateY(-3px); border-color: var(--accent-color); }}
    div[data-testid="stMetricLabel"] {{ color: var(--text-muted) !important; font-size: 0.95rem; font-weight: 500; margin-bottom: 4px; }}
    div[data-testid="stMetricValue"] {{ color: var(--text-primary) !important; font-size: 1.6rem; font-weight: 700; }}
    
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
    """Formats values with standard error (e.g., 10.5 ± 0.2 g)"""
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
    """Calculates sum of values and propagates error using root-sum-square"""
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
        showlegend=False, margin=dict(t=40, b=40, l=40, r=40)
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

        tabs = st.tabs(["🍽️ Proximates & Fibre", "💎 Minerals", "💊 Vitamins", "💧 Fats", "🧬 Amino Acids", "🌿 Bioactives"])

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
            col_chart, col_details = st.columns([1.2, 1])
            with col_chart:
                fig = px.pie(
                    names=['Protein', 'Carbohydrates', 'Fat', 'Moisture', 'Ash'],
                    values=[item.get('protcnt', 0), item.get('choavldf', 0), item.get('fatce', 0), item.get('water', 0), item.get('ash', 0)],
                    hole=0.65,
                    color_discrete_sequence=['#48BB78', '#E6C27A', '#F56565', '#4299E1', '#A0AEC0']
                )
                border_color = '#1c212c' if "Dark" in theme_choice else '#ffffff'
                fig.update_traces(textinfo='percent+label', textfont_size=13, hoverinfo='label+percent+value', marker=dict(line=dict(color=border_color, width=2)))
                fig.update_layout(showlegend=False, paper_bgcolor=chart_bg, font=dict(color=chart_font), margin=dict(t=10, b=10, l=10, r=10), height=350)
                fig.add_annotation(text="Proximates", x=0.5, y=0.5, font_size=18, showarrow=False, font_color=chart_font)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_details:
                st.markdown("#### Other Carbohydrates")
                st.dataframe(pd.DataFrame({
                    "Component": ["Starch", "Total Sugars"],
                    "Value (g)": [format_val(item, 'starch'), format_val(item, 'fsugar')]
                }), hide_index=True, use_container_width=True)

        # --- TAB 2: MINERALS (With Error Bars) ---
        with tabs[1]:
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Macro Minerals (mg)")
                mins_keys = {"Calcium": 'ca', "Magnesium": 'mg', "Phosphorus": 'p', "Sodium": 'na', "Potassium": 'k'}
                y_vals = [item.get(k, 0) for k in mins_keys.values()]
                e_vals = [item.get(f"{k}_e", 0) for k in mins_keys.values()]
                
                fig_macro = px.bar(x=list(mins_keys.keys()), y=y_vals, error_y=e_vals, text_auto='.2s')
                fig_macro.update_traces(marker_color='#E6C27A' if "Dark" in theme_choice else '#B45309', textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                fig_macro.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, yaxis=dict(showgrid=True, gridcolor=chart_grid), xaxis_title="", yaxis_title="mg", font=dict(color=chart_font))
                st.plotly_chart(fig_macro, use_container_width=True)
            
            with c2:
                st.markdown("#### Trace Elements (mg)")
                trace_keys = {"Iron": 'fe', "Zinc": 'zn', "Copper": 'cu', "Manganese": 'mn'}
                ty_vals = [item.get(k, 0) for k in trace_keys.values()]
                te_vals = [item.get(f"{k}_e", 0) for k in trace_keys.values()]
                
                fig_trace = px.bar(x=list(trace_keys.keys()), y=ty_vals, error_y=te_vals, text_auto='.2s')
                fig_trace.update_traces(marker_color='#4299E1', textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                fig_trace.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, yaxis=dict(showgrid=True, gridcolor=chart_grid), xaxis_title="", yaxis_title="mg", font=dict(color=chart_font))
                st.plotly_chart(fig_trace, use_container_width=True)

        # --- TAB 3: VITAMINS ---
        with tabs[2]:
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Water Soluble")
                st.metric("Vitamin C", format_val(item, 'vitc', 'mg'))
                st.metric("Total Folates", format_val(item, 'folsum', 'µg'))
                
                b_vits = {
                    "Thiamin (B1)": 'thia', "Riboflavin (B2)": 'ribf', 
                    "Niacin (B3)": 'nia', "Pantothenic (B5)": 'pantac',
                    "Vitamin B6": 'vitb6c'
                }
                b_vit_data = [{"Vitamin": k, "Value (mg)": format_val(item, v, "")} for k, v in b_vits.items()]
                st.dataframe(pd.DataFrame(b_vit_data), hide_index=True, use_container_width=True)

            with c2:
                st.markdown("#### Fat Soluble")
                st.metric("Vitamin A (Retinol)", format_val(item, 'retol', 'µg'))
                st.metric("Vitamin D2+D3", format_sum_val(item, ['ergcal', 'chocal'], 'µg'))
                st.metric("Vitamin E", format_sum_val(item, ['vite', 'tocpha'], 'mg'))
                st.metric("Vitamin K", format_sum_val(item, ['vitk1', 'vitk2'], 'µg'))

        # --- TAB 4: FATS ---
        with tabs[3]:
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Fat Composition")
                fats = {"Saturated (SFA)": item.get('fasat', 0), "Monounsat (MUFA)": item.get('fams', 0), "Polyunsat (PUFA)": item.get('fapu', 0)}
                st.plotly_chart(plot_radar(list(fats.values()), list(fats.keys()), "Fatty Acids", "#F56565"), use_container_width=True)
            
            with c2:
                st.markdown("#### Lipid Health")
                st.metric("Cholesterol", format_val(item, 'cholc', 'mg'))
                st.metric("Omega-3 (ALA)", format_val(item, 'ala', 'mg'))

        # --- TAB 5: AMINO ACIDS ---
        with tabs[4]:
            st.write("")
            st.markdown("#### Essential Amino Acids (mg/g N)")
            aa_labels = ["Arg", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Thr", "Trp", "Val"]
            aa_keys = ['arg', 'his', 'ile', 'leu', 'lys', 'met', 'phe', 'thr', 'trp', 'val']
            aa_values = [item.get(k, 0) for k in aa_keys]
            st.plotly_chart(plot_radar(aa_values, aa_labels, "Amino Profile", "#48BB78"), use_container_width=True)

        # --- TAB 6: BIOACTIVES ---
        with tabs[5]:
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
