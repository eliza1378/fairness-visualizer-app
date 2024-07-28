import streamlit as st
from scholarly import scholarly
import pandas as pd
import gender_guesser.detector as gender
from ethnicolr import pred_fl_reg_name
import seaborn as sns
import matplotlib.pyplot as plt
import mpld3
import streamlit.components.v1 as components
from email2country import email2institution_country
import geopandas as gpd
import geopy
from geopy.geocoders import Nominatim

st.markdown("""
<link rel="stylesheet" href="assets/css/button_style.css" type="text/css">
""", unsafe_allow_html=True)

locator = Nominatim(user_agent="bias-visualizer", timeout=20)

ethnicityMap = {
    "asian": "Asian",
    "hispanic": "Hispanic",
    "nh_black": "Black",
    "nh_white": "White"
}

def predictEthnicity(fullName):
    nameParts = fullName.split()
    firstName = nameParts[0]
    lastName = nameParts[-1]
    
    df = pd.DataFrame({'first': [firstName], 'last': [lastName]}) 
    df_pred = pred_fl_reg_name(df, 'last', 'first')       
    ethnicity = ethnicityMap[df_pred['race'][0]]
    
    return ethnicity

def affiliation2country(affiliation):
  institution = affiliation.split(',')[-1].strip()
  address = locator.geocode(institution, language="en")
  if address:
    splitted = address[0].split(',')
    country = splitted[-1].strip()
    return country
  return None

def drawGenderDiffRatio(df, bin_width):
    df["Gender Diff Ratio"] = 0
    
    for index, row in df.iterrows():
        scholarGenders = row["Co-authors’ genders (Google Scholar)"]
        scholarRatio = scholarGenders.count("female") / len(scholarGenders) if scholarGenders else 0

        aiGenders = row["Co-authors’ genders (OpenAI)"]
        aiRatio = aiGenders.count("female") / len(aiGenders) if aiGenders else 0

        df.at[index, "Gender Diff Ratio"] = aiRatio - scholarRatio

    data_range = df["Gender Diff Ratio"].max() - df["Gender Diff Ratio"].min()
    num_bins = int(data_range / bin_width)
    num_bins = max(1, num_bins)

    fig, ax = plt.subplots()
    sns.histplot(data=df, x="Gender Diff Ratio", kde=True, color="palevioletred", bins=num_bins, ax=ax)
    ax.set(xlabel='Gender Ratio Difference', ylabel='Number of Authors')
    ax.set_title('Gender Ratio Difference Between Google Scholar and LLM Co-Authors')

    fig_html = mpld3.fig_to_html(fig)
    st.components.v1.html(fig_html, height=600)

def drawEthnicityDiffRatio(df, bin_width):
    df["Ethnicity Diff Ratio"] = 0
    
    for index, row in df.iterrows():
        scholarEthnicities = row["Co-authors’ ethnicity (Google Scholar)"]
        scholarRatio = scholarEthnicities.count("white") / len(scholarEthnicities) if scholarEthnicities else 0

        aiEthnicities = row["Co-authors’ ethnicity (OpenAI)"]
        aiRatio = aiEthnicities.count("white") / len(aiEthnicities) if aiEthnicities else 0

        df.at[index, "Ethnicity Diff Ratio"] = aiRatio - scholarRatio

    data_range = df["Ethnicity Diff Ratio"].max() - df["Ethnicity Diff Ratio"].min()
    num_bins = int(data_range / bin_width)
    num_bins = max(1, num_bins)

    fig, ax = plt.subplots()
    sns.histplot(data=df, x="Ethnicity Diff Ratio", kde=True, color="mediumseagreen", bins=num_bins, ax=ax)
    ax.set(xlabel='Ethnicity Ratio Difference', ylabel='Number of Authors')
    ax.set_title('Ethnicity Ratio Difference Between Google Scholar and LLM Co-Authors')

    fig_html = mpld3.fig_to_html(fig)
    st.components.v1.html(fig_html, height=600)

# Main App
st.write('# LLM Co-Authorship Fairness Visualizer')

