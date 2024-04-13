import pandas as pd
import streamlit as st
import altair as alt
import requests

st.title('Historical Name Popularity')
st.write("by Conner Drake")
st.write("")

@st.cache_data
def get_name_data():
    df = pd.read_csv("popular_names.csv")
    return df.pivot_table(
        index='year',
        columns='name',
        values='n',
        aggfunc='sum',
        fill_value=0
    )

df = get_name_data()
names = st.multiselect(
    "Choose Names", options=[col for col in df.columns], default=["Harry", "Gertrude", "Alberta"]
)

if not names:
    st.error("Please select at least one name.")
else:
    data = df.reset_index()[['year'] + names]
    data['year'] = data['year'].astype(str)
    data_long = data.melt('year', var_name='name', value_name='n')

    data_wide_for_download = data_long.pivot(index='year', columns='name', values='n').reset_index()
    data_wide_for_download.columns.name = None  # Remove the index name
    data_wide_for_download = data_wide_for_download.rename(columns=lambda x: x if x == 'year' else x + '_count')

    chart = alt.Chart(data_long).mark_bar(opacity=0.3).encode(
        x='year:O',
        y=alt.Y('n:Q', title='Frequency'),
        color='name:N',
        tooltip=['name', 'n', 'year:O']
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    # filtered data to CSV
    csv = data_wide_for_download.to_csv(index=False)
    
    # download button
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="name_frequencies.csv",
        mime='text/csv',
    )

    # download all name data
    all_data_url = "https://raw.githubusercontent.com/esnt/Data/main/Names/popular_names.csv"
    all_data = requests.get(all_data_url).content
    st.download_button(
        label="Download All Name Data",
        data=all_data,
        file_name="all_name_data.csv",
        mime='text/csv'
    )

    with st.expander("More Information"):
        st.write("This chart displays how many newborns were given the selected name(s) within each year since 1910. Add multiple names to compare trends over time!\n\nClick the \"Download CSV\" button to get a CSV with the data for the selected name(s).\n\nExample:")
        st.image("csv-example.png", caption="Downloadable CSV with selected data")
