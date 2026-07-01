import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Setup wide screen real estate layout
st.set_page_config(layout="wide", page_title="K-Pop Analytics Engine")
st.title("🇰🇷 K-Pop Comeback Momentum & Fandom Intensity Platform")
st.caption("Strategic Intelligence Suite Built for Atlantic Recording Corporation")

# =========================================================================
# 1. DATA VALIDATION & PREPARATION MODULE 
# =========================================================================
@st.cache_data
def run_data_validation_pipeline():
    df = pd.read_csv("mock_data.csv")
    df['date'] = pd.to_datetime(df['date'])
    
    # Requirement: Ensure exactly 50 entries per day
    daily_totals = df.groupby('date').size()
    faulty_dates = daily_totals[daily_totals != 50].index.tolist()
    if faulty_dates:
        st.sidebar.error(f"❌ Validation Error: Dates {faulty_dates} do not contain 50 rows.")
        
    # Requirement: Normalize identifiers
    df['song'] = df['song'].astype(str).str.strip().str.title()
    df['artist'] = df['artist'].astype(str).str.strip().str.title()
    
    # Requirement: Convert duration to minutes
    df['duration_min'] = df['duration_ms'] / 60000
    
    # Requirement: Validate popularity consistency (Bounded 0-100 scales)
    df['popularity'] = df['popularity'].clip(0, 100)
    
    return df

df_validated = run_data_validation_pipeline()

# =========================================================================
# 2. CORE ANALYTICAL CALCULATIONS ENGINE 
# =========================================================================
def execute_algorithmic_metrics(df):
    # Sort sequentially per unique asset to trace movement vectors
    df = df.sort_values(by=['song', 'artist', 'date']).reset_index(drop=True)
    
    # --- CHART RE-ENTRY DETECTION --- (Step 2)
    df['prev_date'] = df.groupby(['song', 'artist'])['date'].shift(1)
    df['time_gap_days'] = (df['date'] - df['prev_date']).dt.days
    
    # Logic: Left chart if time gap since last record is longer than 1 calendar day
    df['is_re_entry'] = df['time_gap_days'] > 1
    df['re_entry_count'] = df.groupby(['song', 'artist'])['is_re_entry'].cumsum()
    df['entry_status'] = np.where(df['re_entry_count'] == 0, 'First Entry', 'Comeback Re-Entry')
    
    # --- MOMENTUM SPIKE MEASUREMENT ---(Step 3)
    df['prev_position'] = df.groupby(['song', 'artist'])['position'].shift(1)
    df['prev_popularity'] = df.groupby(['song', 'artist'])['popularity'].shift(1)
    
    df['popularity_change_rate'] = df['popularity'] - df['prev_popularity']
    df['rank_jump_magnitude'] = df['prev_position'] - df['position'] # Positives = upward climb
    
    # Formula combining position velocity scaling with streaming metric deltas upon return
    df['momentum_intensity_score'] = (df['rank_jump_magnitude'].fillna(0) * 2.0) + df['popularity_change_rate'].fillna(0)
    df['momentum_intensity_score'] = np.where(df['is_re_entry'], df['momentum_intensity_score'], 0.0)
    
    # --- MOMENTUM SUSTAINABILITY ANALYSIS --- (Step 4)
    df['days_retained_post_comeback'] = df.groupby(['song', 'artist', 're_entry_count']).cumcount()
    # Post-peak rank decay velocity
    df['rank_decay_speed'] = df.groupby(['song', 'artist', 're_entry_count'])['position'].diff().fillna(0)
    # Volatility rolling framework index (3-cycle position variance)
    df['post_surge_volatility'] = df.groupby(['song', 'artist', 're_entry_count'])['position'].transform(lambda x: x.rolling(3, min_periods=1).var()).fillna(0)
    
    # --- FANDOM ENGAGEMENT PROXY ANALYSIS ---
    proxy_aggregates = df.groupby(['song', 'artist']).agg(
        re_entry_frequency=('is_re_entry', 'sum'),
        popularity_spike_sharpness=('popularity_change_rate', 'max'),
        rank_recovery_speed=('rank_jump_magnitude', lambda x: x[x > 0].mean() if len(x[x > 0]) > 0 else 0)
    ).reset_index()
    
    # Mathematical synthesis normalizing metrics to a clean 100-point benchmark scale
    proxy_aggregates['fandom_intensity_proxy_score'] = (
        (proxy_aggregates['re_entry_frequency'] * 25) + 
        (proxy_aggregates['popularity_spike_sharpness'].clip(0) * 1.5) + 
        (proxy_aggregates['rank_recovery_speed'] * 1.0)
    ).clip(0, 100)
    
    return df.merge(proxy_aggregates[['song', 'artist', 'fandom_intensity_proxy_score']], on=['song', 'artist'], how='left')

df_analytics = execute_algorithmic_metrics(df_validated)

# =========================================================================
# 3. SIDEBAR INTERACTION SUITE (USER CAPABILITIES) 
# =========================================================================
st.sidebar.header("🎛️ User Capabilities Filters")

# 1. Date range selector
min_d, max_d = df_analytics['date'].min().to_pydatetime(), df_analytics['date'].max().to_pydatetime()
selected_dates = st.sidebar.date_input("Date Range Selector", [min_d, max_d])

