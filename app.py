import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Global Temperature Dashboard",
    page_icon="🌍",
    layout="wide"
)


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ZIP_FILE = (
    BASE_DIR
    / "data"
    / "GlobalLandTemperaturesByCity.csv.zip"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 35px;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            #0f172a,
            #1d4ed8
        );
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        font-size: 40px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 17px;
        opacity: 0.9;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CHECK ZIP
# ============================================================

if not ZIP_FILE.exists():

    st.error("❌ ZIP file not found.")

    st.code(
        str(ZIP_FILE)
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

    <h1>🌍 Global Land Temperature</h1>

    <p>
    Explore historical temperature patterns across
    cities and countries worldwide.
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# READ COUNTRIES ONLY
# ============================================================

@st.cache_data
def get_countries():

    countries = set()

    for chunk in pd.read_csv(
        ZIP_FILE,
        compression="zip",
        usecols=["Country"],
        chunksize=20000
    ):

        countries.update(
            chunk["Country"]
            .dropna()
            .unique()
        )

    return sorted(countries)


# ============================================================
# COUNTRIES
# ============================================================

with st.spinner(
    "🌎 Reading countries..."
):

    countries = get_countries()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🎛️ Filters"
)

st.sidebar.markdown("---")


selected_country = st.sidebar.selectbox(
    "🌎 Country",
    ["All Countries"] + countries
)


# ============================================================
# GET CITIES
# ============================================================

@st.cache_data
def get_cities(country):

    cities = set()

    for chunk in pd.read_csv(
        ZIP_FILE,
        compression="zip",
        usecols=["City", "Country"],
        chunksize=20000
    ):

        if country != "All Countries":

            chunk = chunk[
                chunk["Country"] == country
            ]

        cities.update(
            chunk["City"]
            .dropna()
            .unique()
        )

    return sorted(cities)


with st.spinner(
    "🏙️ Reading cities..."
):

    cities = get_cities(
        selected_country
    )


selected_city = st.sidebar.selectbox(
    "🏙️ City",
    ["All Cities"] + cities
)


# ============================================================
# GET YEARS
# ============================================================

@st.cache_data
def get_years():

    years = set()

    for chunk in pd.read_csv(
        ZIP_FILE,
        compression="zip",
        usecols=["dt"],
        chunksize=20000
    ):

        dates = pd.to_datetime(
            chunk["dt"],
            errors="coerce"
        )

        years.update(
            dates.dt.year
            .dropna()
            .astype(int)
            .unique()
        )

    return sorted(years)


with st.spinner(
    "📅 Reading years..."
):

    years = get_years()


selected_year = st.sidebar.selectbox(
    "📅 Year",
    ["All Years"] + years
)


# ============================================================
# LOAD ONLY SELECTED DATA
# ============================================================

def load_selected_data(
    country,
    city,
    year
):

    columns = [
        "dt",
        "AverageTemperature",
        "AverageTemperatureUncertainty",
        "City",
        "Country",
        "Latitude",
        "Longitude"
    ]

    results = []

    for chunk in pd.read_csv(
        ZIP_FILE,
        compression="zip",
        usecols=columns,
        chunksize=20000
    ):

        # Country

        if country != "All Countries":

            chunk = chunk[
                chunk["Country"] == country
            ]

        # City

        if city != "All Cities":

            chunk = chunk[
                chunk["City"] == city
            ]

        # If nothing remains, skip

        if len(chunk) == 0:

            continue

        # Date

        chunk["dt"] = pd.to_datetime(
            chunk["dt"],
            errors="coerce"
        )

        # Year

        if year != "All Years":

            chunk = chunk[
                chunk["dt"].dt.year == year
            ]

        if len(chunk) > 0:

            results.append(
                chunk
            )

    if results:

        return pd.concat(
            results,
            ignore_index=True
        )

    return pd.DataFrame(
        columns=columns
    )


# ============================================================
# LOAD BUTTON
# ============================================================

st.sidebar.markdown("---")

load_button = st.sidebar.button(
    "🔎 Load Selected Data",
    type="primary",
    use_container_width=True
)


# ============================================================
# DEFAULT
# ============================================================

if "selected_data" not in st.session_state:

    st.session_state.selected_data = (
        pd.DataFrame()
    )


# ============================================================
# LOAD
# ============================================================

if load_button:

    with st.spinner(
        "🔄 Searching the ZIP dataset..."
    ):

        st.session_state.selected_data = (
            load_selected_data(
                selected_country,
                selected_city,
                selected_year
            )
        )


df = st.session_state.selected_data


# ============================================================
# BEFORE DATA
# ============================================================

if df.empty:

    st.info(
        """
        👈 Select your Country, City and Year
        from the sidebar, then click:

        **🔎 Load Selected Data**
        """
    )

    st.markdown("---")

    st.subheader(
        "📌 How this application works"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            """
            ### 1️⃣ Select

            Choose a country, city and year.
            """
        )

    with c2:

        st.markdown(
            """
            ### 2️⃣ Load

            The app searches the ZIP file
            without loading the complete dataset.
            """
        )

    with c3:

        st.markdown(
            """
            ### 3️⃣ Analyze

            View temperature trends,
            statistics and locations.
            """
        )

    st.stop()


