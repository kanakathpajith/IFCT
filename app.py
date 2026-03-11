import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------
import streamlit as st

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="IFCT 2017 Master",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Premium Dark Theme Custom CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* 1. Main Background and Typography */
    .stApp { 
        background-color: #0B0E14; /* Deep, rich dark background */
        color: #E2E8F0;            /* Crisp, readable off-white text */
        font-family: 'Inter', 'Segoe UI', sans-serif; 
    }

    /* 2. Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #151A22; /* Slightly lighter than main bg for depth */
        border-right: 1px solid #2D3748;
    }

    /* 3. Elegant Gold Headings */
    h1, h2, h3, h4, h5, h6 { 
        color: #D4AF37 !important; 
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* 4. Premium Metric Cards */
    div[data-testid="stMetric"] { 
        background-color: #1A202C; 
        border: 1px solid #2D3748; 
        border-radius: 12px; 
        padding: 15px 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    
    /* Subtle Gold Glow on Metric Hover */
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(212, 175, 55, 0.15); 
        border-color: #D4AF37;
    }

    div[data-testid="stMetricLabel"] { 
        color: #A0AEC0; 
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    div[data-testid="stMetricValue"] { 
        color: #FFFFFF; 
        font-size: 2rem; 
        font-weight: 700;
    }

    /* 5. Sophisticated Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1A202C;
        border-radius: 6px 6px 0 0;
        border: 1px solid #2D3748;
        border-bottom: none;
        color: #A0AEC0;
        padding: 10px 20px;
    }

    .stTabs [aria-selected="true"] { 
        background-color: #D4AF37 !important; 
        color: #0B0E14 !important; 
        font-weight: 700;
        border-color: #D4AF37;
    }
    
    /* Hide the default Streamlit top decoration */
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Demo Content (To preview the styles)
# -----------------------------------------------------------------------------
st.title("🥗 IFCT 2017 Nutritional Explorer")
st.markdown("Explore the Indian Food Composition Tables with advanced analytics and filtering.")

# Sidebar demo
with st.sidebar:
    st.header("Filters")
    st.selectbox("Select Food Group", ["Cereals", "Pulses", "Vegetables", "Fruits"])
    st.slider("Protein Content (g)", 0, 100, (10, 50))

# Metrics demo
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Foods", "528", "+12 additions")
col2.metric("Avg Protein", "14.2 g", "High")
col3.metric("Avg Fiber", "8.5 g", "-1.2 g")
col4.metric("Data Completeness", "98.5%", "+0.5%")

st.markdown("---")

# Tabs demo
tab1, tab2, tab3 = st.tabs(["📊 Nutritional Overview", "🔍 Search Database", "📈 Comparative Analysis"])

with tab1:
    st.subheader("Macronutrient Distribution")
    st.info("Your charts and dataframes will go here. The dark theme will make brightly colored charts stand out beautifully.")# -----------------------------------------------------------------------------
# 2. DATA PROCESSING
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        # Load the uploaded file
        df = pd.read_csv("extracted_ifct_data.csv")
        
        # 1. Generate 'Group' column from IFCT Code (First Letter)
        code_map = {
            'A': 'Cereals & Millets', 'B': 'Grain Legumes', 'C': 'Green Leafy Veg',
            'D': 'Other Veg', 'E': 'Fruits', 'F': 'Roots & Tubers',
            'G': 'Condiments & Spices', 'H': 'Nuts & Oil Seeds', 'I': 'Sugars',
            'J': 'Mushrooms', 'K': 'Misc', 'L': 'Milk & Dairy',
            'M': 'Egg Products', 'N': 'Poultry', 'O': 'Animal Meat',
            'P': 'Marine Fish', 'Q': 'Marine Shellfish', 'R': 'Marine Mollusks',
            'S': 'Freshwater Fish'
        }
        
        # Extract first letter of code (e.g., 'A001' -> 'A')
        df['Group_Code'] = df['code'].astype(str).str[0].str.upper()
        df['Group'] = df['Group_Code'].map(code_map).fillna('Other')
        
        # 2. Clean Numeric Columns (Fill NaNs with 0 for plotting)
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
        line=dict(color=color),
        fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.3,)}"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, showticklabels=False)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FAFAFA'),
        showlegend=False,
        margin=dict(t=30, b=30, l=40, r=40)
    )
    return fig

