import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import matplotlib.patches as mpatches
import mpld3
import streamlit.components.v1 as components
import seaborn as sns
import plotly.express as px
from scipy.stats import gaussian_kde
import networkx as nx


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

    st.plotly_chart(fig, use_container_width=True)

def calculateRecallPrecision(df):
  df["Recall 50%"] = 0
  df["Recall 60%"] = 0
  df["Recall 70%"] = 0
  df["Recall 80%"] = 0

  df["Precision 50%"] = 0
  df["Precision 60%"] = 0
  df["Precision 70%"] = 0
  df["Precision 80%"] = 0

  for index, row in df.iterrows():
    df.at[index, "Recall 50%"] = row["Match Count 50%"] / len(row["Co-authors’ genders (Google Scholar)"].split(", "))
    df.at[index, "Recall 60%"] = row["Match Count 60%"] / len(row["Co-authors’ genders (Google Scholar)"].split(", "))
    df.at[index, "Recall 70%"] = row["Match Count 70%"] / len(row["Co-authors’ genders (Google Scholar)"].split(", "))
    df.at[index, "Recall 80%"] = row["Match Count 80%"] / len(row["Co-authors’ genders (Google Scholar)"].split(", "))

    df.at[index, "Precision 50%"] = row["Match Count 50%"] / len(row["Co-authors’ genders (OpenAI)"].split(", "))
    df.at[index, "Precision 60%"] = row["Match Count 60%"] / len(row["Co-authors’ genders (OpenAI)"].split(", "))
    df.at[index, "Precision 70%"] = row["Match Count 70%"] / len(row["Co-authors’ genders (OpenAI)"].split(", "))
    df.at[index, "Precision 80%"] = row["Match Count 80%"] / len(row["Co-authors’ genders (OpenAI)"].split(", "))

  return df

