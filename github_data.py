import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load CSV Files
github_dataset = pd.read_csv('github_dataset.csv')
repo_data = pd.read_csv('repository_data.csv')

# Filter out NaN values
github_dataset = github_dataset.dropna()
repo_data = repo_data.dropna()

# Convert created_at in repo_data to datetime
repo_data['created_at'] = pd.to_datetime(repo_data['created_at'])

# Step 2: Define Function to Create Groups
def create_groups(dataset, column):
    min_value = dataset[column].min()
    max_value = dataset[column].max()
    bin_edges = pd.cut([min_value, max_value], bins=4, retbins=True)[1]
    bin_edges = [int(round(edge)) for edge in bin_edges]
    group_labels = [
        f'Group 1: {bin_edges[0]} - {bin_edges[1]}',
        f'Group 2: {bin_edges[1]} - {bin_edges[2]}',
        f'Group 3: {bin_edges[2]} - {bin_edges[3]}',
        f'Group 4: {bin_edges[3]} - {bin_edges[4]}'
    ]

    dataset['group'] = pd.cut(dataset[column], bins=bin_edges, labels=group_labels)
    return dataset

# Step 4: Group by Category and Calculate Percentages
def get_percentage_grouped(dataset, group_column, value_column):
    grouped = dataset.groupby([group_column])[value_column].value_counts(normalize=True).unstack(fill_value=0) * 100
    return grouped

# Step 5: Streamlit User Interface
st.title("Repository Analysis")

# Sidebar for selecting analysis view
file_option = st.sidebar.selectbox("Select Data", ["Github Dataset", "Repository Data"])
if file_option == "Github Dataset":
    analysis_option = st.sidebar.radio("Select Analysis View", ("Stars Count", "Pull Requests", "Forks Count", "Contributors", "Stars vs Forks Correlation", "Top Repositories"))  # Changed watchers to forks
elif file_option == "Repository Data":
    analysis_option = st.sidebar.radio("Select Analysis View", ("Stars Count", "Pull Requests", "Forks Count", "Watchers", "Language Popularity Over Time", "Stars vs Forks Correlation", "Top Repositories"))



if analysis_option in ["Stars Count", "Pull Requests", "Forks Count", "Contributors", "Watchers"]:
    # Column mapping
    column_map = {
        "Stars Count": 'stars_count',
        "Pull Requests": 'pull_requests',
        "Forks Count": 'forks_count',
        "Contributors": 'contributors',
        "Watchers": 'watchers'
    }

    st.subheader(f"Language Distribution by {analysis_option}")

    language_percentages=[]

    if file_option == "Github Dataset":
         # Language selection dropdown
        language_option = st.selectbox("Select Language", github_dataset['language'].unique())

        column = column_map[analysis_option]

        # # Get percentage data and plot
        github_dataset = create_groups(github_dataset, column)
        language_percentages = get_percentage_grouped(github_dataset, 'group', 'language')[language_option]

    if file_option == "Repository Data":
         # Language selection dropdown
        language_option = st.selectbox("Select Language", repo_data['primary_language'].unique())

        column = column_map[analysis_option]

        # Get percentage data and plot
        repo_dataset = create_groups(repo_data, column)
        language_percentages = get_percentage_grouped(repo_data, 'group', 'primary_language')[language_option]
    # Plotting
    fig, ax = plt.subplots()
    language_percentages.plot(kind='bar', ax=ax)
    ax.set_title(f'Percentage of Repositories Using {language_option} by {analysis_option}')
    ax.set_ylabel('Percentage of Repositories')
    ax.set_xlabel(f'{analysis_option} Groups')
    ax.set_xticklabels(language_percentages.index, rotation=45)
    st.pyplot(fig)

# Language Popularity Over Time Analysis
elif analysis_option == "Language Popularity Over Time" and file_option == "Repository Data":
    st.subheader("Language Popularity Over Time")

    # Extract year from created_at in repo_data
    repo_data['year'] = repo_data['created_at'].dt.year

    language_option = st.selectbox("Select Language", repo_data['primary_language'].unique())

    # Group by year and language
    language_trends = repo_data.groupby(['year', 'primary_language']).size().unstack(fill_value=0)[language_option]

    # Plotting the trends
    fig, ax = plt.subplots(figsize=(10, 6))
    language_trends.plot(kind='line', ax=ax)
    ax.set_title('Number of Repositories Created per Year by Language')
    ax.set_ylabel('Number of Repositories')
    ax.set_xlabel('Year')
    st.pyplot(fig)

# Stars vs Forks Correlation Analysis
elif analysis_option == "Stars vs Forks Correlation":
    st.subheader("Stars vs Forks Correlation")

    # Scatter plot of stars vs forks
    fig, ax = plt.subplots(figsize=(8, 6))
    if file_option == "Github Dataset":
        sns.scatterplot(x='stars_count', y='forks_count', data=github_dataset, ax=ax)
    if file_option == "Repository Data":
        sns.scatterplot(x='stars_count', y='forks_count', data=repo_data, ax=ax)
    ax.set_title('Correlation Between Stars and Forks')
    ax.set_xlabel('Stars Count')
    ax.set_ylabel('Forks Count')
    st.pyplot(fig)

# Top Repositories by Stars or Forks
elif analysis_option == "Top Repositories":
    st.subheader("Top Repositories by Stars and Forks")

    # Display top repositories
    top_n = st.slider("Select Number of Top Repositories", min_value=5, max_value=50, value=10)

    if file_option == "Github Dataset":
        st.write("Top Repositories by Stars:")
        top_by_stars = github_dataset.nlargest(top_n, 'stars_count')[['repositories', 'stars_count', 'language']]
        st.write("Top Repositories by Forks:")
        top_by_forks = github_dataset.nlargest(top_n, 'forks_count')[['repositories', 'forks_count', 'language']]
    if file_option == "Repository Data":
        st.write("Top Repositories by Stars:")
        top_by_stars = repo_data.nlargest(top_n, 'stars_count')[['name', 'stars_count', 'primary_language']]
        st.write("Top Repositories by Forks:")
        top_by_forks = repo_data.nlargest(top_n, 'forks_count')[['name', 'forks_count', 'primary_language']]
    st.dataframe(top_by_stars)
    st.dataframe(top_by_forks)


# Display raw data
if st.checkbox("Show Raw Data"):
    st.write("GitHub Dataset:")
    st.dataframe(github_dataset)
    st.write("Repo Data:")
    st.dataframe(repo_data)
