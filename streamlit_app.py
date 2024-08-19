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
from pyvis.network import Network


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

def getEnglishNonEnglishList(countries):
    englishCountries = ["United States", "United Kingdom", "Ireland", "Canada", "Australia"]
    englishNonEnglishList = []
    for country in countries:
        if country in englishCountries:
            englishNonEnglishList.append("English")
        else:
            englishNonEnglishList.append("Non-English")
    return englishNonEnglishList

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
    sf = df.copy(deep=False)
    sf["Gender Diff Ratio"] = 0
    
    for index, row in sf.iterrows():
        scholarGenders = row["Co-authors’ genders (Google Scholar)"]
        scholarRatio = scholarGenders.count("female") / len(scholarGenders) if scholarGenders else 0

        aiGenders = row["Co-authors’ genders (OpenAI)"]
        aiRatio = aiGenders.count("female") / len(aiGenders) if aiGenders else 0

        sf.at[index, "Gender Diff Ratio"] = aiRatio - scholarRatio

    data_range = sf["Gender Diff Ratio"].max() - sf["Gender Diff Ratio"].min()
    num_bins = int(data_range / bin_width)
    num_bins = max(1, num_bins)

    fig, ax = plt.subplots()
    sns.histplot(data=sf, x="Gender Diff Ratio", kde=True, color="palevioletred", bins=num_bins, ax=ax)
    ax.set(xlabel='Gender Ratio Difference', ylabel='Number of Authors')
    ax.set_title('Gender Ratio Difference Between Google Scholar and LLM Co-Authors')

    fig_html = mpld3.fig_to_html(fig)
    st.components.v1.html(fig_html, height=500)

def drawEthnicityDiffRatio(df, bin_width):
    sf = df.copy(deep=False)
    sf["Ethnicity Diff Ratio"] = 0
    
    for index, row in sf.iterrows():
        scholarEthnicities = row["Co-authors’ ethnicity (Google Scholar)"]
        scholarRatio = 1 - (scholarEthnicities.count("White") / len(scholarEthnicities) if scholarEthnicities else 0)

        aiEthnicities = row["Co-authors’ ethnicity (OpenAI)"]
        aiRatio = 1 - (aiEthnicities.count("White") / len(aiEthnicities) if aiEthnicities else 0)

        sf.at[index, "Ethnicity Diff Ratio"] = aiRatio - scholarRatio

    data_range = sf["Ethnicity Diff Ratio"].max() - sf["Ethnicity Diff Ratio"].min()
    num_bins = int(data_range / bin_width)
    num_bins = max(1, num_bins)
    
    fig, ax = plt.subplots()
    sns.histplot(data=sf, x="Ethnicity Diff Ratio", kde=True, color="mediumseagreen", bins=num_bins, ax=ax)
    ax.set(xlabel='Ethnicity Ratio Difference', ylabel='Number of Authors')
    ax.set_title('Ethnicity Ratio Difference Between Google Scholar and LLM Co-Authors')

    fig_html = mpld3.fig_to_html(fig)
    st.components.v1.html(fig_html, height=500)

def drawLanguageDiffRatio(df, bin_width):
    sf = df.copy(deep=False)
    sf["Language Diff Ratio"] = 0
    
    for index, row in sf.iterrows():
        scholarCountries = row["Co-authors’ countries (Google Scholar)"]
        scholarCountries = [x for x in scholarCountries if x is not None]
        scholarCountries = getEnglishNonEnglishList(scholarCountries)
        scholarRatio = 1 - (scholarCountries.count("English") / len(scholarCountries) if scholarCountries else 0)

        aiCountries = row["Co-authors’ countries (OpenAI)"]
        aiCountries = getEnglishNonEnglishList(aiCountries)
        aiRatio = 1 - (aiCountries.count("English") / len(aiCountries) if aiCountries else 0)

        sf.at[index, "Language Diff Ratio"] = aiRatio - scholarRatio

    data_range = sf["Language Diff Ratio"].max() - sf["Language Diff Ratio"].min()
    num_bins = int(data_range / bin_width)
    num_bins = max(1, num_bins)

    fig, ax = plt.subplots()
    sns.histplot(data=sf, x="Language Diff Ratio", kde=True, color="gold", bins=num_bins, ax=ax)
    ax.set(xlabel='Language Ratio Difference', ylabel='Number of Authors')
    ax.set_title('Language Ratio Difference Between Google Scholar and LLM Co-Authors')

    fig_html = mpld3.fig_to_html(fig)
    st.components.v1.html(fig_html, height=500)