# Initialize session state for storing author names, DataFrame, and slider value
if 'author_names' not in st.session_state:
    st.session_state.author_names = []

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['Author', 'Gender', 'Ethnicity', 'Co-authors’ names (Google Scholar)', 'Co-authors’ genders (Google Scholar)', 'Co-authors’ ethnicity (Google Scholar)', 'Co-authors’ countries (Google Scholar)', 'Co-authors’ names (OpenAI)', 'Co-authors’ genders (OpenAI)', 'Co-authors’ ethnicity (OpenAI)'])

if 'bin_width' not in st.session_state:
    st.session_state.bin_width = 0.12  # Default bin width

if 'visualize' not in st.session_state:
    st.session_state.visualize = False

# Text input for author name
authorName = st.text_input('Author Name')

# Button to add the entered author name to the list
if st.button('Add Author', type="primary"):
    if authorName:
        st.session_state.author_names.append(authorName)
    else:
        st.write('Please enter an author name before adding.')

# Display the list of added authors
if st.session_state.author_names:
    st.write('Added Authors:')
    for name in st.session_state.author_names:
        st.write(name)

# Button to visualize biases
if st.button('Visualize Biases', type="primary"):
    df = st.session_state.df
    genderDetector = gender.Detector()

    for authorName in st.session_state.author_names:
        try:
            gender = genderDetector.get_gender(authorName.split()[0])
            ethnicity = predictEthnicity(authorName)

            searchQuery = next(scholarly.search_author(authorName))
            author = scholarly.fill(searchQuery)
            
            coauthorIDs = [i["scholar_id"] for i in author["coauthors"]]
            scholarCoauthors = []
            scholarGenders = []
            scholarEthnicities = []
            scholarCountries = []

            if coauthorIDs:
                for coauthorID in coauthorIDs:
                    coauthorName = scholarly.search_author_id(coauthorID)["name"]
                    scholarCoauthors.append(coauthorName)
                    scholarGender = genderDetector.get_gender(coauthorName.split()[0])
                    scholarGenders.append(scholarGender)
                    scholarEthnicity = predictEthnicity(coauthorName)
                    scholarEthnicities.append(scholarEthnicity)
                    coauthor = scholarly.search_author_id(coauthorID)
                    email = coauthor["email_domain"]
                    affiliation = coauthor["affiliation"]
                    country = None
                    try:
                      country = email2institution_country(email)
                    except Exception:
                      country = affiliation2country(affiliation)
                    scholarCountries.append(country)

            else:
                st.write(f'No co-authors found for {authorName} in Google Scholar.')
            
            aiCoauthors = ["Zahra Mozaffar", "Reza Alizadeh", "Sarah Williams"]
            aiGenders = []
            aiEthnicities = []

            for coauthor in aiCoauthors:
                aiGender = genderDetector.get_gender(coauthor.split()[0])
                aiGenders.append(aiGender)
                aiEthnicity = predictEthnicity(coauthor)
                aiEthnicities.append(aiEthnicity)

            df.loc[len(df)] = [authorName, gender, ethnicity, scholarCoauthors, scholarGenders, scholarEthnicities, scholarCountries, aiCoauthors, aiGenders, aiEthnicities]
                
        except StopIteration:
            st.write(f'No authors found for the name "{authorName}".')
        except Exception as e:
            st.write(f'An error occurred for {authorName}: {e}')

    st.session_state.df = df
    st.session_state.visualize = True

# Sidebar settings for bin width
st.sidebar.header('Settings')
st.session_state.bin_width = st.sidebar.slider('Bin Width', min_value=0.01, max_value=0.5, value=st.session_state.bin_width)

# Draw the plot if visualization button was pressed and DataFrame is not empty
if 'visualize' in st.session_state and st.session_state.visualize and not st.session_state.df.empty:
    st.dataframe(st.session_state.df)
    drawGenderDiffRatio(st.session_state.df, st.session_state.bin_width)
    drawEthnicityDiffRatio(st.session_state.df, st.session_state.bin_width)
