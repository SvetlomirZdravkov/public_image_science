import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Public Images of Science in Bulgaria",
    layout="wide"
)

st.title("Public Images of Science in Bulgaria (2011–2024)")
st.caption("Interactive dashboard for exploring topics, tone, and trends in digital media content.")

@st.cache_data
def load_data():
    # If you later switch to CSV, replace with:
    # return pd.read_csv("data.csv")
    df = pd.read_excel("data.xlsx")
    return df

df = load_data()

# ---------- Basic cleanup ----------
if "DatePosted" in df.columns:
    df["DatePosted"] = pd.to_datetime(df["DatePosted"], errors="coerce")
    df["Year"] = df["DatePosted"].dt.year

if "Length" in df.columns:
    df["Length"] = pd.to_numeric(df["Length"], errors="coerce")

if "Probability" in df.columns:
    df["Probability"] = pd.to_numeric(df["Probability"], errors="coerce")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

# Year filter
if "Year" in df.columns and df["Year"].notna().any():
    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())
    year_range = st.sidebar.slider(
        "Year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
    df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

# Topic filter
if "Topic" in df.columns:
    topic_options = sorted(df["Topic"].dropna().astype(str).unique().tolist())
    selected_topics = st.sidebar.multiselect("Topic", topic_options, default=topic_options)
    if selected_topics:
        df = df[df["Topic"].astype(str).isin(selected_topics)]

# Tone filter
if "Tone" in df.columns:
    tone_options = sorted(df["Tone"].dropna().astype(str).unique().tolist())
    selected_tones = st.sidebar.multiselect("Tone", tone_options, default=tone_options)
    if selected_tones:
        df = df[df["Tone"].astype(str).isin(selected_tones)]

# Source / article title filter
if "ArticleTitle" in df.columns:
    search_title = st.sidebar.text_input("Search in article title")
    if search_title:
        df = df[df["ArticleTitle"].astype(str).str.contains(search_title, case=False, na=False)]

# Free text search in content
if "Content" in df.columns:
    search_text = st.sidebar.text_input("Search in content")
    if search_text:
        df = df[df["Content"].astype(str).str.contains(search_text, case=False, na=False)]

# ---------- Top metrics ----------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Records", f"{len(df):,}")

if "ArticleId" in df.columns:
    c2.metric("Unique articles", f"{df['ArticleId'].nunique():,}")
else:
    c2.metric("Unique articles", "—")

if "Topic" in df.columns and len(df) > 0:
    c3.metric("Topics", f"{df['Topic'].nunique():,}")
else:
    c3.metric("Topics", "—")

if "Length" in df.columns and df["Length"].notna().any():
    c4.metric("Avg. length", f"{df['Length'].mean():.1f}")
else:
    c4.metric("Avg. length", "—")

st.markdown("---")

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Topics",
    "Tone",
    "Trends",
    "Data Explorer"
])

# ---------- Tab 1: Overview ----------
with tab1:
    st.subheader("Overview")

    col1, col2 = st.columns(2)

    if "Topic" in df.columns and len(df) > 0:
        topic_counts = df["Topic"].astype(str).value_counts().reset_index()
        topic_counts.columns = ["Topic", "Count"]
        fig = px.bar(topic_counts, x="Topic", y="Count", title="Topic distribution")
        col1.plotly_chart(fig, use_container_width=True)

    if "Tone" in df.columns and len(df) > 0:
        tone_counts = df["Tone"].astype(str).value_counts().reset_index()
        tone_counts.columns = ["Tone", "Count"]
        fig2 = px.pie(tone_counts, names="Tone", values="Count", title="Tone distribution")
        col2.plotly_chart(fig2, use_container_width=True)

    if "Representative_document" in df.columns:
        rep_count = df["Representative_document"].astype(str).value_counts(dropna=False).reset_index()
        rep_count.columns = ["Representative_document", "Count"]
        st.write("Representative document flag")
        st.dataframe(rep_count, use_container_width=True)

