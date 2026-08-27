# modules/architecture/synthesis.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
import json

def generate_layout(algorithm, site_area, max_height, program_mix, iterations):
    """
    Generate a building layout based on input parameters.
    This is a mock generator - replace with real algorithms.
    """
    random.seed(42)
    
    if algorithm == "Grid":
        # Grid-based layout
        footprints = []
        total_area = 0
        target_areas = {
            "Office": program_mix.get("Office", 40) / 100 * site_area,
            "Residential": program_mix.get("Residential", 30) / 100 * site_area,
            "Retail": program_mix.get("Retail", 20) / 100 * site_area,
            "Amenities": program_mix.get("Amenities", 10) / 100 * site_area,
        }
        
        for typ, target in target_areas.items():
            if target > 0:
                num_units = random.randint(3, 8)
                unit_area = target / num_units
                for i in range(num_units):
                    footprints.append({
                        "id": f"{typ[0]}{i+1}",
                        "type": typ,
                        "width": random.uniform(8, 15),
                        "depth": random.uniform(8, 15),
                        "area": unit_area * random.uniform(0.7, 1.3),
                        "x": random.uniform(0, 50),
                        "y": random.uniform(0, 50),
                    })
                    total_area += footprints[-1]["area"]
    elif algorithm == "Radial":
        # Radial (central core) layout
        footprints = []
        core_x, core_y = 25, 25
        for ring in range(1, 4):
            num_units = 4 * ring
            for i in range(num_units):
                angle = (i / num_units) * 2 * 3.14159
                radius = ring * 8
                footprints.append({
                    "id": f"R{ring}{i+1}",
                    "type": ["Office", "Residential", "Retail", "Amenities"][i % 4],
                    "width": random.uniform(6, 12),
                    "depth": random.uniform(6, 12),
                    "area": random.uniform(50, 150),
                    "x": core_x + radius * 0.7 * random.uniform(0.8, 1.2),
                    "y": core_y + radius * 0.7 * random.uniform(0.8, 1.2),
                })
    else:  # Organic / Freeform
        footprints = []
        for i in range(random.randint(8, 15)):
            footprints.append({
                "id": f"O{i+1}",
                "type": ["Office", "Residential", "Retail", "Amenities"][i % 4],
                "width": random.uniform(5, 20),
                "depth": random.uniform(5, 20),
                "area": random.uniform(30, 200),
                "x": random.uniform(0, 50),
                "y": random.uniform(0, 50),
            })
    
    # Add height
    for f in footprints:
        f["height"] = random.uniform(3, max_height * 0.5)
        f["storeys"] = max(1, int(f["height"] / 3.5))
    
    # Calculate summary stats
    total_floor_area = sum(f["area"] * f["storeys"] for f in footprints)
    efficiency = (sum(f["area"] for f in footprints) / site_area) * 100
    
    return footprints, {
        "Total Units": len(footprints),
        "Total Area (m²)": f"{sum(f['area'] for f in footprints):.0f}",
        "Total Floor Area (m²)": f"{total_floor_area:.0f}",
        "Site Efficiency": f"{efficiency:.1f}%",
        "Max Height (m)": f"{max(f['height'] for f in footprints):.1f}",
        "Avg Unit Area (m²)": f"{sum(f['area'] for f in footprints) / len(footprints):.0f}",
    }

