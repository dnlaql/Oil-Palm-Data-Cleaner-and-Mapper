import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px  
import time

# Set page layout to wide for dashboard optimization
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
    
    # Top Header & Navigation Banner
    col_header, col_nav = st.columns([5, 1])
    with col_header:
        st.title("📊 Estate Spatial Mapping Analytics Dashboard")
        st.caption("Successfully processed layout file. Explore the mapped nodes and download data summaries below.")
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
    
    # Split the screen into two structural halves: Controls/Table (Left) vs Layout Visualization (Right)
    col_stats, col_viz = st.columns([1, 2], gap="large")
    
    # --------------------------------------------------------------------------
    # LEFT SIDEBAR COLUMN: METRICS, FILTER, DOWNLOADS & TABLES
    # --------------------------------------------------------------------------
    with col_stats:
        st.subheader("📋 Data Controls & Summary")
        st.markdown("Review the summarized tree allocations and export the clean tabular schema.")
        
        # Total Tree KPI Card
        st.metric(label="Total Unique Planted Trees Identified", value=f"{total_trees} Palms")
        
        # --- NEW FEATURE: SEARCH / FILTER PALM NO. ---
        st.markdown("#### 🔍 Search Filter")
        search_query = st.text_input(
            "Enter Palm No. (e.g., 10, 105) or leave blank to show all:",
            key="palm_search"
        ).strip()
        
        # Apply filtering logic based on input
        if search_query:
            try:
                # Convert input to integer to match dataframe data type
                search_val = int(search_query)
                df_filtered = df_clean[df_clean["PALM NO."] == search_val]
            except ValueError:
                st.warning("Please enter a valid numeric Palm Number.")
                df_filtered = df_clean.copy()
        else:
            df_filtered = df_clean.copy()
            
        # Download Action Button (Always exports the full data summary for convenience)
        df_summary_full = df_clean[["PALM NO.", "LOCATION"]]
        csv_data = df_summary_full.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Master Summary (CSV)",
            data=csv_data,
            file_name="cleaned_palm_summary.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown("")
        
        # Display either filtered or full dataframe
        st.markdown(f"#### 📊 Table View ({len(df_filtered)} rows showing)")
        df_display = df_filtered[["PALM NO.", "LOCATION"]]
        st.dataframe(df_display, height=350, use_container_width=True)
        
    # --------------------------------------------------------------------------
    # RIGHT SIDEBAR COLUMN: ORGANIZED VISUALIZATIONS (2D & 3D TABS)
    # --------------------------------------------------------------------------
    with col_viz:
        st.subheader("🗺️ Estate Layout Visualizations")
        st.markdown("Toggle between the specialized **2D Plot Layout Matrix** or the **Interactive 3D Network Layer** views.")
        
        if not df_filtered.empty:
            # Setting up tabs to organize the 2D and 3D views beautifully
            tab1, tab2 = st.tabs(["📈 2D Matrix Layout View", "🎛️ Interactive 3D Terrain View"])
            
            # --- TAB 1: 2D MATPLOTLIB SCATTER VIEW ---
            with tab1:
                st.markdown("#### Spatial Field Layout Matrix")
                st.caption("A clean bird's-eye view tracking active coordinate nodes across your field blocks.")
                
                # We calculate max values from master data to keep grid boundaries stable during filtering
                max_c = df_clean["Col_Num"].max()
                max_r = df_clean["Row_Num"].max()
                
                fig_2d, ax = plt.subplots(figsize=(12, 7.5))
                
                # Plot 2D coordinates (Uses df_filtered)
                ax.scatter(
                    df_filtered["Col_Num"], 
                    df_filtered["Row_Num"], 
                    color="#1B5E20" if search_query else "#2E7D32", # Change color slightly if filtered
                    s=100 if search_query else 40,                  # Make node bigger if it is a specific search result
                    alpha=1.0 if search_query else 0.85, 
                    edgecolors='black' if search_query else 'none'
                )
                
                # Flip Y axis so Row 1 starts from top visually
                ax.set_ylim(max_r + 2, -1)
                ax.set_xlim(-1, max_c + 2)
                
                ax.set_xlabel("Columns (Coordinate Vectors)", fontsize=10, fontweight='bold')
                ax.set_ylabel("Rows (Coordinate Vectors)", fontsize=10, fontweight='bold')
                
                ax.grid(True, linestyle=":", alpha=0.4, color="gray")
                ax.set_facecolor("#FAFAFA")
                
                st.pyplot(fig_2d)
                
            # --- TAB 2: 3D INTERACTIVE PLOTLY VIEW (FLAT & SPACED OUT) ---
            with tab2:
                st.markdown("#### Dynamic 3D Tree Matrix Map")
                st.caption("💡 **Interactivity Tip:** Left-click and drag to rotate the view. Scroll up/down to zoom in on individual nodes.")
                
                # Ensure height (Z-axis) is a flat baseline 0
                df_filtered["Height (Z)"] = 0 
                
                # Generate 3D Scatter Plot using Plotly (Uses df_filtered)
                fig_3d = px.scatter_3d(
                    df_filtered,
                    x="Col_Num",
                    y="Row_Num",
                    z="Height (Z)",
                    color="PALM NO.",  
                    color_continuous_scale="Viridis",
                    labels={
                        "Col_Num": "Column (X)",
                        "Row_Num": "Row (Y)",
                        "Height (Z)": "Base Level",
                        "PALM NO.": "Palm ID"
                    },
                    hover_name="LOCATION",
                    hover_data={"PALM NO.": True, "Col_Num": False, "Row_Num": False, "Height (Z)": False}
                )

                # Aspect ratio added to manually space out the X and Y coordinates in 3D space
                fig_3d.update_layout(
                    scene=dict(
                        xaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="lightgray"),
                        yaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="lightgray", autorange="reversed"),
                        zaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="lightgray", showticklabels=False, title=""),
                        aspectmode="manual",
                        aspectratio=dict(x=1, y=1, z=0.3)  
                    ),
                    margin=dict(r=0, l=0, b=0, t=10),
                    height=600
                )
                
                st.plotly_chart(fig_3d, use_container_width=True)
                
        else:
            st.warning("No matches found for the entered Palm Number. Please check your query.")

# ==============================================================================
# SYSTEM FOOTER & DISCLAIMER
# ==============================================================================
st.markdown("---")

# Layout split for credits and legal disclaimer
col_credits, col_disclaimer = st.columns([1, 2], gap="large")

with col_credits:
    st.markdown("#### 💡 System Credits")
    st.markdown("""
    * **Idea & Conceptualization:** Saidatina Nurfarahanim
    * **Development & Engineering:** Muhammad Daniel Aqil
    """)
    st.caption("© 2026 All Rights Reserved. Oil Palm Estate Data Engine.")

with col_disclaimer:
    st.markdown("#### ⚖️ Legal Disclaimer")
    st.caption("""
    This software utility is provided "as is" for automated spatial cleaning, coordinate transformation, 
    and interactive 2D/3D visualization of agricultural grid matrices. The developer and conceptualizer 
    assume no liability for operational field anomalies, surveying errors, or data inaccuracies resulting 
    from faulty structural formats within the user's uploaded Excel matrix templates. Users are highly 
    encouraged to cross-verify physical tree tags against output coordinates before committing resources 
    to field operations.
    """)
