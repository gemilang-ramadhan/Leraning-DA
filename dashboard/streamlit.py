# Import necessary libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style('whitegrid')
sns.set_palette('Set2')

st.set_page_config(
    page_title="Bike Rentals Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar 
st.sidebar.title("Bike dataset analysis for Dicoding Final Project")
st.sidebar.markdown("---") 

st.sidebar.markdown("""
**Created by:**\n  
    Muhammad Gemilang Ramadhan  
    Bangkit ML-63 Cohort  
    
    m004b4ky2856@bangkit.academy
Finished on September 24th 2024
""")

st.sidebar.markdown("---")

# Date input untuk sidebar
st.sidebar.header('Select Date Range')
date_range = st.sidebar.date_input(
    'Select desired date range from 2011-01-01 until 2012-12-31',
    value=(pd.to_datetime('2011-01-01'), pd.to_datetime('2012-12-31')),
    min_value=pd.to_datetime('2011-01-01'), # Sesuai dengan dataset yang dimiliki
    max_value=pd.to_datetime('2012-12-31')
)

# date_range harus bertipe tuple/list agar streamlit bisa membandingkan datetype
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    st.error("## Valid data range should be around 2011-01-01 until 2012-12-31")
    st.stop()

# Title and Introduction
st.title("Bike Rentals Dashboard")
st.markdown("""
The following dashboard provides information of bike rental from the start of 2011 until the end of 2012
""")

@st.cache_data # cache data agar load dataset hanya dilakukan sekali run
def load_data():
    day_df = pd.read_csv('./data/bike/day.csv')
    hour_df = pd.read_csv('./data/bike/hour.csv')
    return day_df, hour_df

day_df, hour_df = load_data()

# Assesing data
weather_labels = {
    1: 'Clear, Few clouds, Partly cloudy',
    2: 'Mist + Cloudy, Mist + Broken clouds',
    3: 'Light Snow, Light Rain + Thunderstorm',
    4: 'Heavy Rain, Snow + Fog'
}

day_df['weather_desc'] = day_df['weathersit'].map(weather_labels)
hour_df['weather_desc'] = hour_df['weathersit'].map(weather_labels)

season_labels = {
    1: 'Spring',
    2: 'Summer',
    3: 'Fall',
    4: 'Winter'
}

day_df['season_desc'] = day_df['season'].map(season_labels)

# Convert 'dteday' ke datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Grouping data
grouped_day_df = day_df[(day_df['dteday'] >= start_date) & (day_df['dteday'] <= end_date)]
grouped_hour_df = hour_df[(hour_df['dteday'] >= start_date) & (hour_df['dteday'] <= end_date)]

grouped_data = grouped_day_df.groupby(['season_desc', 'weather_desc'])['cnt'].mean().reset_index()
grouped_hour_df['holiday_desc'] = grouped_hour_df['holiday'].map({0: 'No', 1: 'Yes'})
grouped_hour_data = grouped_hour_df.groupby(['holiday_desc', 'weather_desc'])['cnt'].mean().reset_index()
hourly_peak_data = grouped_hour_df.groupby('hr')['cnt'].mean().reset_index()

# Create Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Season and Weather", "Holiday and Weather", "Hourly Rentals", "Registered and Casual User"])

# Plot: Average Rentals by Season and Weather
with tab1:
    st.header('Average Bike Rentals by Season and Weather Situation')

    if grouped_data.empty:
        st.warning("No data available for the selected date range.")
    else:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=grouped_data, x='season_desc', y='cnt', hue='weather_desc')

        plt.title('Average Bike Rentals by Season and Weather', fontsize=16)
        plt.xlabel('Season', fontsize=14)
        plt.ylabel('Average Bike Rentals', fontsize=14)
        plt.legend(title='Weather Situation', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        st.pyplot(plt.gcf())
        plt.close()

        st.markdown("""
        **Observation:**  
        Diagram batang di atas menunjukkan bahwa penyewaan sepeda paling banyak terjadi pada musim gugur dan musim panas, terutama ketika cuaca cerah. 
        Kondisi cuaca buruk seperti hujan lebat atau salju secara signifikan mengurangi jumlah penyewaan di semua musim.
        """)

# Plot: Average Rentals by Holiday and Weather
with tab2:
    st.header('Average Bike Rentals by Holiday and Weather Situation')

    if grouped_hour_data.empty:
        st.warning("No data available for the selected date range.")
    else:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=grouped_hour_data, x='holiday_desc', y='cnt', hue='weather_desc')

        plt.title('Average Bike Rentals by Holiday and Weather', fontsize=16)
        plt.xlabel('Holiday', fontsize=14)
        plt.ylabel('Average Bike Rentals', fontsize=14)
        plt.legend(title='Weather Situation', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        st.pyplot(plt.gcf())
        plt.close()

        st.markdown("""
        **Observation:**  
        Diagram tersebut menunjukkan bahwa penyewaan sepeda umumnya lebih tinggi pada hari biasa dibandingkan dengan hari libur, apapun situasi cuacanya. 
        Hal ini menunjukkan bahwa orang lebih cenderung menyewa sepeda pada hari kerja biasa, yang dimana saat hari libur mungkin orang lebih memilih untuk bepergian bersama keluarga.
        """)

# Plot: Average Rentals by Hour of the Day
with tab3:
    st.header('Average Bike Rentals by Hour of the Day')

    if hourly_peak_data.empty:
        st.warning("No data available for the selected date range.")
    else:
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=hourly_peak_data, x='hr', y='cnt', marker='o')

        plt.title('Average Bike Rentals by Hour of the Day', fontsize=16)
        plt.xlabel('Hour of the Day (0 - 23)', fontsize=14)
        plt.ylabel('Average Bike Rentals', fontsize=14)
        plt.xticks(range(0, 24))
        plt.tight_layout()

        st.pyplot(plt.gcf())
        plt.close()

        st.markdown("""
        **Observation:**  
        Grafik diatas menunjukkan bahwa Peak hours terjadi sekitar pukul 07:00-08:00 dan 16:00-18:00, kemungkinan karena itu adalah jam-jam masuk kerja dan pulang kerja.
        """)

# Plot: Registered vs Casual Users Across Days
with tab4:
    st.header('Registered Users vs Casual Users Across Days')

    if grouped_day_df.empty:
        st.warning("No data available for the selected date range.")
    else:
        plt.figure(figsize=(14, 6))

        sns.lineplot(data=grouped_day_df, x='dteday', y='registered', label='Registered Users')
        sns.lineplot(data=grouped_day_df, x='dteday', y='casual', label='Casual Users')

        plt.title('Registered vs Casual Users Across Days', fontsize=16)
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Number of Users', fontsize=14)
        plt.legend(title='User Type')
        plt.tight_layout()

        st.pyplot(plt.gcf())
        plt.close()

        st.markdown("""
        **Observation:**  
        Dari grafik diatas, jumlah pengguna terdaftar secara konsisten selalu melebihi jumlah pengguna biasa. 
        """)
