import streamlit as st
import pandas as pd
import numpy as np
import ast

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="IMDb Movie Analytics Dashboard",
    page_icon="🎬",
    layout="wide"
)

# Main Title & Subtitle matching the screenshot
st.title("🎬 IMDb Movie Analytics Dashboard")
st.caption("Interactive Streamlit Dashboard based on IMDb Top 250 Movies Dataset")

# =========================================================
# 📍 DATASET SELECTION - PASTE YOUR DATASET FILENAME HERE
# =========================================================
DATASET_FILENAME = "ToP 250 movies on imdb in 2026.csv"


# ---------------------------------------------------------
# HELPER FUNCTIONS & DATA LOADING (Section A)
# ---------------------------------------------------------
def parse_list_column(val):
    """Safely parse list strings like ['Drama', 'Crime'] or 'Drama, Crime'"""
    if pd.isna(val):
        return []
    if isinstance(val, list):
        return val
    try:
        res = ast.literal_eval(str(val))
        if isinstance(res, list):
            return [str(item) for item in res]
    except Exception:
        pass
    return [x.strip() for x in str(val).replace('[', '').replace(']', '').replace("'", "").split(',') if x.strip()]

@st.cache_data
def load_dataset(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception:
        # Fallback candidates if exact filename varies
        fallback_files = [
            "ToP_250_movies_on_imdb_in_2026.csv",
            "imdb_top_250.csv",
            "top_250_movies.csv"
        ]
        df = None
        for candidate in fallback_files:
            try:
                df = pd.read_csv(candidate)
                break
            except Exception:
                continue
        if df is None:
            st.error(f"⚠️ Could not load dataset '{file_path}'. Please place the CSV file in your project folder.")
            st.stop()

    # Normalize column names across common variations
    column_mapping = {
        'primaryTitle': 'Title', 'movie_title': 'Title', 'title': 'Title',
        'genres': 'Genre', 'genre': 'Genre',
        'countriesOfOrigin': 'Country', 'country': 'Country', 'countries': 'Country',
        'rating': 'averageRating', 'IMDb Rating': 'averageRating',
        'votes': 'numVotes', 'Votes': 'numVotes',
        'grossWorldwide': 'grossWorldwide', 'Worldwide Gross': 'grossWorldwide'
    }
    df = df.rename(columns=column_mapping)
    
    # Process Genres and Countries
    genre_col = 'Genre' if 'Genre' in df.columns else ('genres' if 'genres' in df.columns else None)
    if genre_col:
        df['parsed_genres'] = df[genre_col].apply(parse_list_column)
    else:
        df['parsed_genres'] = [[] for _ in range(len(df))]
        
    country_col = 'Country' if 'Country' in df.columns else ('countriesOfOrigin' if 'countriesOfOrigin' in df.columns else None)
    if country_col:
        df['parsed_countries'] = df[country_col].apply(parse_list_column)
    else:
        df['parsed_countries'] = [[] for _ in range(len(df))]

    # Numeric formatting
    df['averageRating'] = pd.to_numeric(df.get('averageRating', pd.Series()), errors='coerce')
    df['numVotes'] = pd.to_numeric(df.get('numVotes', pd.Series()), errors='coerce')
    df['grossWorldwide'] = pd.to_numeric(df.get('grossWorldwide', pd.Series()), errors='coerce').fillna(0)
    
    return df

# Load the dataset
df = load_dataset(DATASET_FILENAME)

# ---------------------------------------------------------
# SIDEBAR: DATASET METADATA, STUDENT DETAILS & BOTTOM NOTE
# ---------------------------------------------------------
with st.sidebar:
    # ℹ️ Dataset Metadata
    st.header("ℹ️ Dataset Metadata")
    st.write(f"**Rows:** {df.shape[0]}")
    st.write(f"**Columns:** {df.shape[1]}")
    
    with st.expander("🔍 Metadata & Missing Values"):
        st.subheader("Data Types")
        st.write(df.dtypes.astype(str))
        st.subheader("Missing Values")
        st.write(df.isnull().sum())
        
    st.divider()

    # 🎓 Student Details
    st.header("IMDB")
    st.markdown("👤RATINGS")
    st.markdown("🏫 WORLD")
    st.markdown("📌ENTERTAINMENT")

    st.divider()

    # 📝 Bottom Note Box (Matching screenshot styling exactly)
    st.markdown("""
    <div style="background-color: #f0ecfc; border: 1px solid #d0c4f7; border-radius: 10px; padding: 12px; margin-top: 15px;">
        <p style="margin: 0; color: #4a154b; font-weight: bold; font-size: 15px;">📝 Note: Created by Pathangi Mokshagna Rao</p>
        <p style="margin: 6px 0 0 0; color: #222222; font-size: 14px;"><b>PRN No:</b> 250200091</p>
        <p style="margin: 3px 0 0 0; color: #222222; font-size: 14px;"><b>Date:</b> 06-11-2026</p>
    </div>
    """, unsafe_allow_html=True)

# Success Message
st.success("✅ Dataset loaded successfully!")

# Section A - First 10 Records Expander
with st.expander("📄 Section A: First 10 Dataset Records", expanded=False):
    st.dataframe(df.head(10), use_container_width=True)

st.divider()

# ---------------------------------------------------------
# MAIN NAVIGATION TABS
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "🔍 Interactive Explorer", "🔎 Movie Search (Form & State)"])