def drawEthnicityDP(df):    
    asian_white_DP = []
    black_white_DP = []
    hispanic_white_DP = []
    non_white_white_DP = []

    asian_white_DP.append(df[df["Ethnicity"] == "Asian"]["Recall 50%"].mean() / df[df["Ethnicity"] == "White"]["Recall 50%"].mean())
    asian_white_DP.append(df[df["Ethnicity"] == "Asian"]["Recall 60%"].mean() / df[df["Ethnicity"] == "White"]["Recall 60%"].mean())
    asian_white_DP.append(df[df["Ethnicity"] == "Asian"]["Recall 70%"].mean() / df[df["Ethnicity"] == "White"]["Recall 70%"].mean())
    asian_white_DP.append(df[df["Ethnicity"] == "Asian"]["Recall 80%"].mean() / df[df["Ethnicity"] == "White"]["Recall 80%"].mean())

    black_white_DP.append(df[df["Ethnicity"] == "Black"]["Recall 50%"].mean() / df[df["Ethnicity"] == "White"]["Recall 50%"].mean())
    black_white_DP.append(df[df["Ethnicity"] == "Black"]["Recall 60%"].mean() / df[df["Ethnicity"] == "White"]["Recall 60%"].mean())
    black_white_DP.append(df[df["Ethnicity"] == "Black"]["Recall 70%"].mean() / df[df["Ethnicity"] == "White"]["Recall 70%"].mean())
    black_white_DP.append(df[df["Ethnicity"] == "Black"]["Recall 80%"].mean() / df[df["Ethnicity"] == "White"]["Recall 80%"].mean())

    hispanic_white_DP.append(df[df["Ethnicity"] == "Hispanic"]["Recall 50%"].mean() / df[df["Ethnicity"] == "White"]["Recall 50%"].mean())
    hispanic_white_DP.append(df[df["Ethnicity"] == "Hispanic"]["Recall 60%"].mean() / df[df["Ethnicity"] == "White"]["Recall 60%"].mean())
    hispanic_white_DP.append(df[df["Ethnicity"] == "Hispanic"]["Recall 70%"].mean() / df[df["Ethnicity"] == "White"]["Recall 70%"].mean())
    hispanic_white_DP.append(df[df["Ethnicity"] == "Hispanic"]["Recall 80%"].mean() / df[df["Ethnicity"] == "White"]["Recall 80%"].mean())

    non_white_white_DP.append(df[df["Ethnicity"] != "White"]["Recall 50%"].mean() / df[df["Ethnicity"] == "White"]["Recall 50%"].mean())
    non_white_white_DP.append(df[df["Ethnicity"] != "White"]["Recall 60%"].mean() / df[df["Ethnicity"] == "White"]["Recall 60%"].mean())
    non_white_white_DP.append(df[df["Ethnicity"] != "White"]["Recall 70%"].mean() / df[df["Ethnicity"] == "White"]["Recall 70%"].mean())
    non_white_white_DP.append(df[df["Ethnicity"] != "White"]["Recall 80%"].mean() / df[df["Ethnicity"] == "White"]["Recall 80%"].mean())
    
    xi = [0.5, 0.6, 0.7, 0.8]

    fig = go.Figure()

    # Add traces
    fig.add_trace(go.Scatter(x=xi, y=asian_white_DP, mode='lines+markers', name='Asian / White', line=dict(color='goldenrod', dash='dash')))
    fig.add_trace(go.Scatter(x=xi, y=black_white_DP, mode='lines+markers', name='Black / White', line=dict(color='#0047AB', dash='dash')))
    fig.add_trace(go.Scatter(x=xi, y=hispanic_white_DP, mode='lines+markers', name='Hispanic / White', line=dict(color='#FE828C', dash='dash')))
    fig.add_trace(go.Scatter(x=xi, y=non_white_white_DP, mode='lines+markers', name='Non-White / White', line=dict(color='#FF00FF', dash='dash')))

    # Update layout
    fig.update_layout(
        title={
            'text': 'Demographic Parity for Different Ethnic Groups',
            'x': 0.5,  # Center the title
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16}  # Adjust the font size as needed
        },
        xaxis_title='Epsilon',
        yaxis_title='Demographic Parity',
        xaxis=dict(tickmode='array', tickvals=xi, ticktext=xi),
        yaxis=dict(tickmode='array', tickvals=[0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4]),
        legend=dict(font=dict(size=12)),
        template='seaborn',
        autosize=True,
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def drawEthnicityPE(df):    
    asian_white_PE = []
    black_white_PE = []
    hispanic_white_PE = []
    non_white_white_PE = []

    asian_white_PE.append(df[df["Ethnicity"] == "Asian"]["Precision 50%"].mean() / df[df["Ethnicity"] == "White"]["Precision 50%"].mean())
    asian_white_PE.append(df[df["Ethnicity"] == "Asian"]["Precision 60%"].mean() / df[df["Ethnicity"] == "White"]["Precision 60%"].mean())
    asian_white_PE.append(df[df["Ethnicity"] == "Asian"]["Precision 70%"].mean() / df[df["Ethnicity"] == "White"]["Precision 70%"].mean())
    asian_white_PE.append(df[df["Ethnicity"] == "Asian"]["Precision 80%"].mean() / df[df["Ethnicity"] == "White"]["Precision 80%"].mean())

    black_white_PE.append(df[df["Ethnicity"] == "Black"]["Precision 50%"].mean() / df[df["Ethnicity"] == "White"]["Precision 50%"].mean())
    black_white_PE.append(df[df["Ethnicity"] == "Black"]["Precision 60%"].mean() / df[df["Ethnicity"] == "White"]["Precision 60%"].mean())
    black_white_PE.append(df[df["Ethnicity"] == "Black"]["Precision 70%"].mean() / df[df["Ethnicity"] == "White"]["Precision 70%"].mean())
    black_white_PE.append(df[df["Ethnicity"] == "Black"]["Precision 80%"].mean() / df[df["Ethnicity"] == "White"]["Precision 80%"].mean())

    hispanic_white_PE.append(df[df["Ethnicity"] == "Hispanic"]["Precision 50%"].mean() / df[df["Ethnicity"] == "White"]["Precision 50%"].mean())
    hispanic_white_PE.append(df[df["Ethnicity"] == "Hispanic"]["Precision 60%"].mean() / df[df["Ethnicity"] == "White"]["Precision 60%"].mean())
    hispanic_white_PE.append(df[df["Ethnicity"] == "Hispanic"]["Precision 70%"].mean() / df[df["Ethnicity"] == "White"]["Precision 70%"].mean())
    hispanic_white_PE.append(df[df["Ethnicity"] == "Hispanic"]["Precision 80%"].mean() / df[df["Ethnicity"] == "White"]["Precision 80%"].mean())

    non_white_white_PE.append(df[df["Ethnicity"] != "White"]["Precision 50%"].mean() / df[df["Ethnicity"] == "White"]["Precision 50%"].mean())
    non_white_white_PE.append(df[df["Ethnicity"] != "White"]["Precision 60%"].mean() / df[df["Ethnicity"] == "White"]["Precision 60%"].mean())
    non_white_white_PE.append(df[df["Ethnicity"] != "White"]["Precision 70%"].mean() / df[df["Ethnicity"] == "White"]["Precision 70%"].mean())
    non_white_white_PE.append(df[df["Ethnicity"] != "White"]["Precision 80%"].mean() / df[df["Ethnicity"] == "White"]["Precision 80%"].mean())
    
    xi = [0.5, 0.6, 0.7, 0.8]

    fig = go.Figure()

    # Add traces
    fig.add_trace(go.Scatter(x=xi, y=asian_white_PE, mode='lines+markers', name='Asian / White', line=dict(color='goldenrod', dash='dash')))
    fig.add_trace(go.Scatter(x=xi, y=black_white_PE, mode='lines+markers', name='Black / White', line=dict(color='#0047AB', dash='dash')))
    fig.add_trace(go.Scatter(x=xi, y=hispanic_white_PE, mode='lines+markers', name='Hispanic / White', line=dict(color='#FE828C', dash='dash')))
    fig.add_trace(go.Scatter(x=xi, y=non_white_white_PE, mode='lines+markers', name='Non-White / White', line=dict(color='#FF00FF', dash='dash')))

    # Update layout
    fig.update_layout(
        title={
            'text': 'Predictive Equality for Different Ethnic Groups',
            'x': 0.5,  # Center the title
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16}  # Adjust the font size as needed
        },
        xaxis_title='Epsilon',
        yaxis_title='Predictive Equality',
        xaxis=dict(tickmode='array', tickvals=xi, ticktext=xi),
        yaxis=dict(tickmode='array', tickvals=[0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]),
        legend=dict(font=dict(size=12)),
        template='seaborn',
        autosize=True,
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def drawGenderDiffRatio(df):
    for index, row in df.iterrows():
        scholarGenders = row["Co-authors’ genders (Google Scholar)"].split(", ")
        scholarRatio = scholarGenders.count("Female") / len(scholarGenders)

        gptGenders = row["Co-authors’ genders (OpenAI)"].split(", ")
        gptRatio = gptGenders.count("Female") / len(gptGenders)

        df.at[index, "Gender Diff Ratio"] = gptRatio - scholarRatio

    fig = px.histogram(df, x="Gender Diff Ratio", nbins=17, color_discrete_sequence=['khaki'])
    
    # Calculate the density curve
    x = df["Gender Diff Ratio"]
    density = gaussian_kde(x)
    x_vals = np.linspace(x.min(), x.max(), 1000)
    density_vals = density(x_vals)
    
    # Add the density curve to the figure
    fig.add_trace(go.Scatter(x=x_vals, y=density_vals * len(x) * 0.12, mode='lines', name='Density', line=dict(color='darkolivegreen')))
    
    fig.update_layout(
       title={
            'text': 'Gender Ratio Difference Distribution between Google Scholar and LLM Co-Authors',
            'x': 0.5,  # Center the title
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16}  # Adjust the font size as needed
        },
        xaxis_title='Gender Ratio Difference',
        yaxis_title='Number of Authors',
        bargap=0.2,
        template='simple_white'
    )

    st.plotly_chart(fig)