# ============================================================
# TEMPERATURE
# ============================================================

temperature = (
    pd.to_numeric(
        df["AverageTemperature"],
        errors="coerce"
    )
    .dropna()
)


# ============================================================
# METRICS
# ============================================================

st.subheader(
    "📊 Temperature Overview"
)

m1, m2, m3, m4 = st.columns(4)


with m1:

    st.metric(
        "🌡️ Average",
        f"{temperature.mean():.2f} °C"
    )


with m2:

    st.metric(
        "🔥 Maximum",
        f"{temperature.max():.2f} °C"
    )


with m3:

    st.metric(
        "❄️ Minimum",
        f"{temperature.min():.2f} °C"
    )


with m4:

    st.metric(
        "📊 Records",
        f"{len(df):,}"
    )


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Trends",
        "🌡️ Analysis",
        "🗺️ Map",
        "📋 Data"
    ]
)


# ============================================================
# TREND
# ============================================================

with tab1:

    st.subheader(
        "📈 Temperature Trend"
    )

    chart_df = df.copy()

    chart_df["dt"] = pd.to_datetime(
        chart_df["dt"],
        errors="coerce"
    )

    chart_df["AverageTemperature"] = pd.to_numeric(
        chart_df["AverageTemperature"],
        errors="coerce"
    )

    chart_df = chart_df.dropna(
        subset=[
            "dt",
            "AverageTemperature"
        ]
    )

    if len(chart_df) > 0:

        monthly = (
            chart_df
            .groupby(
                chart_df["dt"].dt.month
            )["AverageTemperature"]
            .mean()
            .reset_index()
        )

        monthly.columns = [
            "Month",
            "Temperature"
        ]

        fig, ax = plt.subplots(
            figsize=(12, 5)
        )

        ax.plot(
            monthly["Month"],
            monthly["Temperature"],
            marker="o",
            linewidth=2
        )

        ax.set_xlabel(
            "Month"
        )

        ax.set_ylabel(
            "Temperature (°C)"
        )

        ax.set_title(
            "Average Monthly Temperature"
        )

        ax.set_xticks(
            range(1, 13)
        )

        ax.grid(
            alpha=0.25
        )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        plt.close(fig)


# ============================================================
# ANALYSIS
# ============================================================

with tab2:

    st.subheader(
        "🌡️ Temperature Distribution"
    )

    if len(temperature) > 0:

        fig, ax = plt.subplots(
            figsize=(12, 5)
        )

        ax.hist(
            temperature,
            bins=30
        )

        ax.set_xlabel(
            "Temperature (°C)"
        )

        ax.set_ylabel(
            "Frequency"
        )

        ax.set_title(
            "Temperature Distribution"
        )

        ax.grid(
            alpha=0.2
        )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        plt.close(fig)


# ============================================================
# MAP
# ============================================================

# ============================================================
# MAP
# ============================================================

with tab3:

    st.subheader(
        "🗺️ Geographic Location"
    )

    map_df = df[
        [
            "Latitude",
            "Longitude"
        ]
    ].copy()


    # Convert coordinates such as 36.35N / 75.59E
    # into numbers

    def convert_coordinate(value):

        if pd.isna(value):
            return None

        value = str(value).strip()

        if len(value) == 0:
            return None

        direction = value[-1].upper()

        try:
            number = float(value[:-1])
        except ValueError:
            return None

        # South and West are negative

        if direction in ["S", "W"]:
            number = -number

        return number


    # Convert Latitude

    map_df["Latitude"] = (
        map_df["Latitude"]
        .apply(convert_coordinate)
    )


    # Convert Longitude

    map_df["Longitude"] = (
        map_df["Longitude"]
        .apply(convert_coordinate)
    )


    # Remove invalid coordinates

    map_df = map_df.dropna(
        subset=[
            "Latitude",
            "Longitude"
        ]
    )


    # Rename columns for Streamlit

    map_df = map_df.rename(
        columns={
            "Latitude": "latitude",
            "Longitude": "longitude"
        }
    )


    # Remove duplicate locations

    map_df = map_df.drop_duplicates()


    # Display map

    if len(map_df) > 0:

        st.map(
            map_df,
            latitude="latitude",
            longitude="longitude",
            height=600
        )

        st.success(
            f"🗺️ Showing {len(map_df):,} locations"
        )

    else:

        st.warning(
            "No valid coordinates were found."
        )
# ============================================================
# DATA
# ============================================================

with tab4:

    st.subheader(
        "📋 Selected Data"
    )

    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )

    csv = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Selected Data",
        csv,
        "temperature_data.csv",
        "text/csv",
        use_container_width=True
    )


# ============================================================
# ML
# ============================================================

st.markdown("---")

st.subheader(
    "🤖 Machine Learning Prediction"
)

st.info(
    """
    The prediction section can be connected to your
    trained `.joblib` model. Your ZIP dataset remains
    unchanged.
    """
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "🌍 Global Land Temperature Prediction | "
    "Streamlit • Pandas • Machine Learning"
)