# 2. Song & artist filter
artist_list = sorted(df_analytics['artist'].unique())
selected_artists = st.sidebar.multiselect("Artist & Song Filters", artist_list, default=[a for a in artist_list if "Indie" not in a])

# 3. Re-entry count filter
max_re = int(df_analytics['re_entry_count'].max())
selected_min_re = st.sidebar.slider("Re-Entry Count Filter (Minimum)", 0, max_re, 0)

# 4. Album type toggle
album_options = df_analytics['album_type'].unique().tolist()
selected_albums = st.sidebar.multiselect("Album Type Toggle Framework", album_options, default=album_options)

# Execute interactive user filters dynamically
filtered_df = df_analytics[
    (df_analytics['date'] >= pd.to_datetime(selected_dates[0])) &
    (df_analytics['date'] <= pd.to_datetime(selected_dates[1])) &
    (df_analytics['artist'].isin(selected_artists)) &
    (df_analytics['re_entry_count'] >= selected_min_re) &
    (df_analytics['album_type'].isin(selected_albums))
]

# =========================================================================
# 4. APP INTERFACE VISUALIZATION TABS 
# =========================================================================
tab_timeline, tab_spikes, tab_comp, tab_attr, tab_leaderboard = st.tabs([
    "📈 Re-Entry Timeline Visualizer",
    "⚡ Momentum Spike Detection",
    "🔄 Comeback vs. First-Entry",
    "📊 Attribute vs. Momentum",
    "🏆 Fandom Intensity Leaderboard"
])

# MODULE 1: RE-ENTRY TIMELINE VISUALIZER
with tab_timeline:
    st.subheader("Re-Entry Timeline Visualizer")
    fig_line = px.line(
        filtered_df, x='date', y='position', color='song', markers=True,
        title="Playlist Rank Trajectory Lifecycle (Rank 1 at Apex Elevation)",
        labels={'position': 'Playlist Position Rank'}
    )
    fig_line.update_yaxes(autorange="reversed") # Rank 1 conventions
    st.plotly_chart(fig_line, use_container_width=True)

# MODULE 2: MOMENTUM SPIKE DETECTION CHARTS
with tab_spikes:
    st.subheader("Momentum Spike Detection Charts")
    re_events = filtered_df[filtered_df['is_re_entry'] == True]
    if not re_events.empty:
        fig_scatter = px.scatter(
            re_events, x='date', y='momentum_intensity_score', color='song', size='rank_jump_magnitude',
            title="Identified Comeback Volatility and Spike Magnitudes",
            labels={'momentum_intensity_score': 'Computed Momentum Score'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No re-entry spike items detected inside this filtered subset range.")

# MODULE 3: COMEBACK VS FIRST-ENTRY COMPARISON
with tab_comp:
    st.subheader("Comeback vs. First-Entry Comparison Performance Profiles")
    col_l, col_r = st.columns(2)
    with col_l:
        fig_box_comp = px.box(
            filtered_df, x='entry_status', y='position', color='entry_status',
            title="Positional Density Layout profiles"
        )
        fig_box_comp.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_box_comp, use_container_width=True)
    with col_r:
        fig_decay = px.box(
            filtered_df[filtered_df['entry_status'] == 'Comeback Re-Entry'], x='song', y='rank_decay_speed',
            title="Post-Peak Rank Decay Speed Vectors per Track Asset"
        )
        st.plotly_chart(fig_decay, use_container_width=True)

# MODULE 4: CONTENT ATTRIBUTE VS MOMENTUM ANALYSIS (Step 5)
with tab_attr:
    st.subheader("Content Attribute vs Momentum Analysis Modules")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("**Single vs Album Track Comeback Strength & Size Analysis**")
        fig_bubble = px.scatter(
            filtered_df[filtered_df['is_re_entry'] == True], x='total_tracks', y='momentum_intensity_score',
            color='album_type', size='duration_min', title="Album Packaging Density vs Surge Magnitude",
            labels={'total_tracks': 'Tracks on Release Project', 'momentum_intensity_score': 'Spike Power'}
        )
        st.plotly_chart(fig_bubble, use_container_width=True)
    with col_g2:
        st.markdown("**Explicit vs Clean Content Performance Guardrails**")
        fig_exp = px.box(
            filtered_df, x='is_explicit', y='popularity', color='is_explicit',
            title="Popularity Range Stability Distribution: Explicit vs Clean"
        )
        st.plotly_chart(fig_exp, use_container_width=True)

# MODULE 5: FANDOM INTENSKITY LEADERBOARD
with tab_leaderboard:
    st.subheader("The Fandom Intensity Leaderboard Matrix")
    st.markdown("Isolating pure consumer streaming metrics via normalized composite scoring weights.")
    
    board = filtered_df.groupby(['song', 'artist', 'album_type']).agg(
        fandom_intensity_proxy_score=('fandom_intensity_proxy_score', 'first'),
        re_entry_frequency_count=('is_re_entry', 'sum'),
        peak_rank_attained=('position', 'min'),
        mean_decay_velocity=('rank_decay_speed', 'mean'),
        post_surge_volatility_index=('post_surge_volatility', 'mean')
    ).sort_values(by='fandom_intensity_proxy_score', ascending=False).reset_index()
    
    st.dataframe(board, use_container_width=True)