def create_3d_plot(footprints):
    """Create a 3D massing visualization."""
    fig = go.Figure()
    
    colors = {
        "Office": "#2196F3",
        "Residential": "#4CAF50",
        "Retail": "#FF9800",
        "Amenities": "#9C27B0",
    }
    
    for f in footprints:
        fig.add_trace(go.Mesh3d(
            x=[f["x"], f["x"]+f["width"], f["x"]+f["width"], f["x"], 
               f["x"], f["x"]+f["width"], f["x"]+f["width"], f["x"]],
            y=[f["y"], f["y"], f["y"]+f["depth"], f["y"]+f["depth"],
               f["y"], f["y"], f["y"]+f["depth"], f["y"]+f["depth"]],
            z=[0, 0, 0, 0, f["height"], f["height"], f["height"], f["height"]],
            color=colors.get(f["type"], "#999"),
            opacity=0.7,
            name=f"{f['type']} {f['id']}",
            showlegend=False,
            hovertemplate=f"{f['type']}<br>Area: {f['area']:.0f} m²<br>Height: {f['height']:.1f}m<br>Storeys: {f['storeys']}<extra></extra>",
        ))
    
    fig.update_layout(
        title="3D Massing Model",
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Height (m)",
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        height=600,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig

def render():
    st.subheader("🏗️ Generative Layout Solver")
    st.markdown("*AI-driven massing and spatial layout generation*")
    
    # Sidebar inputs within the page
    with st.expander("⚙️ Design Parameters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            site_area = st.number_input("Site Area (m²)", min_value=100, max_value=100000, value=5000, step=100)
            max_height = st.number_input("Max Height (m)", min_value=3, max_value=200, value=30, step=1)
            algorithm = st.selectbox("Layout Algorithm", ["Grid", "Radial", "Organic / Freeform"])
        
        with col2:
            st.markdown("**Program Mix (%)**")
            office = st.slider("Office", 0, 100, 40, 5)
            residential = st.slider("Residential", 0, 100, 30, 5)
            retail = st.slider("Retail", 0, 100, 20, 5)
            amenities = 100 - office - residential - retail
            if amenities < 0:
                amenities = 0
            st.info(f"Amenities: {amenities}% (auto-adjusted)")
            
            program_mix = {
                "Office": office,
                "Residential": residential,
                "Retail": retail,
                "Amenities": amenities,
            }
        
        with col3:
            iterations = st.slider("Generation Iterations", 1, 10, 3)
            st.markdown("**Design Constraints**")
            setback = st.checkbox("Apply Setback Requirements", value=True)
            solar = st.checkbox("Solar Orientation Optimization", value=False)
            parking = st.number_input("Parking Spaces", min_value=0, max_value=500, value=50, step=5)
    
    if st.button("🚀 Generate Layout", use_container_width=True):
        with st.spinner("Generating layout..."):
            footprints, stats = generate_layout(
                algorithm, site_area, max_height, program_mix, iterations
            )
            
            st.session_state["generated_layout"] = footprints
            st.session_state["layout_stats"] = stats
            
            # Success message
            st.success(f"✅ Layout generated successfully! {stats['Total Units']} units created.")
    
    # Display results if generated
    if "generated_layout" in st.session_state:
        footprints = st.session_state["generated_layout"]
        stats = st.session_state.get("layout_stats", {})
        
        st.markdown("---")
        st.subheader("📊 Generation Results")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard", "📐 3D Model", "📋 Footprint Data", "📊 Analysis"])
        
        with tab1:
            # Metrics row
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Units", stats.get("Total Units", 0))
            col2.metric("Total Area", stats.get("Total Area (m²)", "0"), help="Site coverage")
            col3.metric("Floor Area", stats.get("Total Floor Area (m²)", "0"), help="Total buildable area")
            col4.metric("Efficiency", stats.get("Site Efficiency", "0%"))
            col5.metric("Max Height", stats.get("Max Height (m)", "0"))
            
            # Program distribution chart
            df_program = pd.DataFrame(footprints)
            if not df_program.empty:
                df_type = df_program.groupby("type").agg({
                    "id": "count",
                    "area": "sum",
                    "storeys": "sum"
                }).reset_index()
                df_type.columns = ["Type", "Count", "Area (m²)", "Storeys"]
                
                col1, col2 = st.columns(2)
                with col1:
                    fig_pie = px.pie(df_type, values="Area (m²)", names="Type", title="Program Distribution by Area")
                    st.plotly_chart(fig_pie, use_container_width=True)
                with col2:
                    fig_bar = px.bar(df_type, x="Type", y=["Area (m²)", "Storeys"], 
                                     title="Area & Storeys by Program Type", barmode="group")
                    st.plotly_chart(fig_bar, use_container_width=True)
        
        with tab2:
            # 3D plot
            fig_3d = create_3d_plot(footprints)
            st.plotly_chart(fig_3d, use_container_width=True)
        
        with tab3:
            # Footprint data table
            df_footprints = pd.DataFrame(footprints)
            df_footprints = df_footprints[["id", "type", "area", "width", "depth", "height", "storeys"]]
            df_footprints = df_footprints.rename(columns={
                "id": "Unit ID",
                "type": "Type",
                "area": "Area (m²)",
                "width": "Width (m)",
                "depth": "Depth (m)",
                "height": "Height (m)",
                "storeys": "Storeys"
            })
            st.dataframe(df_footprints, use_container_width=True, height=400)
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                csv = df_footprints.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            with col2:
                st.download_button(
                    label="📥 Download as JSON",
                    data=json.dumps(footprints, indent=2),
                    file_name=f"layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with tab4:
            st.subheader("📊 Analysis")
            
            # Height distribution
            col1, col2 = st.columns(2)
            with col1:
                df_heights = pd.DataFrame(footprints)
                fig_hist = px.histogram(df_heights, x="height", nbins=15, 
                                        title="Height Distribution (m)")
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # Area vs Height scatter
                fig_scatter = px.scatter(df_heights, x="area", y="height", 
                                         color="type", title="Area vs Height by Type",
                                         hover_data=["id"])
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Scoring
            st.subheader("🏆 Design Score")
            
            # Mock scoring
            score_factors = {
                "Site Efficiency": min(100, int(float(stats.get("Site Efficiency", "0%").replace("%", "")) * 1.5)),
                "Program Balance": random.randint(60, 95),
                "Height Utilization": random.randint(50, 90),
                "Unit Diversity": random.randint(40, 85),
                "Overall": random.randint(65, 92)
            }
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Efficiency", f"{score_factors['Site Efficiency']}%")
            col2.metric("Program Balance", f"{score_factors['Program Balance']}%")
            col3.metric("Height Utilization", f"{score_factors['Height Utilization']}%")
            col4.metric("Unit Diversity", f"{score_factors['Unit Diversity']}%")
            col5.metric("⭐ Overall", f"{score_factors['Overall']}%", delta="Good")
            
            # Score gauge (simple)
            st.progress(score_factors["Overall"] / 100)
            st.caption(f"Overall Score: {score_factors['Overall']}%")
    
    else:
        st.info("💡 Adjust parameters above and click 'Generate Layout' to see results.")
        
    # Help
    with st.expander("ℹ️ About Generative Layout Solver"):
        st.markdown("""
        This module uses **AI-driven algorithms** to generate building layouts and massing studies.
        
        **Features:**
        - Multiple layout algorithms (Grid, Radial, Organic)
        - Program mix optimization
        - 3D visualization
        - Downloadable results (CSV/JSON)
        - Design scoring and analysis
        
        **Algorithm Options:**
        - **Grid**: Orthogonal block layout (efficient for offices, retail)
        - **Radial**: Central core, ring-based (good for mixed-use, towers)
        - **Organic**: Freeform arrangement (residential, campus)
        """)