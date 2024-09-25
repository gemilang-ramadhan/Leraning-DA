import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Pallette
sns.set_theme(style="whitegrid")
custom_palette = sns.color_palette("Set2")

# Streamlit page
st.set_page_config(
    page_title="Bike Rentals Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebart
st.sidebar.title("Bike Dataset Analysis")
st.sidebar.markdown("---") 

st.sidebar.markdown("""
**Created by:**\n
    Muhammad Gemilang Ramadhan  
    Bangkit ML-63 Cohort  

m004b4ky2856@bangkit.academy  
Finished on September 24th, 2024
""")

st.sidebar.markdown("---")

# Date input untuk sidebar
st.sidebar.header('📅 Select Date Range')
date_range = st.sidebar.date_input(
    'Choose a date range from 2011-01-01 to 2012-12-31',
    value=(pd.to_datetime('2011-01-01'), pd.to_datetime('2012-12-31')),
    min_value=pd.to_datetime('2011-01-01'), # Sesuai dengan dataset yang dimiliki
    max_value=pd.to_datetime('2012-12-31')
)

# date_range harus bertipe tuple/list agar streamlit bisa membandingkan datetype
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    st.error("## Please select a valid date range between 2011-01-01 and 2012-12-31")
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

# Load datasets
day_df, hour_df = load_data()

# Data Wrangling
weather_labels = {
    1: 'Clear, Few clouds, Partly cloudy',
    2: 'Mist + Cloudy, Mist + Broken clouds',
    3: 'Light Snow, Light Rain + Thunderstorm',
    4: 'Heavy Rain, Snow + Fog'
}

season_labels = {
    1: 'Spring',
    2: 'Summer',
    3: 'Fall',
    4: 'Winter'
}

day_df['weather_desc'] = day_df['weathersit'].map(weather_labels)
hour_df['weather_desc'] = hour_df['weathersit'].map(weather_labels)

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

# Additional Analysis: Clustering Users
def categorize_users(data, column):
    q1 = data[column].quantile(0.25)
    q3 = data[column].quantile(0.75)
    
    def categorize(value):
        if value < q1:
            return 'Low'
        elif q1 <= value <= q3:
            return 'Medium'
        else:
            return 'High'
    
    return data[column].apply(categorize)

# Apply clustering
grouped_day_df['casual_cluster'] = categorize_users(grouped_day_df, 'casual')
grouped_day_df['registered_cluster'] = categorize_users(grouped_day_df, 'registered')

# Create Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌦️ Season & Weather", 
    "🏖️ Holiday & Weather", 
    "⏰ Hourly Rentals", 
    "👥 Registered vs Casual Users", 
    "📊 User Clustering"
])

# Tab 1: Average Rentals by Season and Weather
with tab1:
    st.header('Average Bike Rentals by Season and Weather Situation')
    
    if grouped_data.empty:
        st.warning("No data available for the selected date range.")
    else:
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.barplot(
            data=grouped_data, 
            x='season_desc', 
            y='cnt', 
            hue='weather_desc', 
            palette=custom_palette, 
            edgecolor='white',
            ax=ax
        )
        
        ax.set_title('Average Bike Rentals by Season and Weather', fontsize=18, weight='bold')
        ax.set_xlabel('Season', fontsize=14)
        ax.set_ylabel('Average Bike Rentals', fontsize=14)
        ax.legend(title='Weather Situation', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12, title_fontsize=12)
        
        # Add data labels
        for p in ax.patches:
            height = p.get_height()
            if not np.isnan(height):
                ax.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., height), 
                            ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5),
                            textcoords='offset points')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.markdown("""
        **🔍 Insights:**  
        Kondisi cuaca ekstrem seperti hujan lebat atau salju ringan secara signifikan mengurangi penyewaan sepeda di semua musim. 
        Musim gugur menunjukkan tingkat penyewaan tertinggi, terutama saat cuaca cerah, yang mengindikasikan kondisi ideal untuk bersepeda.
        """)

# Tab 2: Average Rentals by Holiday and Weather
with tab2:
    st.header('Average Bike Rentals by Holiday and Weather Situation')
    
    if grouped_hour_data.empty:
        st.warning("No data available for the selected date range.")
    else:
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.barplot(
            data=grouped_hour_data, 
            x='holiday_desc', 
            y='cnt', 
            hue='weather_desc', 
            palette=custom_palette, 
            edgecolor='white',
            ax=ax
        )
        
        ax.set_title('Average Bike Rentals by Holiday and Weather', fontsize=18, weight='bold')
        ax.set_xlabel('Holiday', fontsize=14)
        ax.set_ylabel('Average Bike Rentals', fontsize=14)
        ax.legend(title='Weather Situation', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12, title_fontsize=12)
        
        # Add data labels
        for p in ax.patches:
            height = p.get_height()
            if not np.isnan(height):
                ax.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., height), 
                            ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5),
                            textcoords='offset points')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.markdown("""
        **🔍 Insights:**  
        Penyewaan sepeda lebih tinggi pada hari biasa dibandingkan hari libur, terlepas dari kondisi cuaca. 
        Hal ini mungkin disebabkan oleh preferensi individu menggunakan kendaraan pribadi saat berlibur. 
        Untuk mengatasi hal ini, fokuskan promosi pada hari libur dan alokasikan sumber daya tambahan selama periode permintaan tinggi.
        """)

