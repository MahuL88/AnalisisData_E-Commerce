
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
import numpy as np
from streamlit_folium import st_folium
from babel.numbers import format_currency
sns.set(style='dark')


# ===============================
# Membuat Helper Function
# ===============================
def create_customer_geo_agg_df(df):
    """Menghitung jumlah pelanggan unik per kota dan koordinat rata-ratanya."""
    customer_geo_agg = (
        df
        .groupby(['geolocation_city', 'geolocation_state'], as_index=False)
        .agg({
            'customer_unique_id': 'nunique',
            'geolocation_lat': 'mean',
            'geolocation_lng': 'mean'
        })
        .rename(columns={'customer_unique_id': 'jumlah_customer'})
        .sort_values(by='jumlah_customer', ascending=False)
    )
    return customer_geo_agg


def create_rating_distribution_df(df,dfs):
    """Membuat distribusi jumlah order berdasarkan skor review."""
    distribusi = df[['order_id']].merge(dfs,on='order_id', how='inner')
    
    # Mengecek distribusi rating
    dist = (
        distribusi.groupby('review_score')['order_id']
        .nunique()
        .reset_index(name='jumlah_order')
        .sort_values(by='jumlah_order', ascending=False)
    )
    
    return dist

def create_low_rating_products_df(df):
    """Menghitung rasio review rendah (rating ≤2) per kategori produk."""
    total_reviews = (
        df
        .groupby('product_category_name_english')
        .size()
        .reset_index(name='total_review')
    )

    low_reviews = (
        df[df['review_score'] <= 2]
        .groupby('product_category_name_english')
        .size()
        .reset_index(name='low_review')
    )

    low_rating_ratio = (
        low_reviews
        .merge(total_reviews, on='product_category_name_english', how='left')
    )

    low_rating_ratio['low_review_ratio'] = (
        low_rating_ratio['low_review'] / low_rating_ratio['total_review'] * 100
    )

    rating_rendah = (
        low_rating_ratio[low_rating_ratio['total_review'] > 100]
        .sort_values(by='low_review_ratio', ascending=False)
    )
    return rating_rendah

def create_delayed_orders_df(df,dfs):
    """Menghitung pesanan yang terlambat dikirim ke kurir."""
    delayed_orders = (
        df
        .merge(dfs[['order_id', 'shipping_limit_date', 'order_delivered_carrier_date','late_delivery']], on='order_id', how='inner')
    )
    late_summary = (
        delayed_orders['late_delivery']
        .value_counts()
        .rename_axis('Delivery Status')
        .rename({True: 'Late', False: 'On Time'})
        .reset_index(name='Count')
    )
    return late_summary

def create_review_orderan_df(df):
    """Membuat Review orderan"""
    review_orderan = (df
    )
    return review_orderan

def create_monthly_orders_df(df):
    """Menghitung jumlah order unik per bulan."""
    df['order_month'] = df['order_purchase_timestamp'].dt.to_period('M')

    monthly_orders = (
        df.groupby('order_month')['order_id']
        .nunique()
        .reset_index(name='jumlah_order')
    )

    monthly_orders['order_month'] = monthly_orders['order_month'].dt.to_timestamp()
    return monthly_orders


def create_category_sales_df(df):
    """Menghitung total pembelian dan nilai penjualan per kategori produk."""
    category_sales = (
        df
        .groupby('product_category_name_english', as_index=False)
        .agg({
            'order_id': 'count',
            'price': 'sum'
        })
        .rename(columns={
            'order_id': 'jumlah_pembelian',
            'price': 'total_harga'
        })
        .sort_values(by='jumlah_pembelian', ascending=False)
    )
    return category_sales

def create_seller_volume_df(df, dfs):
    """Menghitung jumlah order dan total penjualan per seller."""
    seller_volume = (
        df
        .merge(dfs[['seller_id', 'seller_city', 'seller_state']], on='seller_id', how='left')
        .groupby(['seller_id', 'seller_city', 'seller_state'], as_index=False)
        .agg({
            'order_id': 'count',
            'price': 'sum'
        })
        .rename(columns={
            'order_id': 'jumlah_order',
            'price': 'total_penjualan'
        })
        .sort_values(by='jumlah_order', ascending=False)
    )
    return seller_volume

def create_monthly_orders_df(df):
    daily_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df
kategori = pd.read_csv("data/category_sales.csv")
cust = pd.read_csv("data/customer_geo_agg.csv")
delay = pd.read_csv("data/orders_shipping.csv")
order = pd.read_csv("data/monthly_orders.csv")
rating = pd.read_csv("data/rating_rendah.csv")
review = pd.read_csv("data/review_orderan.csv")
dist_rate = pd.read_csv("data/order_reviews.csv")
seller = pd.read_csv("data/seller_volume.csv")
revenue = pd.read_csv("data/revenue.csv")


# Kolom bertipe datetime
datetime_columns = ["order_purchase_timestamp","order_delivered_customer_date"
                    ,"order_estimated_delivery_date"]
datetime_columns_delay = ["shipping_limit_date","order_delivered_carrier_date","order_purchase_timestamp"]

revenue.sort_values(by="order_purchase_timestamp", inplace=True)
revenue.reset_index(inplace=True)
revenue["order_purchase_timestamp"]=pd.to_datetime(revenue["order_purchase_timestamp"])
 
for column in datetime_columns:
    review[column] = pd.to_datetime(review[column])
for column in datetime_columns_delay:
    delay[column] = pd.to_datetime(delay[column])

# membuat filter dengan widget date input serta menambahkan logo
min_date = revenue["order_purchase_timestamp"].min()
max_date = revenue["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/MahuL88/AnalisisData_E-Commerce/blob/main/logo.jpg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = revenue[(revenue["order_purchase_timestamp"] >= str(start_date)) & 
                (revenue["order_purchase_timestamp"] <= str(end_date))]

