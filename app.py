import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="IFCT 2017 Master",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom Theme (Executive Dark & Champagne Gold)
st.markdown("""
<style>
    /* Main Background & Typography */
    .stApp { 
        background-color: #0F1116; 
        color: #E2E8F0; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Headers */
    h1, h2, h3, h4 { 
        color: #E6C27A !important; /* Champagne Gold */
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }
    
    /* Elegant Metric Cards */
    div[data-testid="stMetric"] { 
        background-color: #1A1D24; 
        border: 1px solid #2D313A; 
        border-radius: 12px; 
        padding: 16px 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #E6C27A;
    }
    div[data-testid="stMetricLabel"] { 
        color: #A0AEC0; 
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 4px;
    }
    div[data-testid="stMetricValue"] { 
        color: #FFFFFF; 
        font-size: 1.8rem; 
        font-weight: 700;
    }
    
    /* Styled Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding-bottom: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1D24;
        border-radius: 6px;
        padding: 10px 24px;
        border: 1px solid #2D313A;
        color: #A0AEC0;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #E6C27A !important; 
        color: #0F1116 !important; 
        font-weight: 700;
        border-color: #E6C27A;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #15171C;
        border-right: 1px solid #2D313A;
    }
    
    /* Dividers */
    hr {
        border-color: #2D313A;
        opacity: 0.5;
    }
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
def plot_radar(values, labels, title, color):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=labels, fill='toself', name=title,
        line=dict(color=color, width=2),
        fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}",
        marker=dict(size=6)
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, showticklabels=False, gridcolor='#2D313A', linecolor='#2D313A'),
            angularaxis=dict(gridcolor='#2D313A', linecolor='#2D313A')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#A0AEC0', size=12),
        showlegend=False,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig

# -----------------------------------------------------------------------------
# 4. APP LAYOUT
# -----------------------------------------------------------------------------
if not df.empty:
    with st.sidebar:
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

    # Main Content
    if selected_item:
        item = df[df['name'] == selected_item].iloc[0]
        
        # Header
        c1, c2 = st.columns([3, 1])
        with c1:
            st.title(item['name'])
            st.markdown(f"<span style='color:#A0AEC0; font-size:1.1rem;'><i>{item['scie']}</i> • {item['regn']}</span>", unsafe_allow_html=True)
        with c2:
            st.metric("Total Energy", f"{int(item['enerc'])} kcal")
        
        st.markdown("---")

        # Tabs
        tabs = st.tabs(["🍽️ Macros", "💎 Minerals", "💊 Vitamins", "💧 Fats", "🧬 Amino Acids", "🌿 Bioactives"])

        # --- TAB 1: MACROS ---
        with tabs[0]:
            st.write("") # Padding
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Protein", f"{item['protcnt']} g")
            c2.metric("Carbs (Avail)", f"{item['choavldf']} g")
            c3.metric("Total Fat", f"{item['fatce']} g")
            c4.metric("Dietary Fiber", f"{item['fibtg']} g")
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_chart, col_details = st.columns([1.2, 1])
            with col_chart:
                # Upgraded sleek donut chart
                fig = px.pie(
                    names=['Protein', 'Carbohydrates', 'Fat'],
                    values=[item['protcnt'], item['choavldf'], item['fatce']],
                    hole=0.75,
                    color_discrete_sequence=['#48BB78', '#E6C27A', '#F56565']
                )
                fig.update_traces(textinfo='percent+label', textfont_size=14, hoverinfo='label+percent+value', marker=dict(line=dict(color='#0F1116', width=3)))
                fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#E2E8F0'), margin=dict(t=10, b=10, l=10, r=10), height=350)
                
                # Add center text
                fig.add_annotation(text="Macros", x=0.5, y=0.5, font_size=20, showarrow=False, font_color="#A0AEC0")
                st.plotly_chart(fig, use_container_width=True)
            
            with col_details:
                st.markdown("#### Carbohydrate Breakdown")
                st.dataframe(pd.DataFrame({
                    "Component": ["Starch", "Total Sugars", "Soluble Fiber", "Insoluble Fiber"],
                    "Value (g)": [item.get('starch', 0), item.get('fsugar', 0), item.get('fibsol', 0), item.get('fibins', 0)]
                }), hide_index=True, use_container_width=True)

        # --- TAB 2: MINERALS ---
        with tabs[1]:
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Macro Minerals (mg)")
                mins = {"Calcium": item['ca'], "Magnesium": item['mg'], "Phosphorus": item['p'], "Sodium": item['na'], "Potassium": item['k']}
                # Refined Bar Chart
                fig_macro = px.bar(x=list(mins.keys()), y=list(mins.values()), text_auto='.2s')
                fig_macro.update_traces(marker_color='#E6C27A', textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                fig_macro.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#2D313A'), xaxis_title="", yaxis_title="mg", font=dict(color='#A0AEC0'))
                st.plotly_chart(fig_macro, use_container_width=True)
            
            with c2:
                st.markdown("#### Trace Elements (mg)")
                trace = {"Iron": item['fe'], "Zinc": item['zn'], "Copper": item['cu'], "Manganese": item['mn']}
                fig_trace = px.bar(x=list(trace.keys()), y=list(trace.values()), text_auto='.2s')
                fig_trace.update_traces(marker_color='#4299E1', textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                fig_trace.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#2D313A'), xaxis_title="", yaxis_title="mg", font=dict(color='#A0AEC0'))
                st.plotly_chart(fig_trace, use_container_width=True)

        # --- TAB 3: VITAMINS ---
        with tabs[2]:
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Water Soluble")
                st.metric("Vitamin C", f"{item['vitc']} mg")
                st.metric("Total Folates", f"{item.get('folsum', 0)} µg")
                
                b_vits = {
                    "Thiamin (B1)": item['thia'], "Riboflavin (B2)": item['ribf'], 
                    "Niacin (B3)": item['nia'], "Pantothenic (B5)": item.get('pantac', 0),
                    "Vitamin B6": item.get('vitb6c', 0)
                }
                st.dataframe(pd.DataFrame(list(b_vits.items()), columns=["Vitamin", "Value (mg)"]), hide_index=True, use_container_width=True)

            with c2:
                st.markdown("#### Fat Soluble")
                st.metric("Vitamin A (Retinol)", f"{item.get('retol', 0)} µg")
                st.metric("Vitamin D2+D3", f"{item.get('ergcal', 0) + item.get('chocal', 0)} µg")
                st.metric("Vitamin E", f"{item.get('vite', 0) + item.get('tocpha', 0)} mg")
                st.metric("Vitamin K", f"{item.get('vitk1', 0) + item.get('vitk2', 0)} µg")

        # --- TAB 4: FATS ---
        with tabs[3]:
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Fat Composition")
                fats = {
                    "Saturated (SFA)": item.get('fasat', 0),
                    "Monounsat (MUFA)": item.get('fams', 0),
                    "Polyunsat (PUFA)": item.get('fapu', 0)
                }
                st.plotly_chart(plot_radar(list(fats.values()), list(fats.keys()), "Fatty Acids", "#F56565"), use_container_width=True)
            
            with c2:
                st.markdown("#### Lipid Health")
                st.metric("Cholesterol", f"{item.get('cholc', 0)} mg")
                st.metric("Omega-3 (ALA)", f"{item.get('ala', 0)} mg")

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
                st.metric("Total Polyphenols", f"{item.get('polyph', 0)} mg")
                st.markdown("##### Specific Phenolics")
                st.caption(f"**Gallic Acid:** {item.get('gallac', 0)} mg")
                st.caption(f"**Quercetin:** {item.get('querce', 0)} mg")
            
            with c2:
                st.markdown("#### Anti-Nutrients")
                st.metric("Phytate", f"{item.get('phytac', 0)} mg")
                st.metric("Total Oxalates", f"{item.get('oxalt', 0)} mg")
                st.metric("Saponins", f"{item.get('sapon', 0)} mg")