# Tab 3: Average Rentals by Hour of the Day
with tab3:
    st.header('Average Bike Rentals by Hour of the Day')
    
    if hourly_peak_data.empty:
        st.warning("No data available for the selected date range.")
    else:
        fig, ax = plt.subplots(figsize=(16, 8))
        sns.lineplot(
            data=hourly_peak_data, 
            x='hr', 
            y='cnt', 
            marker='o', 
            color=custom_palette[2], 
            linewidth=2.5, 
            ax=ax
        )
        
        ax.set_title('Average Bike Rentals by Hour of the Day', fontsize=18, weight='bold')
        ax.set_xlabel('Hour of the Day (0 - 23)', fontsize=14)
        ax.set_ylabel('Average Bike Rentals', fontsize=14)
        ax.set_xticks(range(0, 24))
        ax.set_xticklabels(range(0, 24))
        ax.axvspan(7, 8, color='orange', alpha=0.3, label='Morning Peak')
        ax.axvspan(16, 18, color='green', alpha=0.3, label='Evening Peak')
        ax.legend(title='Peak Hours', loc='upper left', fontsize=12, title_fontsize=12)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.markdown("""
        **🔍 Insights:**  
        Jam puncak penyewaan terjadi antara pukul 07:00-08:00 dan 16:00-18:00, yang kemungkinan besar berkaitan dengan waktu masuk dan pulang kerja.
        """)

# Tab 4: Registered vs Casual Users
with tab4:
    st.header('Registered Users vs Casual Users Across Days')
    
    if grouped_day_df.empty:
        st.warning("No data available for the selected date range.")
    else:
        fig, ax = plt.subplots(figsize=(18, 8))
        
        sns.lineplot(
            data=grouped_day_df, 
            x='dteday', 
            y='registered', 
            label='Registered Users', 
            color=custom_palette[0], 
            linewidth=2.5, 
            ax=ax
        )
        sns.lineplot(
            data=grouped_day_df, 
            x='dteday', 
            y='casual', 
            label='Casual Users', 
            color=custom_palette[1], 
            linewidth=2.5, 
            ax=ax
        )
        
        ax.set_title('Registered vs Casual Users Across Days', fontsize=18, weight='bold')
        ax.set_xlabel('Date', fontsize=14)
        ax.set_ylabel('Number of Users', fontsize=14)
        ax.legend(title='User Type', fontsize=12, title_fontsize=12)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.markdown("""
        **🔍 Insights:**  
        Registered user secara konsisten selalu melebihi pengguna casual
        """)

# Tab 5: User Clustering Analysis
with tab5:
    st.header('Clustering Analysis of Users')
    
    if grouped_day_df.empty:
        st.warning("No data available for the selected date range.")
    else:
        st.subheader('🔹 Casual Users Clustering')
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.countplot(
            data=grouped_day_df, 
            x='casual_cluster', 
            palette=custom_palette, 
            edgecolor='white', 
            ax=ax1
        )
        ax1.set_title('Clustering of Casual Users (Low, Medium, High)', fontsize=16, weight='bold')
        ax1.set_xlabel('Cluster', fontsize=14)
        ax1.set_ylabel('Number of Days', fontsize=14)
        
        # Add counts
        for p in ax1.patches:
            height = p.get_height()
            ax1.annotate(f'{height}', (p.get_x() + p.get_width() / 2., height), 
                        ha='center', va='bottom', fontsize=12, color='black', xytext=(0, 5),
                        textcoords='offset points')
        
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close()
        
        st.subheader('🔹 Registered Users Clustering')
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.countplot(
            data=grouped_day_df, 
            x='registered_cluster', 
            palette=custom_palette, 
            edgecolor='white', 
            ax=ax2
        )
        ax2.set_title('Clustering of Registered Users (Low, Medium, High)', fontsize=16, weight='bold')
        ax2.set_xlabel('Cluster', fontsize=14)
        ax2.set_ylabel('Number of Days', fontsize=14)
        
        # Add counts
        for p in ax2.patches:
            height = p.get_height()
            ax2.annotate(f'{height}', (p.get_x() + p.get_width() / 2., height), 
                        ha='center', va='bottom', fontsize=12, color='black', xytext=(0, 5),
                        textcoords='offset points')
        
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()
        
        st.markdown("""
        **🔍 Insights:**
        Mayoritas hari termasuk dalam kategori 'Medium' untuk penyewaan pengguna casual, menunjukkan penggunaan harian yang rata-rata.
        """)

