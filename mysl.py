import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

DATE_TIME = "timestart"
st.title('Streamlit Bangkok')

"""
## An example of geographic data in Bangkok
"""

@st.cache(persist=True,allow_output_mutation=True)
def load_data(nrows):
    df1 = pd.read_csv('https://raw.githubusercontent.com/Maplub/odsample/master/20190101.csv',header=0)
    df2 = pd.read_csv('https://raw.githubusercontent.com/Maplub/odsample/master/20190102.csv',header=1)
    df3 = pd.read_csv('https://raw.githubusercontent.com/Maplub/odsample/master/20190103.csv',header=1)
    df4 = pd.read_csv('https://raw.githubusercontent.com/Maplub/odsample/master/20190104.csv',header=1)
    df5 = pd.read_csv('https://raw.githubusercontent.com/Maplub/odsample/master/20190105.csv',header=1)
    f=[df1,df2,df3,df4,df5]
    data = pd.concat(f)
    data=data.iloc[:,0:7]
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    return data

data = load_data(379772)

sel = st.selectbox("Start/Stop", options=['start','stop'])
if sel == 'start':
    lat_m="latstartl";lon_m="lonstartl";DATE_TIME = "timestart";
else:
    lat_m="latstop";lon_m="lonstop";DATE_TIME = "timestop";


hour = st.slider("Hour to look at", 0, 23, step=3)
data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
data = data[(data[DATE_TIME].dt.hour>=hour) & (data[DATE_TIME].dt.hour< hour+3)]

st.subheader("Geo data between %i:00 and %i:00" % (hour, (hour + 3) % 24))
midpoint = (np.average(data[lat_m]), np.average(data[lon_m]))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 10,
        "pitch": 50
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data,
            get_position=[lon_m, lat_m],
            radius=100,
            elevation_scale=10,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 3) % 24))
filtered = data[
    (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 3))
]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ), use_container_width=True)

if st.checkbox("Show raw data", False):
    st.subheader("Raw data by minute between %i:00 and %i:00" % (hour, (hour + 3) % 24))
    st.write(data)
"""
## ref. https://github.com/streamlit/demo-uber-nyc-pickups
"""