# ---------------------------------------------------------
# TAB 1: SECTION B – MOVIE ANALYTICS DASHBOARD (18 MARKS)
# ---------------------------------------------------------
with tab1:
    st.header("📊 Movie Analytics Dashboard")
    
    # KPI Metrics (7 Marks)
    total_movies = len(df)
    avg_rating = df['averageRating'].mean()
    max_rating = df['averageRating'].max()
    total_votes = df['numVotes'].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Movies", value=f"{total_movies:,}")
    col2.metric(label="Average Rating", value=f"{avg_rating:.2f}")
    col3.metric(label="Highest Rating", value=f"{max_rating:.1f}")
    col4.metric(label="Total Votes", value=f"{total_votes:,.0f}")

    st.divider()

    # Data Visualizations (8 Marks)
    st.subheader("📈 Data Visualizations")
    
    vis_col1, vis_col2 = st.columns(2)
    
    with vis_col1:
        st.markdown("### 🎬 Movies by Genre")
        all_genres_series = df['parsed_genres'].explode().str.strip().dropna()
        genre_counts = all_genres_series.value_counts()
        st.bar_chart(genre_counts)
        
    with vis_col2:
        st.markdown("### 📊 IMDb Rating Distribution")
        counts, bin_edges = np.histogram(df['averageRating'].dropna(), bins=10)
        hist_df = pd.DataFrame(
            {'Movie Count': counts},
            index=[f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(counts))]
        )
        st.bar_chart(hist_df)

    vis_col3, vis_col4 = st.columns(2)
    
    with vis_col3:
        st.markdown("### 🔀 Rating vs Number of Votes")
        scatter_data = df[['averageRating', 'numVotes']].dropna()
        st.scatter_chart(scatter_data, x='averageRating', y='numVotes')

    with vis_col4:
        st.markdown("### 🏆 Top 10 Movies by Worldwide Gross ($)")
        top_10_gross = df.sort_values(by='grossWorldwide', ascending=False).head(10)
        title_col = 'Title' if 'Title' in df.columns else df.columns[0]
        top_10_chart = top_10_gross.set_index(title_col)['grossWorldwide']
        st.bar_chart(top_10_chart)