orderan_delay = create_delayed_orders_df(main_df,delay)
monthly_orders = create_monthly_orders_df(main_df)
rating_dist = create_rating_distribution_df(main_df,dist_rate)


st.header('E-commerce Dashboard :sparkles:')

st.subheader('Monthly Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = monthly_orders.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(monthly_orders.revenue.sum(), "BRL", locale='pt_BR') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders["order_purchase_timestamp"],
    monthly_orders["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Persentase Pengiriman Terlambat")
    fig2, ax2 = plt.subplots(figsize=(6,6)) 
    ax2.pie(
        orderan_delay['Count'],
        labels=orderan_delay['Delivery Status'],
        autopct='%1.1f%%',
        startangle=90,
        colors=sns.color_palette('Spectral')
    )
    st.pyplot(fig2)

with col2:
    st.subheader("Jumlah Orderan Berdasarkan Review Score")

    rating_sorted = rating_dist.sort_values(by="jumlah_order", ascending=False)

    rating_sorted["review_score"] = pd.Categorical(
        rating_sorted["review_score"],
        categories=rating_sorted["review_score"].tolist(),
        ordered=True
    )

    fig3, ax3 = plt.subplots(figsize=(6,6)) 
    ax3.bar(
        rating_sorted["review_score"].astype(str),
        rating_sorted["jumlah_order"],
        color=sns.color_palette('pastel',n_colors=len(rating_sorted))
    )
    ax3.set_xlabel("Review Score")
    ax3.set_ylabel("Jumlah Order")
    st.pyplot(fig3)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Kategori Paling Sering Dibeli")

    top_5 = kategori.head(5).sort_values(by="jumlah_pembelian", ascending=True)

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(top_5['product_category_name_english'], top_5['jumlah_pembelian'])
    ax.set_xlabel("Jumlah Pembelian")
    ax.set_ylabel("Kategori Produk")
    ax.set_title("5 kategori yang sering dibeli", fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.subheader(" Kategori Yang Jarang Dibeli")

    bottom_5 = kategori.tail(5).sort_values(by="jumlah_pembelian", ascending=False)

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(bottom_5['product_category_name_english'], bottom_5['jumlah_pembelian'], color="orange")
    ax.set_xlabel("Jumlah Pembelian")
    ax.set_ylabel("Kategori Produk")
    ax.set_title("5 kategori yang jarang dibeli", fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)

st.subheader("10 Penjual dengan Jumlah Pesanan dan Total Penjualan Tertinggi")

# Ambil 10 penjual teratas berdasarkan jumlah order
top_seller = seller.nlargest(10, 'jumlah_order').copy()

# Potong seller_id agar lebih pendek (biar rapi di sumbu X)
top_seller['short_id'] = top_seller['seller_id'].apply(lambda x: x[:3])

# Buat plot
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar chart untuk jumlah order (warna biru langit)
color = 'skyblue'
ax1.bar(top_seller['short_id'], top_seller['jumlah_order'], color=color)
ax1.set_xlabel('Seller ID (3 huruf pertama)')
ax1.set_ylabel('Jumlah Order', color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax1.tick_params(axis='x', rotation=45)

# Line chart untuk total penjualan (warna oranye)
ax2 = ax1.twinx()
color = 'orange'
ax2.plot(top_seller['short_id'], top_seller['total_penjualan'], color=color, marker='o')
ax2.set_ylabel('Total Penjualan', color=color)
ax2.tick_params(axis='y', labelcolor=color)

# Judul dan layout rapi
plt.title('Perbandingan Jumlah Pesanan dan Total Penjualan per Penjual')
plt.tight_layout()

# Tampilkan ke Streamlit
st.pyplot(fig)

st.subheader("10 Kategori Produk dengan Review Rendah (dalam Persentase)")

# Ambil 10 kategori dengan review terendah
low_rate = rating.head(10)

# Buat plot
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=low_rate,
    x='product_category_name_english',
    y='low_review_ratio',
    palette='crest_r',
    ax=ax
)

# Kustomisasi tampilan
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
ax.set_xlabel('Kategori Produk')
ax.set_ylabel('Persentase Review Rendah (%)')
ax.set_title('10 Kategori Produk dengan Review Skor Rendah')
ax.set_ylim(0, 100)
plt.tight_layout()

# Tampilkan di Streamlit
st.pyplot(fig)

st.set_page_config(layout="wide")
st.markdown("## 🌍 Persebaran Pelanggan Berdasarkan Letak Geografi")

# --- Data Example ---
# pastikan kamu sudah punya DataFrame `customer_geo_agg`
# dengan kolom: ['geolocation_city', 'geolocation_state', 'geolocation_lat', 'geolocation_lng', 'jumlah_customer']

# --- Hitung titik tengah peta ---
center_lat = cust['geolocation_lat'].mean()
center_lng = cust['geolocation_lng'].mean()

# --- Buat Peta Folium ---
m = folium.Map(location=[center_lat, center_lng], zoom_start=4)

# --- Tambahkan Marker untuk tiap kota ---
for _, row in cust.iterrows():
    radius = np.sqrt(row['jumlah_customer']) * 0.5  # skala radius biar proporsional
    folium.CircleMarker(
        location=[row['geolocation_lat'], row['geolocation_lng']],
        radius=radius,
        color='#66c2a5',  # warna biru pastel
        fill=True,
        fill_color='#66c2a5',
        fill_opacity=0.6,
        popup=f"{row['geolocation_city']}, {row['geolocation_state']}: {row['jumlah_customer']} pelanggan"
    ).add_to(m)

# --- Tampilkan Peta di Streamlit ---
st_folium(m, width=800, height=500)