def drawCoAuthorshipNet(src, targets, index, mode):
    net = Network(notebook=True, directed=True, height='200px')
    net.add_node(src)
    for target in targets:
        net.add_node(target)
        net.add_edge(src, target)
    
    fileName = mode + "Network" + str(index) + ".html"
    net.show(fileName)
    #HtmlFile = open(fileName, "r", encoding="utf-8")
    #st.components.v1.html(HtmlFile.read(), height=400)

def drawCoAuthorshipNetByIndex(authorName, index):
    scholarFileName = "scholar" + "Network" + str(index) + ".html"
    aiFileName = "ai" + "Network" + str(index) + ".html"
    scholarFile = open(scholarFileName, "r", encoding="utf-8")
    aiFile = open(aiFileName, "r", encoding="utf-8")
    col1, col2 = st.columns(2)
    with col1:
        st.write(authorName + "'s Google Scholar Network")
        st.components.v1.html(scholarFile.read(), height=240)
    with col2:
        st.write(authorName + "'s LLM-Constructed Network")
        st.components.v1.html(aiFile.read(), height=240)

# Main App
st.write('# LLM Co-Authorship Fairness Visualizer')

# Initialize session state for storing author names, DataFrame, and slider value
if 'author_names' not in st.session_state:
    st.session_state.author_names = []

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['Author', 'Gender', 'Ethnicity', 'Co-authors’ names (Google Scholar)', 'Co-authors’ genders (Google Scholar)', 'Co-authors’ ethnicity (Google Scholar)', 'Co-authors’ countries (Google Scholar)', 'Co-authors’ names (OpenAI)', 'Co-authors’ genders (OpenAI)', 'Co-authors’ ethnicity (OpenAI)', 'Co-authors’ countries (OpenAI)'])

if 'bin_width' not in st.session_state:
    st.session_state.bin_width = 0.12  # Default bin width

if 'visualize' not in st.session_state:
    st.session_state.visualize = False

# Text input for author name
authorName = st.text_input('Author Name', key="user_input")

def clearInput():
    st.session_state.authorName = authorName
    st.session_state.user_input = ""

# Button to add the entered author name to the list
if st.button('Add Author', type="primary", on_click=clearInput):
    if st.session_state.authorName:
        st.session_state.author_names.append(st.session_state.authorName)
    else:
        st.write('Please enter an author name before adding.')


# Display the list of added authors
if st.session_state.author_names:
    st.write('Added Authors:')
    for name in st.session_state.author_names:
        st.write(name)

def clearOutput():
    st.session_state.author_names = []
    st.session_state.df = pd.DataFrame(columns=['Author', 'Gender', 'Ethnicity', 'Co-authors’ names (Google Scholar)', 'Co-authors’ genders (Google Scholar)', 'Co-authors’ ethnicity (Google Scholar)', 'Co-authors’ countries (Google Scholar)', 'Co-authors’ names (OpenAI)', 'Co-authors’ genders (OpenAI)', 'Co-authors’ ethnicity (OpenAI)', 'Co-authors’ countries (OpenAI)'])
    st.empty()

if st.button('Reset', type="primary", on_click=clearOutput):
    pass

# Button to visualize biases
if st.button('Visualize Biases', type="primary"):
    df = st.session_state.df
    genderDetector = gender.Detector()

    for authorName in st.session_state.author_names:
        index = 0
        if authorName in df["Author"].to_list():
            #index = df["Author"].to_list().index(authorName)
            #drawCoAuthorshipNetByIndex(index)
            continue
        else:
            index = len(df)
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

                drawCoAuthorshipNet(authorName, scholarCoauthors, index, "scholar")

            else:
                st.write(f'No co-authors found for {authorName} in Google Scholar.')
            
            aiCoauthors = ["Zahra Mozaffar", "Reza Alizadeh", "Sarah Williams"]
            aiGenders = []
            aiEthnicities = []
            aiCountries = ["Iran", "Germany", "United States"]

            for coauthor in aiCoauthors:
                aiGender = genderDetector.get_gender(coauthor.split()[0])
                aiGenders.append(aiGender)
                aiEthnicity = predictEthnicity(coauthor)
                aiEthnicities.append(aiEthnicity)

            drawCoAuthorshipNet(authorName, aiCoauthors, index, "ai")

            df.loc[len(df)] = [authorName, gender, ethnicity, scholarCoauthors, scholarGenders, scholarEthnicities, scholarCountries, aiCoauthors, aiGenders, aiEthnicities, aiCountries]
                
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
    for index in range(len(st.session_state.df)):
        authorName = st.session_state.df["Author"][index]
        drawCoAuthorshipNetByIndex(authorName, index)
    drawGenderDiffRatio(st.session_state.df, st.session_state.bin_width)
    drawEthnicityDiffRatio(st.session_state.df, st.session_state.bin_width)
    drawLanguageDiffRatio(st.session_state.df, st.session_state.bin_width)