# ---------------------------------------------------------
# TAB 2: SECTION C – INTERACTIVE MOVIE EXPLORER (12 MARKS)
# ---------------------------------------------------------
with tab2:
    st.header("🔍 Interactive Movie Explorer")
    
    flat_genres = sorted(list(set([g for sublist in df['parsed_genres'] for g in sublist if g])))
    flat_countries = sorted(list(set([c for sublist in df['parsed_countries'] for c in sublist if c])))

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        selected_genre = st.selectbox("Select Genre", options=["All"] + flat_genres)
        selected_countries = st.multiselect("Select Countries", options=flat_countries)

    with filter_col2:
        min_r = float(df['averageRating'].min())
        max_r = float(df['averageRating'].max())
        rating_range = st.slider("IMDb Rating Range", min_value=min_r, max_value=max_r, value=(min_r, max_r), step=0.1)
        
        min_v = int(df['numVotes'].min())
        max_v = int(df['numVotes'].max())
        min_votes_input = st.number_input("Minimum Votes", min_value=0, max_value=max_v, value=min_v, step=50000)

    with filter_col3:
        search_title = st.text_input("Search Title", value="")
        sort_order = st.radio("Sort Rating By", options=["Descending", "Ascending"])
        reset_pressed = st.button("🔄 Reset Filters")

    if reset_pressed:
        st.rerun()

    # Filtering Logic
    filtered_df = df.copy()

    if selected_genre != "All":
        filtered_df = filtered_df[filtered_df['parsed_genres'].apply(lambda g_list: selected_genre in g_list)]

    if selected_countries:
        filtered_df = filtered_df[filtered_df['parsed_countries'].apply(lambda c_list: any(c in c_list for c in selected_countries))]

    filtered_df = filtered_df[
        (filtered_df['averageRating'] >= rating_range[0]) & 
        (filtered_df['averageRating'] <= rating_range[1]) &
        (filtered_df['numVotes'] >= min_votes_input)
    ]

    title_field = 'Title' if 'Title' in df.columns else df.columns[0]
    if search_title.strip():
        filtered_df = filtered_df[filtered_df[title_field].astype(str).str.contains(search_title.strip(), case=False, na=False)]

    ascending_bool = (sort_order == "Ascending")
    filtered_df = filtered_df.sort_values(by='averageRating', ascending=ascending_bool)

    st.info(f"📌 **Filtered Records Count:** {len(filtered_df)} movie(s) found.")
    st.dataframe(filtered_df, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: SECTION C – SESSION STATE & FORM HANDLING (10 MARKS)
# ---------------------------------------------------------
with tab3:
    st.header("🔎 Movie Search (Form & Session State)")
    
    if 'selected_movie' not in st.session_state:
        st.session_state.selected_movie = None

    with st.form(key="movie_search_form"):
        st.subheader("Movie Search Preferences")
        form_title = st.text_input("Movie Title (Optional Keyword)")
        form_genre = st.selectbox("Preferred Genre", options=["Any"] + flat_genres)
        form_min_rating = st.slider("Minimum IMDb Rating", min_value=1.0, max_value=10.0, value=8.0, step=0.1)
        
        submitted = st.form_submit_button("Search Movie")

    if submitted:
        search_res = df.copy()
        search_res = search_res[search_res['averageRating'] >= form_min_rating]
        
        if form_genre != "Any":
            search_res = search_res[search_res['parsed_genres'].apply(lambda g_list: form_genre in g_list)]
            
        title_field = 'Title' if 'Title' in df.columns else df.columns[0]
        if form_title.strip() != "":
            search_res = search_res[search_res[title_field].astype(str).str.contains(form_title.strip(), case=False, na=False)]

        if not search_res.empty:
            st.session_state.selected_movie = search_res.iloc[0].to_dict()
            st.success("🎉 Matching movie found!")
        else:
            st.session_state.selected_movie = None
            st.info("ℹ️ No movie matches the specified criteria. Try broadening your search!")

    if st.session_state.selected_movie is not None:
        st.subheader("⭐ Search Result Details (Persisted in Session State)")
        movie = st.session_state.selected_movie
        
        res_col1, res_col2 = st.columns(2)
        title_field = 'Title' if 'Title' in movie else list(movie.keys())[0]
        with res_col1:
            st.metric(label="Title", value=str(movie[title_field]))
            st.metric(label="IMDb Rating", value=f"{movie['averageRating']}")
        with res_col2:
            st.write(f"**Genre:** {movie.get('Genre', movie.get('genres', 'N/A'))}")
            st.write(f"**Country:** {movie.get('Country', movie.get('countriesOfOrigin', 'N/A'))}")
            st.write(f"**Number of Votes:** {int(movie['numVotes']):,}")
            st.write(f"**Worldwide Gross:** ${int(movie['grossWorldwide']):,}")