# ---------- Tab 2: Topics ----------
with tab2:
    st.subheader("Topic analysis")

    if "Topic" in df.columns:
        topic_summary = df.groupby("Topic").size().reset_index(name="Count").sort_values("Count", ascending=False)
        st.dataframe(topic_summary, use_container_width=True)

        selected_topic = st.selectbox(
            "Select a topic to inspect",
            topic_summary["Topic"].astype(str).tolist() if len(topic_summary) > 0 else []
        )

        if selected_topic:
            topic_df = df[df["Topic"].astype(str) == str(selected_topic)]

            col1, col2 = st.columns(2)

            if "Top_n_words" in topic_df.columns:
                top_words = topic_df["Top_n_words"].dropna().astype(str).value_counts().reset_index()
                top_words.columns = ["Top_n_words", "Count"]
                col1.write("Top words / labels")
                col1.dataframe(top_words.head(20), use_container_width=True)

            if "Probability" in topic_df.columns and topic_df["Probability"].notna().any():
                fig_prob = px.histogram(
                    topic_df,
                    x="Probability",
                    nbins=30,
                    title=f"Probability distribution for topic: {selected_topic}"
                )
                col2.plotly_chart(fig_prob, use_container_width=True)

            preview_cols = [c for c in [
                "Id", "ArticleTitle", "DatePosted", "Tone", "Probability",
                "Topic", "Top_n_words", "Representative_document", "CommentLink"
            ] if c in topic_df.columns]

            if preview_cols:
                st.write("Sample records")
                st.dataframe(topic_df[preview_cols].head(50), use_container_width=True)

# ---------- Tab 3: Tone ----------
with tab3:
    st.subheader("Tone analysis")

    if "Tone" in df.columns:
        tone_counts = df["Tone"].astype(str).value_counts().reset_index()
        tone_counts.columns = ["Tone", "Count"]
        fig_tone = px.bar(tone_counts, x="Tone", y="Count", title="Tone counts")
        st.plotly_chart(fig_tone, use_container_width=True)

        if "Topic" in df.columns:
            tone_topic = (
                df.groupby(["Topic", "Tone"])
                .size()
                .reset_index(name="Count")
            )
            fig_heat = px.density_heatmap(
                tone_topic,
                x="Topic",
                y="Tone",
                z="Count",
                title="Tone by topic"
            )
            st.plotly_chart(fig_heat, use_container_width=True)

# ---------- Tab 4: Trends ----------
with tab4:
    st.subheader("Trends over time")

    if "Year" in df.columns and df["Year"].notna().any():
        yearly = df.groupby("Year").size().reset_index(name="Count")
        fig_year = px.line(yearly, x="Year", y="Count", markers=True, title="Records per year")
        st.plotly_chart(fig_year, use_container_width=True)

        if "Topic" in df.columns:
            topic_year = (
                df.groupby(["Year", "Topic"])
                .size()
                .reset_index(name="Count")
            )
            fig_topic_year = px.line(
                topic_year,
                x="Year",
                y="Count",
                color="Topic",
                title="Topic trends over time"
            )
            st.plotly_chart(fig_topic_year, use_container_width=True)

        if "Tone" in df.columns:
            tone_year = (
                df.groupby(["Year", "Tone"])
                .size()
                .reset_index(name="Count")
            )
            fig_tone_year = px.line(
                tone_year,
                x="Year",
                y="Count",
                color="Tone",
                title="Tone trends over time"
            )
            st.plotly_chart(fig_tone_year, use_container_width=True)

# ---------- Tab 5: Data Explorer ----------
with tab5:
    st.subheader("Data explorer")

    display_columns = [c for c in [
        "Id", "DatePosted", "ArticleTitle", "Author", "Tone", "Topic",
        "Top_n_words", "Probability", "Length", "CommentLink"
    ] if c in df.columns]

    if display_columns:
        st.dataframe(df[display_columns], use_container_width=True)
    else:
        st.dataframe(df.head(100), use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="filtered_public_image_science.csv",
        mime="text/csv"
    )
