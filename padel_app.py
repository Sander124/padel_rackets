import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Tuple

# Configure page
st.set_page_config(
    page_title="Padel Racket Explorer",
    page_icon="🎾",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .racket-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    
    .racket-name {
        font-size: 18px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    
    .price-tag {
        font-size: 20px;
        font-weight: bold;
        color: #27ae60;
        margin: 10px 0;
    }
    
    .price-unavailable {
        font-size: 16px;
        color: #95a5a6;
        font-style: italic;
        margin: 10px 0;
    }
    
    .overall-rating {
        background: #3498db;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        display: inline-block;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .stat-row {
        display: flex;
        justify-content: space-between;
        margin: 5px 0;
    }
    
    .stat-label {
        font-weight: 600;
        color: #34495e;
    }
    
    .stat-value {
        color: #2c3e50;
    }
    
    .filter-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and prepare the padel racket data"""
    try:
        df = pd.read_csv('padel_data.csv')
        return df
    except FileNotFoundError:
        st.error("Please upload the padel_data.csv file to use this app")
        return None

def create_price_display(price):
    """Create price display handling missing values"""
    if pd.isna(price) or price is None:
        return '<div class="price-unavailable">Price not available</div>'
    else:
        return f'<div class="price-tag">€{price:.0f}</div>'

def create_racket_card(racket):
    """Create HTML for a single racket card"""
    price_html = create_price_display(racket['price'])
    
    return f"""
    <div class="racket-card">
        <div class="racket-name">{racket['name']}</div>
        <div class="overall-rating">Overall: {racket['overall']}</div>
        {price_html}
        <div class="stat-row">
            <span class="stat-label">Power:</span>
            <span class="stat-value">{racket['power']}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Control:</span>
            <span class="stat-value">{racket['control']}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Rebound:</span>
            <span class="stat-value">{racket['rebound']}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Omgang:</span>
            <span class="stat-value">{racket['omgang']}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Sweet Spot:</span>
            <span class="stat-value">{racket['sweetspot']}</span>
        </div>
    </div>
    """

def filter_and_sort_data(df, filters, sort_by, sort_order):
    """Apply filters and sorting to the dataframe"""
    filtered_df = df.copy()
    
    # Apply filters
    if filters['overall_range'][0] != filters['overall_range'][1]:
        filtered_df = filtered_df[
            (filtered_df['overall'] >= filters['overall_range'][0]) &
            (filtered_df['overall'] <= filters['overall_range'][1])
        ]
    
    if filters['price_range'] and filters['price_range'][0] != filters['price_range'][1]:
        # For price filtering, handle NaN values
        price_mask = (
            (filtered_df['price'] >= filters['price_range'][0]) &
            (filtered_df['price'] <= filters['price_range'][1])
        ) | (filters['include_no_price'] & pd.isna(filtered_df['price']))
        filtered_df = filtered_df[price_mask]
    elif not filters['include_no_price']:
        filtered_df = filtered_df[~pd.isna(filtered_df['price'])]
    
    # Apply attribute filters
    for attr in ['power', 'control', 'rebound', 'omgang', 'sweetspot']:
        attr_range = filters[f'{attr}_range']
        if attr_range[0] != attr_range[1]:
            filtered_df = filtered_df[
                (filtered_df[attr] >= attr_range[0]) &
                (filtered_df[attr] <= attr_range[1])
            ]
    
    # Apply name filter
    if filters['name_search']:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(filters['name_search'], case=False, na=False)
        ]
    
    # Apply sorting
    if sort_by == 'price':
        # Handle NaN values in price sorting
        if sort_order == 'asc':
            filtered_df = filtered_df.sort_values('price', na_position='last')
        else:
            filtered_df = filtered_df.sort_values('price', ascending=False, na_position='last')
    else:
        ascending = sort_order == 'asc'
        filtered_df = filtered_df.sort_values(sort_by, ascending=ascending)
    
    return filtered_df

def main():
    st.title("🎾 Padel Racket Explorer")
    st.markdown("Find your perfect padel racket from our comprehensive database")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar filters
    with st.container():
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.subheader("🔍 Filters & Sorting")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**Search & Overall Rating**")
            name_search = st.text_input("Search by name", placeholder="Enter racket name...")
            overall_range = st.slider(
                "Overall Rating", 
                min_value=int(df['overall'].min()), 
                max_value=int(df['overall'].max()), 
                value=(int(df['overall'].min()), int(df['overall'].max()))
            )
        
        with col2:
            st.markdown("**Price Range**")
            # Get price statistics excluding NaN values
            price_data = df['price'].dropna()
            if not price_data.empty:
                price_range = st.slider(
                    "Price (€)", 
                    min_value=int(price_data.min()), 
                    max_value=int(price_data.max()), 
                    value=(int(price_data.min()), int(price_data.max()))
                )
            else:
                price_range = None
            
            include_no_price = st.checkbox("Include rackets without price", value=True)
        
        with col3:
            st.markdown("**Performance Attributes**")
            power_range = st.slider(
                "Power", 
                min_value=int(df['power'].min()), 
                max_value=int(df['power'].max()), 
                value=(int(df['power'].min()), int(df['power'].max()))
            )
            control_range = st.slider(
                "Control", 
                min_value=int(df['control'].min()), 
                max_value=int(df['control'].max()), 
                value=(int(df['control'].min()), int(df['control'].max()))
            )
            rebound_range = st.slider(
                "Rebound", 
                min_value=int(df['rebound'].min()), 
                max_value=int(df['rebound'].max()), 
                value=(int(df['rebound'].min()), int(df['rebound'].max()))
            )
        
        with col4:
            st.markdown("**More Attributes & Sorting**")
            omgang_range = st.slider(
                "Omgang", 
                min_value=int(df['omgang'].min()), 
                max_value=int(df['omgang'].max()), 
                value=(int(df['omgang'].min()), int(df['omgang'].max()))
            )
            sweetspot_range = st.slider(
                "Sweet Spot", 
                min_value=int(df['sweetspot'].min()), 
                max_value=int(df['sweetspot'].max()), 
                value=(int(df['sweetspot'].min()), int(df['sweetspot'].max()))
            )
            
            st.markdown("**Sort by:**")
            sort_by = st.selectbox(
                "Sort by", 
                options=['overall', 'price', 'power', 'control', 'rebound', 'omgang', 'sweetspot', 'name'],
                index=0
            )
            sort_order = st.radio("Order", ["desc", "asc"], horizontal=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Prepare filters dictionary
    filters = {
        'name_search': name_search,
        'overall_range': overall_range,
        'price_range': price_range,
        'include_no_price': include_no_price,
        'power_range': power_range,
        'control_range': control_range,
        'rebound_range': rebound_range,
        'omgang_range': omgang_range,
        'sweetspot_range': sweetspot_range
    }
    
    # Filter and sort data
    filtered_df = filter_and_sort_data(df, filters, sort_by, sort_order)
    
    # Display results summary
    st.markdown("---")
    total_rackets = len(df)
    shown_rackets = len(filtered_df)
    rackets_with_price = len(filtered_df[~pd.isna(filtered_df['price'])])
    rackets_without_price = len(filtered_df[pd.isna(filtered_df['price'])])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rackets", f"{shown_rackets:,}")
    with col2:
        st.metric("With Price", f"{rackets_with_price:,}")
    with col3:
        st.metric("Without Price", f"{rackets_without_price:,}")
    with col4:
        if shown_rackets > 0:
            avg_price = filtered_df['price'].mean()
            if not pd.isna(avg_price):
                st.metric("Avg Price", f"€{avg_price:.0f}")
            else:
                st.metric("Avg Price", "N/A")
    
    # Display rackets in grid
    if filtered_df.empty:
        st.warning("No rackets match your current filters. Try adjusting the filter criteria.")
    else:
        st.markdown("---")
        st.subheader(f"🎾 Rackets ({shown_rackets} found)")
        
        # Create grid layout
        cols_per_row = 3
        rows = (len(filtered_df) + cols_per_row - 1) // cols_per_row
        
        for row in range(rows):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                racket_idx = row * cols_per_row + col_idx
                if racket_idx < len(filtered_df):
                    racket = filtered_df.iloc[racket_idx]
                    with cols[col_idx]:
                        st.markdown(create_racket_card(racket), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