def drawEthnicityDiffRatio(df):
    for index, row in df.iterrows():
        scholarEthnicity = row["Co-authors’ ethnicity (Google Scholar)"].split(", ")
        scholarRatio = 1 - scholarEthnicity.count("White") / len(scholarEthnicity)

        gptEthnicity = row["Co-authors’ ethnicity (OpenAI)"].split(", ")
        gptRatio = 1 - gptEthnicity.count("White") / len(gptEthnicity)

        df.at[index, "Ethnicity Diff Ratio"] = gptRatio - scholarRatio

    fig = px.histogram(df, x="Ethnicity Diff Ratio", nbins=17, color_discrete_sequence=['lightpink'])
    
    # Calculate the density curve
    x = df["Ethnicity Diff Ratio"]
    density = gaussian_kde(x)
    x_vals = np.linspace(x.min(), x.max(), 1000)
    density_vals = density(x_vals)
    
    # Add the density curve to the figure
    fig.add_trace(go.Scatter(x=x_vals, y=density_vals * len(x) * 0.12, mode='lines', name='Density', line=dict(color='darkmagenta')))
    
    fig.update_layout(
       title={
            'text': 'Ethnicity Ratio Difference Distribution between Google Scholar and LLM Co-Authors',
            'x': 0.5,  # Center the title
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16}  # Adjust the font size as needed
        },
        xaxis_title='Ethnicity Ratio Difference',
        yaxis_title='Number of Authors',
        bargap=0.2,
        template='simple_white'
    )

    st.plotly_chart(fig)

