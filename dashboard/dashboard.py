import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Judul dashboard
st.title('🚲 Bike-Sharing Demand Analytics Dashboard')

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("day.csv")  # Pastikan path file relatif dari lokasi script
    df['dteday'] = pd.to_datetime(df['dteday'], dayfirst=True)
    df['day_type'] = np.where(df['holiday'] == 1, 'Holiday',
                              np.where(df['workingday'] == 1, 'Working Day', 'Weekend'))
    df['weather_name'] = df['weathersit'].map({
        1: 'Clear',
        2: 'Mist',
        3: 'Light Rain/Snow',
        4: 'Heavy Rain/Snow'
    })
    df['year'] = df['dteday'].dt.year
    df['month'] = df['dteday'].dt.month_name()
    df['month_order'] = df['dteday'].dt.month
    return df

df = load_data()

# Sidebar
st.sidebar.header('🔍 Filter Data')
selected_years = st.sidebar.multiselect(
    'Pilih Tahun:',
    options=sorted(df['year'].unique()),
    default=sorted(df['year'].unique())
)

selected_months = st.sidebar.multiselect(
    'Pilih Bulan:',
    options=list(df['month'].unique()),
    default=['June', 'July', 'August']
)

# Filter data
filtered_df = df[
    (df['year'].isin(selected_years)) &
    (df['month'].isin(selected_months))
]

# Data mentah
with st.expander("📁 Lihat Data Mentah"):
    st.dataframe(filtered_df, use_container_width=True, height=250)

# Tabs layout
tab1, tab2, tab3 = st.tabs(["📊 Tren Harian", "⛅ Pengaruh Cuaca", "📈 Analisis Musiman"])

with tab1:
    st.subheader("📅 Analisis Pola Harian")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Rata-rata Penyewaan per Jenis Hari**")
        fig, ax = plt.subplots(figsize=(8,5))
        sns.barplot(
            x='day_type',
            y='cnt',
            data=filtered_df,
            estimator=np.mean,
            order=['Working Day', 'Weekend', 'Holiday'],
            palette="viridis",
            ax=ax
        )
        ax.set_ylabel('Rata-rata Penyewaan')
        ax.set_xlabel('')
        ax.set_title('Penyewaan Berdasarkan Jenis Hari')
        st.pyplot(fig)

    with col2:
        st.markdown("**Distribusi Penyewaan Harian**")
        day_type = st.selectbox(
            'Pilih Jenis Hari',
            options=filtered_df['day_type'].unique()
        )
        fig, ax = plt.subplots(figsize=(8,5))
        sns.histplot(
            data=filtered_df[filtered_df['day_type'] == day_type],
            x='cnt',
            bins=20,
            kde=True,
            color="orange",
            ax=ax
        )
        ax.set_title(f'Distribusi Penyewaan: {day_type}')
        ax.set_xlabel('Jumlah Penyewaan')
        st.pyplot(fig)

with tab2:
    st.subheader("🌦️ Dampak Kondisi Cuaca")

    st.markdown("**Korelasi Variabel Cuaca dan Penyewaan**")
    corr_matrix = filtered_df[['temp', 'hum', 'windspeed', 'cnt']].corr()
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    st.markdown("**Penyewaan Berdasarkan Kondisi Cuaca**")
    weather_choice = st.radio("Pilih Tipe Visualisasi:", ("Rata-rata", "Distribusi"), horizontal=True)

    fig, ax = plt.subplots(figsize=(10,5))
    if weather_choice == "Rata-rata":
        sns.barplot(
            x='weather_name',
            y='cnt',
            data=filtered_df,
            estimator=np.mean,
            order=['Clear', 'Mist', 'Light Rain/Snow', 'Heavy Rain/Snow'],
            palette="Blues",
            ax=ax
        )
    else:
        sns.boxplot(
            x='weather_name',
            y='cnt',
            data=filtered_df,
            order=['Clear', 'Mist', 'Light Rain/Snow', 'Heavy Rain/Snow'],
            palette="Blues",
            ax=ax
        )
    ax.set_title('Pengaruh Cuaca terhadap Penyewaan')
    st.pyplot(fig)

with tab3:
    st.subheader("📆 Analisis Tren Musiman")

    st.markdown("**Tren Penyewaan Bulanan per Tahun**")
    fig, ax = plt.subplots(figsize=(12,6))
    sns.lineplot(
        x='month_order',
        y='cnt',
        hue='year',
        data=filtered_df,
        marker='o',
        palette="tab10",
        ax=ax
    )
    month_names = df[['month_order', 'month']].drop_duplicates().sort_values('month_order')
    ax.set_xticks(month_names['month_order'])
    ax.set_xticklabels(month_names['month'], rotation=45)
    ax.set_title('Tren Penyewaan Bulanan')
    ax.set_xlabel('Bulan')
    ax.set_ylabel('Jumlah Penyewaan')
    st.pyplot(fig)

    st.markdown("**Rata-rata Penyewaan per Tahun**")
    year_avg = filtered_df.groupby('year')['cnt'].mean()
    st.bar_chart(year_avg)

# Key Metrics
st.header("📌 Key Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Rata-rata Penyewaan", f"{filtered_df['cnt'].mean():,.0f} sewa/hari")

with col2:
    max_day = filtered_df.loc[filtered_df['cnt'].idxmax()]
    st.metric("Hari Teramai", f"{max_day['cnt']:,}", f"{max_day['dteday'].strftime('%d %b %Y')}")

with col3:
    min_day = filtered_df.loc[filtered_df['cnt'].idxmin()]
    st.metric("Hari Tersepi", f"{min_day['cnt']:,}", f"{min_day['dteday'].strftime('%d %b %Y')}")

# Rekomendasi
st.header("💡 Rekomendasi Bisnis")
with st.expander("Lihat Saran Strategis Berdasarkan Data"):
    st.markdown("""
    **1. Alokasi Sepeda**
    - Tambah stok 20% saat akhir pekan
    - Kurangi stok 30% pada kondisi cuaca buruk

    **2. Strategi Harga**
    - Terapkan dynamic pricing di weekend (+15%)
    - Diskon saat hujan ringan (-20%)

    **3. Operasional**
    - Tingkatkan staf di bulan Juni–Agustus
    - Siapkan shelter tambahan saat musim hujan

    **4. Promosi**
    - Paket "Weekend Adventure" untuk pengguna kasual
    - Program loyalitas pengguna aktif
    """)

# Footer
st.markdown("---")
st.caption(f"Dashboard dibuat dengan ❤️ menggunakan Streamlit | Data: Bike-sharing Dataset (2011–2012)\n\nUpdate terakhir: {datetime.now().strftime('%d %B %Y')}")
