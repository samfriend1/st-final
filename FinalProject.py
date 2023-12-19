"""
Class: CS230 Section 1
Sam Friend
Description: Final Project
I pledge that I have completed the programming assignment
independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import plotly.express as px

st.set_page_config(page_title="Boston Blue Bikes Data Exploration", layout="wide")

bike_data = pd.read_excel('tripdata.xlsx')
station_data = pd.read_excel('current_bluebikes_stations.xlsx', header=1)
bike_data['starttime'] = pd.to_datetime(bike_data['starttime'])

if 'start_date' not in st.session_state:
    st.session_state['start_date'] = bike_data['starttime'].dt.date.min()
if 'end_date' not in st.session_state:
    st.session_state['end_date'] = bike_data['starttime'].dt.date.max()


def main():
    # Set up page configuration

    # Styling
    st.markdown("""
        <style>
        .main {
            background-color: #E8F5E9;
        }
        .big-font {
            font-size:35px !important;
            color: #1A535C;
            font-weight: bold;
        }
        .medium-font {
            font-size:25px !important;
            color: #4ECDC4;
        }
        .sidebar .sidebar-content {
            background-color: #F7FFF7;
        }
        </style>
        """, unsafe_allow_html=True)

    # Enhanced Sidebar for navigation
    st.sidebar.title("Explore")
    page = st.sidebar.radio("Navigate to", ["Home", "Line Chart", "Heat Map", "Histogram", "Dock Distribution",
                                            "Popular Times", "Additional Analysis"])

    # Display content based on navigation
    if page == 'Home':
        st.markdown("""
            <div style="text-align: center;">
                <h1 style="color: #1A535C; font-size: 40px;">Boston Blue Bikes Data Explorer</h1>
                <p style="font-size: 20px; color: #4ECDC4;">
                    Welcome to the interactive exploration of Boston's bike-sharing ecosystem. Dive into the vibrant 
                    world of urban mobility and discover how Bostonians navigate their city.
                </p>
            </div>
            <div style="font-size: 18px; color: #333;">
                <ul>
                    <li><b>Usage Patterns:</b> Uncover trends in bike usage over time, on different days of the week, 
                    and across various user types.</li>
                    <li><b>Popular Routes:</b> Explore the most frequented paths and understand the flow of bike 
                    traffic in the city.</li>
                    <li><b>Station Activity:</b> Analyze station-specific data to see where bikes are most in demand 
                    and how dock capacity meets the need.</li>
                    <li><b>Interactive Visualizations:</b> Engage with dynamic charts and maps that bring the data to 
                    life, allowing for a hands-on exploration of Boston's biking landscape.</li>
                </ul>
            </div>
            <p style="text-align: center; font-size: 16px; color: #555;">
                Whether you're a city planner, a daily commuter, or just a data enthusiast, this platform offers 
                valuable insights into the heartbeat of urban mobility in Boston.
            </p>
            """, unsafe_allow_html=True)
    elif page == 'Line Chart':
        show_popular_days_chart()
    elif page == 'Heat Map':
        show_heatmap(station_data)
    elif page == 'Histogram':
        show_histogram()
    elif page == 'Dock Distribution':
        show_dock_distribution()
    elif page == 'Popular Times':
        fig, ax = plot_duration_vs_time_of_day(bike_data, 'hour')
        st.pyplot(fig)
    elif page == 'Additional Analysis':
        # Second call to show_heatmap
        additional_analysis(station_data)


def show_popular_days_chart():
    st.markdown('<p class="big-font">Most Popular Days by User Type Comparison</p>', unsafe_allow_html=True)
    st.markdown('<p class="small-font">This line chart compares the average number of rides across different '
                'days of the week for selected user types. It helps identify patterns in bike usage, such as '
                'peak days for riders, and can be used to infer the impact of weekdays and weekends on '
                'bike-sharing habits. Select different user types to see how usage patterns vary among '
                'them</p>', unsafe_allow_html=True)

    # Select user types for comparison
    user_type_options = bike_data['usertype'].unique()
    selected_user_types = st.multiselect('Select User Types for Comparison', user_type_options,
                                         default=user_type_options)

    # Create a figure for the plot
    plt.figure(figsize=(10, 6))

    # Sort days of the week
    ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for user_type in selected_user_types:
        # Filter data based on selected user type
        filtered_data = bike_data[bike_data['usertype'] == user_type]

        # Adding a column for the day of the week
        filtered_data['day_of_week'] = filtered_data['starttime'].dt.day_name()

        # Group by day of the week and count the number of rides
        day_counts = filtered_data.groupby('day_of_week').size().reindex(ordered_days)

        # Plotting
        plt.plot(day_counts.index, day_counts.values, label=f'Average Rides for {user_type}', marker='o')

    plt.xlabel('Day of the Week')
    plt.ylabel('Average Number of Rides')
    plt.title('Comparison of Average Number of Rides by Day of the Week Across User Types')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)


def show_heatmap(data):
    st.markdown('<p class="big-font">Heatmap of Stations</p>', unsafe_allow_html=True)
    st.markdown('<p class="small-font">The heat map visualizes the concentration of bike stations '
                'and their activity levels throughout the city. Brighter areas indicate higher activity, '
                'allowing you to quickly identify hotspots of bike usage. Hover over any point to '
                'see more details about each station</p>', unsafe_allow_html=True)
    # Creating a dictionary mapping station names to additional information
    station_info_dict = {row['Name']: f"ID: {row['Number']}, Lat: {row['Latitude']}, Lon: {row['Longitude']}"
                         for _, row in data.iterrows()}

    # Setting up the tooltip to include information from the dictionary
    tooltip = {
        "html": "<b>Station Name:</b> {Name}<br><b>District:</b> " + station_info_dict.get("{District}", "{District}"),
        "style": {
            "backgroundColor": "orange",
            "color": "black"
        }
    }

    # Heatmap Layer
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data,
        get_position=["Longitude", "Latitude"],
        opacity=0.4,
        radius=50
    )

    # Scatterplot Layer for tooltips
    scatterplot_layer = pdk.Layer(
        "ScatterplotLayer",
        data,
        get_position=["Longitude", "Latitude"],
        get_color="[200, 30, 0, 160]",
        get_radius=35,
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=data["Latitude"].mean(),
        longitude=data["Longitude"].mean(),
        zoom=11,
        pitch=0
    )

    st.pydeck_chart(pdk.Deck(layers=[heatmap_layer, scatterplot_layer], initial_view_state=view_state, tooltip=tooltip))


def show_histogram():
    st.markdown('<p class="big-font">Histogram of Bike Trip Durations</p>', unsafe_allow_html=True)
    st.markdown('<p class="small-font">This histogram shows the distribution of bike trip durations. '
                'It gives an insight into how long users typically rent the bikes, highlighting the '
                'most common trip durations. Use the sliders to filter the results by user type and adjust '
                'the maximum trip duration and bin size for a more detailed analysis</p>', unsafe_allow_html=True)
    # Interactive Elements on the main page
    user_type_options = ['All'] + list(bike_data['usertype'].unique())
    selected_user_type = st.selectbox('Filter by User Type', user_type_options)

    max_duration_limit = st.slider('Maximum Trip Duration (minutes)', 5, 120, 60)
    bin_size = st.slider('Bin Size (minutes)', 1, 10, 5)

    # Ensure the 'trip_duration_min' column exists
    if 'trip_duration_min' not in bike_data.columns:
        bike_data['trip_duration_min'] = bike_data['tripduration'] / 60

    # Data Filtering
    if selected_user_type != 'All':
        filtered_data = bike_data[(bike_data['usertype'] == selected_user_type) & (bike_data['trip_duration_min']
                                                                                   <= max_duration_limit)]
    else:
        filtered_data = bike_data[bike_data['trip_duration_min'] <= max_duration_limit]

    # Create a histogram using Plotly
    fig = px.histogram(filtered_data, x='trip_duration_min', nbins=int(max_duration_limit/bin_size))
    fig.update_layout(
        title=f'Distribution of Bike Trip Durations for {selected_user_type}',
        xaxis_title='Trip Duration (minutes)',
        yaxis_title='Number of Trips',
        bargap=0.1,
    )
    fig.update_traces(hoverinfo='y', hovertemplate='%{y} rides')
    st.plotly_chart(fig)


def show_dock_distribution():
    st.markdown('<p class="big-font">Dock Capacity Distribution by Selected District</p>', unsafe_allow_html=True)
    st.markdown('<p class="small-font">The pie chart shows the proportion of bike stations within each dock capacity '
                'category for a selected district. It provides a visual breakdown of station capacities, helping to '
                'understand how well the infrastructure serves the area. Choose a district to see its dock capacity '
                'distribution.</p>', unsafe_allow_html=True)

    # Interactive Element: Dropdown for choosing a district
    # Filter out NaN values from the 'District' column
    district_options = station_data['District'].dropna().unique()
    selected_district = st.selectbox('Select a District', district_options)

    # Filter data based on the selected district
    filtered_data = station_data[station_data['District'] == selected_district]

    # Define dock capacity categories
    dock_bins = [0, 5, 10, 15, 20, 25, 30]  # Adjust these bins as per your data
    labels = ['0-5', '6-10', '11-15', '16-20', '21-25', '26+']
    filtered_data['Dock Capacity Category'] = pd.cut(filtered_data['Total docks'], bins=dock_bins,
                                                     labels=labels, right=False)

    # Data aggregation based on dock capacity category
    dock_category_counts = filtered_data['Dock Capacity Category'].value_counts()

    # Creating Pie Chart
    fig = px.pie(dock_category_counts, values=dock_category_counts.values, names=dock_category_counts.index,
                 title=f'Dock Capacity Distribution in {selected_district}')
    fig.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')

    st.plotly_chart(fig)


def plot_duration_vs_time_of_day(data, time_bin='hour'):
    st.markdown('<p class="big-font">Popular Times</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="small-font">This scatter plot illustrates the relationship between the time of day and '
        'the average trip duration. It can reveal trends such as peak times for longer or shorter trips. '
        'Each dot represents the average duration of trips that started at a particular hour of '
        'the day</p>', unsafe_allow_html=True)
    # Ensure 'trip_duration_min' exists
    if 'trip_duration_min' not in data.columns:
        data['trip_duration_min'] = data['tripduration'] / 60

    # Extract hour or minute from 'starttime'
    if time_bin == 'hour':
        data['time_of_day'] = data['starttime'].dt.hour
    elif time_bin == 'minute':
        data['time_of_day'] = data['starttime'].dt.hour * 60 + data['starttime'].dt.minute

    # Prepare data for plotting (using list comprehension)
    grouped_data = [(time, df['trip_duration_min'].mean()) for time, df in data.groupby('time_of_day')]

    # Unpack grouped data
    times, avg_durations = zip(*grouped_data)

    # Plotting
    fig, ax = plt.subplots()
    ax.scatter(times, avg_durations, color='purple')
    ax.set_xlabel(f'Time of Day ({time_bin})')
    ax.set_ylabel('Average Trip Duration (minutes)')
    ax.set_title('Average Trip Duration vs. Time of Day')

    return fig, ax


def additional_analysis(station_data):
    st.title("Additional Station Data Analysis")

    # Filter out the unnamed columns from the dataframe
    relevant_columns = station_data.columns[:8].tolist()
    station_data = station_data[relevant_columns]

    # Viewing Columns by Ascending or Descending Order
    st.subheader("Viewing Columns by Ascending or Descending Order")
    sort_column = st.selectbox("Select column to sort by", relevant_columns)
    sort_order = st.radio("Sort order", ("Ascending", "Descending"))
    sorted_data = station_data.sort_values(by=sort_column, ascending=(sort_order == "Ascending"))
    st.dataframe(sorted_data.head(10))

    # Sorting
    st.subheader("Sorting")
    top_n = st.slider("Select top N stations by total docks", 1, 20, 5)
    top_column = st.selectbox("Select column for top N values", ['Total docks', 'Deployment Year'])
    if top_column in relevant_columns:
        top_data = station_data.nlargest(top_n, top_column) if top_column == 'Total docks' \
            else station_data.nsmallest(top_n, top_column)
        st.dataframe(top_data)

    # Filtering by Column
    st.subheader("Filtering by Column")
    filter_column = st.selectbox("Filter by column", ['District', 'Public'])
    if filter_column in relevant_columns:
        if filter_column == 'District':
            district_to_filter = st.selectbox("Choose the district", station_data['District'].unique())
            filtered_data = station_data[station_data['District'] == district_to_filter]
        elif filter_column == 'Public':
            public_status = st.radio("Public status", ('Yes', 'No'))
            filtered_data = station_data[station_data['Public'] == (public_status == 'Yes')]
        st.dataframe(filtered_data)

    # Show Heatmap with Filtered Data
    if st.button("Show Heatmap with Filtered Data"):
        show_heatmap(filtered_data)

    # Pivot Table Analysis - Average Trip Duration by Station Pair
    st.subheader("Pivot Table Analysis - Average Trip Duration by Station Pair")
    sort_order = st.selectbox("Select sort order for pivot table", ['Descending', 'Ascending'], key="pivot_sort_order")

    # Add a button to generate the pivot table
    if st.button("Generate Pivot Table for Station Pairs"):
        # Create a pivot table with the average trip duration for each start-end station pair
        pivot_table = bike_data.pivot_table(
            index=['start station name', 'end station name'],
            values='tripduration',
            aggfunc='mean'
        ).reset_index()

        # Sort the pivot table
        pivot_table = pivot_table.sort_values('tripduration', ascending=(sort_order == 'Ascending'))

        # Display the pivot table with labels
        st.write("Average Trip Duration (in seconds) from Start to End Station:")
        st.dataframe(pivot_table.assign(**{'Average Duration (sec)':
                                        pivot_table['tripduration']}).drop('tripduration', axis=1))


if __name__ == '__main__':
    main()