def saveCoAuthorshipNets():
    # Data for co-authorship networks
    src = "Geoffrey Hinton"
    scholarTargets = ["Terrence Sejnowski", "Vinod Nair", "George E. Dahl", "Abdelrahman Mohamed", "Radford Neal", 
                      "Sidney Fels", "David C. Plaut", "Chris Williams", "Robert Tibshirani", "Demetri Terzopoulos", 
                      "Steven L. Small"]
    aiTargets = ["Yoshua Bengio", "Yann LeCun", "Ruslan Salakhutdinov", "Ilya Sutskever", "Simon Osindero", 
                 "Alex Krizhevsky", "David Warde-Farley", "Tijmen Tieleman", "Volodymyr Mnih", "Richard Zemel", 
                 "Raia Hadsell"]

    # Create NetworkX graphs
    scholarG = nx.DiGraph()  # Directed graph for scholar network
    aiG = nx.DiGraph()       # Directed graph for AI network

    # Add nodes and edges for scholar network
    scholarG.add_node(src)
    for target in scholarTargets:
        scholarG.add_node(target)
        scholarG.add_edge(src, target)

    # Add nodes and edges for AI network
    aiG.add_node(src)
    for target in aiTargets:
        aiG.add_node(target)
        aiG.add_edge(src, target)

    return scholarG, aiG

def draw_network(graph, title, node_color='blue', label_color='black'):
    pos = nx.spring_layout(graph)  # Positioning for nodes
    edge_x = []
    edge_y = []

    # Drawing edges
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',  # Disable hover info for edges
        mode='lines')

    # Drawing nodes
    node_x = []
    node_y = []
    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',  # Show both markers and text
        hoverinfo='none',  # Disable hover info for nodes
        marker=dict(
            showscale=False,  # Disable color scale (removes color bar)
            color=node_color,  # Set custom node color
            size=35,  # Increase size of nodes
        ),
        text=[f'{node}' for node in graph.nodes()],  # Add labels
        textposition='middle center',  # Position labels in the center of nodes
        textfont=dict(color=label_color)  # Change the color of labels
    )

    # Create the plotly figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=title,
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),  # Hide x-axis ticks and labels
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),  # Hide y-axis ticks and labels
                   ))
    return fig

def drawCoAuthorshipNets():
    scholarG, aiG = saveCoAuthorshipNets()  # Get the two co-authorship networks

    with st.container():
        fig_scholar = draw_network(scholarG, "Geoffrey Hinton's Google Scholar Network", "aquamarine")
        st.plotly_chart(fig_scholar)

        fig_ai = draw_network(aiG, "Geoffrey Hinton's LLM-Constructed Network", "plum")
        st.plotly_chart(fig_ai)

df = pd.read_csv("data/anonymizedLLM.csv")

def main():
    st.title('Fairness Visualizer App')
    calculateRecallPrecision(df)
    
    with st.sidebar:
        if st.button("📊 Data Distributions"):
            st.session_state.page = "Data Distributions"

        if st.button("🎓 Sample Networks"):
            st.session_state.page = "Sample Networks"
        
        if st.button("📈 Fairness Metrics"):
            st.session_state.page = "Fairness Metrics"
        
        if st.button("⚖️ Gender/Ethnicity Biases"):
            st.session_state.page = "Gender/Ethnicity Biases"
    
    # Display the selected page's content
    if st.session_state.page == "Data Distributions":
        drawCountryMap(df)
    if st.session_state.page == "Sample Networks":
        saveCoAuthorshipNets()
        drawCoAuthorshipNets()
    elif st.session_state.page == "Fairness Metrics":
        drawEthnicityDP(df)
        drawEthnicityPE(df)
    elif st.session_state.page == "Gender/Ethnicity Biases":
        drawGenderDiffRatio(df)
        drawEthnicityDiffRatio(df)

if __name__ == "__main__":
    if "page" not in st.session_state:
        st.session_state.page = "Data Distributions"
    main()
