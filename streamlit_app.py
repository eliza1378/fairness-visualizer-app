import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go

def drawCountryMap(df):
    authorCountries = df["Country"].to_list()
    authorDict = {i: authorCountries.count(i) for i in set(authorCountries)}

    data = dict(
        type='choropleth',
        locations=list(authorDict.keys()),
        locationmode='country names',
        colorscale='purp',
        text=list(authorDict.keys()),
        z=list(authorDict.values()),
        colorbar={
            'title': 'Author Count',
            'len': 1,
            'lenmode': 'fraction'
        }
    )

    layout = dict(geo={'scope': 'world'})

    fig = go.Figure(data=[data], layout=layout)
    fig.update_layout(
        title={
            'text': 'Author Distribution by Country',
            'x': 0.5,  # Center the title
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16}  # Adjust the font size as needed
        },
        autosize=True,
    )
    
    fig.update_geos(framewidth=0)
    fig.update_geos(
        showcountries=True,
    )

    st.plotly_chart(fig)

# Title of the app
st.title('Fairness Visualizer App')

df = pd.read_csv("data/anonymizedLLM.csv")

drawCountryMap(df)