# -----------------------------------------------------------------------------
# 4. APP LAYOUT
# -----------------------------------------------------------------------------
if not df.empty:
    with st.sidebar:
        st.title("🥗 IFCT Explorer")
        st.caption(f"Loaded {len(df)} items from database")
        st.markdown("---")
        
        # Filter Logic
        all_groups = ["All"] + sorted(list(df['Group'].unique()))
        selected_group = st.selectbox("Filter by Group", all_groups)
        
        if selected_group != "All":
            filtered_df = df[df['Group'] == selected_group]
        else:
            filtered_df = df
            
        selected_item = st.selectbox("Select Food Item", filtered_df['name'].unique())
        
        st.markdown("---")
        st.info("Displaying IFCT 2017 Standard Data per 100g edible portion.")

    # Main Content
    if selected_item:
        item = df[df['name'] == selected_item].iloc[0]
        
        # Header
        c1, c2 = st.columns([3, 1])
        c1.title(item['name'])
        c1.caption(f"**Scientific Name:** *{item['scie']}* | **Region:** {item['regn']}")
        c2.metric("Energy", f"{int(item['enerc'])} kcal")
        
        st.markdown("---")

        # Tabs
        tabs = st.tabs(["🍽️ Macros", "💎 Minerals", "💊 Vitamins", "💧 Fats", "🧬 Amino Acids", "🌿 Bioactives"])

        # --- TAB 1: MACROS ---
        with tabs[0]:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Protein", f"{item['protcnt']} g")
            c2.metric("Carbs (Avail)", f"{item['choavldf']} g")
            c3.metric("Total Fat", f"{item['fatce']} g")
            c4.metric("Fiber", f"{item['fibtg']} g")
            
            st.write("")
            col_chart, col_details = st.columns(2)
            with col_chart:
                fig = px.pie(
                    names=['Protein', 'Carbs', 'Fat'],
                    values=[item['protcnt'], item['choavldf'], item['fatce']],
                    hole=0.6,
                    color_discrete_sequence=['#4CAF50', '#FFC107', '#F44336']
                )
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_details:
                st.markdown("#### Carbohydrate Breakdown")
                st.dataframe(pd.DataFrame({
                    "Component": ["Starch", "Total Sugars", "Soluble Fiber", "Insoluble Fiber"],
                    "Value (g)": [item.get('starch', 0), item.get('fsugar', 0), item.get('fibsol', 0), item.get('fibins', 0)]
                }), hide_index=True, use_container_width=True)

        # --- TAB 2: MINERALS ---
        with tabs[1]:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Macro Minerals (mg)")
                mins = {
                    "Calcium": item['ca'], "Magnesium": item['mg'], 
                    "Phosphorus": item['p'], "Sodium": item['na'], "Potassium": item['k']
                }
                st.bar_chart(pd.Series(mins), color="#D4AF37")
            
            with c2:
                st.markdown("#### Trace Elements (mg)")
                trace = {
                    "Iron": item['fe'], "Zinc": item['zn'], 
                    "Copper": item['cu'], "Manganese": item['mn']
                }
                fig_trace = px.bar(x=list(trace.keys()), y=list(trace.values()), color_discrete_sequence=['#FF6347'])
                fig_trace.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), yaxis_title="mg")
                st.plotly_chart(fig_trace, use_container_width=True)

        # --- TAB 3: VITAMINS ---
        with tabs[2]:
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
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Fat Composition")
                fats = {
                    "Saturated (SFA)": item.get('fasat', 0),
                    "Monounsat (MUFA)": item.get('fams', 0),
                    "Polyunsat (PUFA)": item.get('fapu', 0)
                }
                st.plotly_chart(plot_radar(list(fats.values()), list(fats.keys()), "Fatty Acids", "#FF7F50"), use_container_width=True)
            
            with c2:
                st.markdown("#### Lipid Health")
                st.metric("Cholesterol", f"{item.get('cholc', 0)} mg")
                st.metric("Omega-3 (Alpha-Linolenic)", f"{item.get('ala', 0)} mg")

        # --- TAB 5: AMINO ACIDS ---
        with tabs[4]:
            st.markdown("#### Essential Amino Acids (mg/g N)")
            aa_labels = ["Arg", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Thr", "Trp", "Val"]
            aa_keys = ['arg', 'his', 'ile', 'leu', 'lys', 'met', 'phe', 'thr', 'trp', 'val']
            aa_values = [item.get(k, 0) for k in aa_keys]
            
            st.plotly_chart(plot_radar(aa_values, aa_labels, "Amino Profile", "#ADFF2F"), use_container_width=True)

        # --- TAB 6: BIOACTIVES ---
        with tabs[5]:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Polyphenols & Antioxidants")
                st.metric("Total Polyphenols", f"{item.get('polyph', 0)} mg")
                # Add specific phenols if available in your CSV
                st.write("**Specific Phenolics:**")
                st.write(f"- Gallic Acid: {item.get('gallac', 0)} mg")
                st.write(f"- Quercetin: {item.get('querce', 0)} mg")
            
            with c2:
                st.markdown("#### Anti-Nutrients")
                st.metric("Phytate", f"{item.get('phytac', 0)} mg")
                st.metric("Total Oxalates", f"{item.get('oxalt', 0)} mg")

                st.metric("Saponins", f"{item.get('sapon', 0)} mg")


