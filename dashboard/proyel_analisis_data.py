import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    day_df = pd.read_csv("dashboard/day.csv")
    day_df['dteday'] = pd.to_datetime(day_df['dteday'], dayfirst=True)

    # Menambahkan kolom after_holiday
    holiday_dates = ["2011-12-25", "2012-12-25", "2011-01-01", "2012-01-01"]
    after_holidays = [(pd.to_datetime(date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d") for date in holiday_dates]
    day_df['after_holiday'] = day_df['dteday'].astype(str).isin(after_holidays)

    # Menambahkan kolom temp_deviation
    season_labels = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    day_df['season'] = day_df['season'].map(season_labels)
    avg_temp_per_season = day_df.groupby('season')['temp'].mean()
    day_df['temp_deviation'] = abs(day_df['temp'] - day_df['season'].map(avg_temp_per_season))
    
    return day_df

# Memuat data
df = load_data()

# Header Dashboard
st.title("Bike Sharing Dashboard")

# Sidebar
st.sidebar.header("Pengaturan")
menu = st.sidebar.radio(
    "Pilih Analisis",
    ["Tampilan Data", "Statistik Deskriptif", "Visualisasi"] 
)

# Fitur interaktif untuk filter
seasons = st.sidebar.multiselect("Pilih Musim:", options=df['season'].unique(), default=df['season'].unique())
workingday = st.sidebar.radio("Tampilkan Data:", ["Semua Hari", "Hari Kerja", "Hari Libur"])
workingday_filter = None if workingday == "Semua Hari" else 1 if workingday == "Hari Kerja" else 0

# Filter data berdasarkan input
filtered_data = df[df['season'].isin(seasons)]
if workingday_filter is not None:
    filtered_data = filtered_data[filtered_data['workingday'] == workingday_filter]

# Tampilan Data
if menu == "Tampilan Data":
    st.header("Tampilan Data")
    st.dataframe(filtered_data)

# Statistik Deskriptif
elif menu == "Statistik Deskriptif":
    st.header("Statistik Deskriptif")
    st.write(filtered_data.describe())

# Visualisasi
elif menu == "Visualisasi":
    st.header("Visualisasi Data")

    # Pilihan visualisasi interaktif
    visual_choice = st.selectbox("Pilih Visualisasi:", [
        "Distribusi Penyewaan Sepeda", 
        "Penyewaan Sepeda Berdasarkan Musim", 
        "Hubungan Suhu dengan Penyewaan",
        "Penyewaan Sepeda Setelah Libur Besar"
    ])
    
    if visual_choice == "Distribusi Penyewaan Sepeda":
        st.subheader("Distribusi Penyewaan Sepeda")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(filtered_data['cnt'], bins=30, kde=True, color="blue", ax=ax)
        ax.set_xlabel("Jumlah Penyewaan Sepeda")
        ax.set_ylabel("Frekuensi")
        ax.set_title("Distribusi Penyewaan Sepeda")
        st.pyplot(fig)

    elif visual_choice == "Penyewaan Sepeda Berdasarkan Musim":
        st.subheader("Penyewaan Sepeda Berdasarkan Musim")
        fig, ax = plt.subplots(figsize=(8, 5))
        season_avg = filtered_data.groupby('season')['cnt'].mean().reset_index()
        sns.lineplot(data=season_avg, x='season', y='cnt', marker='o', color="blue", linewidth=2)
        ax.set_xlabel("Musim")
        ax.set_ylabel("Jumlah Penyewaan Sepeda")
        ax.set_title("Penyewaan Sepeda Berdasarkan Musim")
        st.pyplot(fig)

    elif visual_choice == "Hubungan Suhu dengan Penyewaan":
        st.subheader("Hubungan Suhu dengan Penyewaan Sepeda")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=filtered_data, x='temp', y='cnt', alpha=0.7, color="red", ax=ax)
        ax.set_xlabel("Suhu (Normalized)")
        ax.set_ylabel("Jumlah Penyewaan Sepeda")
        ax.set_title("Hubungan antara Suhu dan Penyewaan Sepeda")
        st.pyplot(fig)

    elif visual_choice == "Penyewaan Sepeda Setelah Libur Besar":
        st.subheader("Penyewaan Sepeda Setelah Libur Besar")
        fig, ax = plt.subplots(figsize=(8, 5))
        avg_cnt = filtered_data.groupby("after_holiday")["cnt"].mean().reset_index()
        sns.barplot(data=avg_cnt, x="after_holiday", y="cnt", palette=["blue", "red"])
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Hari Biasa", "Setelah Libur Besar"])
        ax.set_xlabel("Kategori Hari")
        ax.set_ylabel("Jumlah Penyewaan Sepeda")
        ax.set_title("Distribusi Penyewaan Sepeda pada Hari Setelah Libur Besar vs Hari Biasa")
        st.pyplot(fig)
