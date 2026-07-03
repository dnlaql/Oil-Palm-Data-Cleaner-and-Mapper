import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
    
    # Navigation header back button to let user upload a new file if needed
    col_header, col_nav = st.columns([5, 1])
    with col_header:
        st.title("📊 Estate Spatial Mapping Analytics Dashboard")
    with col_nav:
        st.markdown("<br>", unsafe_allowed_html=True)
        if st.button("🔄 Upload New File", use_container_width=True):
            st.session_state.page = "Upload Page"
            st.session_state.cleaned_df = None
            st.session_state.total_trees = 0
            st.rerun()
            
    st.markdown("---")
    
    # Retrieve data from session state memory
    df_clean = st.session_state.cleaned_df
    total_trees = st.session_state.total_trees
    
    # Separate columns out to match requirements perfectly
    df_summary = df_clean[["PALM NO.", "LOCATION"]]
    
    # Main grid layout splits
    col_stats, col_viz = st.columns([1, 2])
    
    # --- KPI Metrics & Tables Column ---
    with col_stats:
        st.markdown("### 📈 Key Summary Metrics")
        # Requirement 4: Total of Tree
        st.metric(label="Total Unique Planted Trees Identified", value=f"{total_trees} Palms")
        
        # Requirement 2: Summary Downloader (Palm No and Location)
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
        
    # --- Requirement 3: Spatial Matrix Visualization Column ---
    with col_viz:
        st.markdown("### 🗺️ Entire Tree Matrix Mapping Layout")
        
        if not df_clean.empty:
            max_c = df_clean["Col_Num"].max()
            max_r = df_clean["Row_Num"].max()
            
            fig, ax = plt.subplots(figsize=(12, 7.5))
            
            # Scatter coordinates representing structural mapping vectors
            ax.scatter(
                df_clean["Col_Num"], 
                df_clean["Row_Num"], 
                color="#2E7D32", 
                s=35, 
                alpha=0.85, 
                edgecolors='none'
            )
            
            # Flip Y axis so Row 1 starts from top visually matching standard crop field views
            ax.set_ylim(max_r + 2, -1)
            ax.set_xlim(-1, max_c + 2)
            
            ax.set_xlabel("Columns (Coordinate Vectors)", fontsize=10, fontweight='bold')
            ax.set_ylabel("Rows (Coordinate Vectors)", fontsize=10, fontweight='bold')
            ax.set_title(f"Field Mapping Network Node Layout — Total Nodes: {total_trees}", fontsize=11, fontweight='bold', pad=10)
            
            ax.grid(True, linestyle=":", alpha=0.4, color="gray")
            ax.set_facecolor("#FAFAFA")
            
            st.pyplot(fig)
        else:
            st.warning("Data tracking parameters parsed empty.")
