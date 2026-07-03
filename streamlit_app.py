import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px  # Moved to the top to fix the syntax error
import time

# Set page layout
st.set_page_config(page_title="Oil Palm Data Cleaner & Mapper", layout="wide")

# Initialize session state variables for page navigation and data storage
if "page" not in st.session_state:
    st.session_state.page = "Upload Page"
if "cleaned_df" not in st.session_state:
    st.session_state.cleaned_df = None
if "total_trees" not in st.session_state:
    st.session_state.total_trees = 0

# ==============================================================================
# PAGE 1: INTRODUCTION & UPLOAD
# ==============================================================================
if st.session_state.page == "Upload Page":
    st.title("🌴 Oil Palm Estate Data Preprocessing & Mapping System")
    st.markdown("### Welcome to the Automated Spatial Parsing Tool")
    
    # Simple system introduction block
    st.markdown("""
    This system is designed to automate the cleaning and transformation of complex 2D agricultural estate grid layouts.
    
    **How it works:**
    1. **Upload:** Drag and drop your raw 2D grid matrix Excel file (e.g., *0.501 Map Teluk Intan.xlsx*).
    2. **Processing:** The system unpivots the coordinates, isolates individual tree identifiers, and constructs structural location pairs (`C,R`).
    3. **Dashboard Forwarding:** Once cleaned, you will be automatically redirected to your interactive mapping dashboard and data summary download station.
    """)
    
    st.markdown("---")
    st.subheader("📁 Upload Your Dataset")
    
    uploaded_file = st.file_uploader(
        "Drag and drop your estate map Excel file (.xlsx) here", 
        type=["xlsx"], 
        key="uploader"
    )
    
    if uploaded_file is not None:
        # Visual loading spinner before forwarding
        with st.spinner("🤖 Preprocessing engine active... Cleaning data matrix and calculating coordinates..."):
            try:
                # Read raw excel matrix
                xls = pd.ExcelFile(uploaded_file)
                df_raw = pd.read_excel(uploaded_file, sheet_name=xls.sheet_names[0])
                
                row_identifier_col = df_raw.columns[0]
                flattened_data = []
                
                # Loop through matrix to map coordinates
                for idx, row in df_raw.iterrows():
                    row_id = str(row[row_identifier_col]).strip()
                    
                    for col_id in df_raw.columns[1:]:
                        palm_no = row[col_id]
                        
                        if pd.notna(palm_no) and str(palm_no).strip() != "":
                            try:
                                palm_no_int = int(float(palm_no))
                                location_str = f"{col_id},{row_id}"
                                
                                c_num = int(''.join(filter(str.isdigit, col_id)))
                                r_num = int(''.join(filter(str.isdigit, row_id)))
                                
                                flattened_data.append({
                                    "PALM NO.": palm_no_int,
                                    "LOCATION": location_str,
                                    "Col_Num": c_num,
                                    "Row_Num": r_num
                                })
                            except ValueError:
                                continue

                # Create and sort dataframe
                df_clean = pd.DataFrame(flattened_data)
                df_clean = df_clean.sort_values(by="PALM NO.").reset_index(drop=True)
                
                # Save processed outputs to session state memory
                st.session_state.cleaned_df = df_clean
                st.session_state.total_trees = len(df_clean)
                
                # Simulate a smooth load duration before automated redirection
                time.sleep(1.5)
                
                # Update page state and trigger instant rerun to page 2
                st.session_state.page = "Dashboard Page"
                st.rerun()
                
            except Exception as e:
                st.error(f"Error parsing file layout: {e}")

# ==============================================================================
# PAGE 2: CLEANED DATASET & DASHBOARD
# ==============================================================================
elif st.session_state.page == "Dashboard Page":
    
    # Navigation header back button
    col_header, col_nav = st.columns([5, 1])
    with col_header:
        st.title("📊 Estate Spatial Mapping Analytics Dashboard")
    with col_nav:
        st.write("") 
        if st.button("🔄 Upload New File", use_container_width=True):
            st.session_state.page = "Upload Page"
            st.session_state.cleaned_df = None
            st.session_state.total_trees = 0
            st.rerun()
            
    st.markdown("---")
    
    # Retrieve data from session state memory
    df_clean = st.session_state.cleaned_df
    total_trees = st.session_state.total_trees
    df_summary = df_clean[["PALM NO.", "LOCATION"]]
    
    # Main grid layout splits
    col_stats, col_viz = st.columns([1, 2])
    
    # --- KPI Metrics & Tables Column ---
    with col_stats:
        st.markdown("### 📈 Key Summary Metrics")
        st.metric(label="Total Unique Planted Trees Identified", value=f"{total_trees} Palms")
        
        csv_data = df_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Clean Summary (CSV)",
            data=csv_data,
            file_name="cleaned_palm_summary.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown("### 📋 Filtered Dataset View")
        st.dataframe(df_summary, height=430, use_container_width=True)
        
    # --- Interactive 3D Spatial Matrix Visualization Column ---
    with col_viz:
        st.markdown("### 🗺️ Interactive 3D Tree Matrix Mapping Layout")
        st.caption("💡 Click and drag inside the chart to rotate the estate field in 3D space! Scroll to zoom.")
        
        if not df_clean.empty:
            # Create a height (Z-axis) surface layer matching the Palm Numbers
            df_clean["Height (Z)"] = df_clean["PALM NO."] 
            
            # Generate 3D Scatter Plot using Plotly
            fig_3d = px.scatter_3d(
                df_clean,
                x="Col_Num",
                y="Row_Num",
                z="Height (Z)",
                color="Height (Z)",
                color_continuous_scale="Viridis",  # Beautiful green-to-blue gradient
                labels={
                    "Col_Num": "Column (X)",
                    "Row_Num": "Row (Y)",
                    "Height (Z)": "Palm ID Elevation (Z)"
                },
                hover_name="LOCATION",
                hover_data={"PALM NO.": True, "Col_Num": False, "Row_Num": False, "Height (Z)": False}
            )

            # Match layout styling & invert Y-axis so Row 1 sits correctly at the top front
fig_3d.update_layout(
    scene=dict(
        xaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="lightgray"),
        yaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="lightgray", autorange="reversed"), # Fixed spelling here!
        zaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="lightgray"),
    ),
    margin=dict(r=0, l=0, b=0, t=30),
    height=550
)
           
            
            # Render the 3D plot smoothly into Streamlit
            st.plotly_chart(fig_3d, use_container_width=True)
            
        else:
            st.warning("Data tracking parameters parsed empty.")
