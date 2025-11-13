import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import st_folium
from babel.numbers import format_currency
sns.set(style='dark')

st.set_page_config(layout="wide")

# ===============================
# Membuat Helper Function
# ===============================
def create_rating_distribution_df(df,dfs):
    """Membuat distribusi Jumlah Orderan pada setiap Review Score"""
    distribusi = df[['order_id']].merge(dfs,on='order_id', how='inner')
    
    # Mengecek distribusi rating
    dist = (
        distribusi.groupby('review_score')['order_id']
        .nunique()
        .reset_index(name='jumlah_order')
        .sort_values(by='jumlah_order', ascending=False)
    )
    
    return dist

def create_delayed_orders_df(df,dfs):
    """Menghitung Pesanan yang Terlambat Dikirim ke Kurir."""
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

#-----------
# Load Data
#-----------
kategori = pd.read_csv("data/category_sales.csv")
cust = pd.read_csv("data/customer_geo_agg.csv")
delay = pd.read_csv("data/orders_shipping.csv")
rating = pd.read_csv("data/rating_rendah.csv")
dist_rate = pd.read_csv("data/order_reviews.csv")
seller = pd.read_csv("data/seller_volume.csv")
revenue = pd.read_csv("data/revenue.csv")

# Kolom bertipe datetime
datetime_columns = ["shipping_limit_date","order_delivered_carrier_date","order_purchase_timestamp"]
for column in datetime_columns:
    delay[column] = pd.to_datetime(delay[column])

revenue.sort_values(by="order_purchase_timestamp", inplace=True)
revenue["order_purchase_timestamp"]=pd.to_datetime(revenue["order_purchase_timestamp"])

# membuat filter dengan widget date input serta menambahkan logo
min_date = revenue["order_purchase_timestamp"].min()
max_date = revenue["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/MahuL88/AnalisisData_E-Commerce/main/logo_eCom.png")
    
    # Informasi Tambahan
    highest_city = cust.loc[cust['jumlah_customer'].idxmax(), 'geolocation_city']
    st.markdown(f"🏙️ Kota dengan pelanggan terbanyak : ***{highest_city}***")

    top_product = kategori.loc[kategori['jumlah_pembelian'].idxmax(), 'product_category_name_english']
    st.markdown(f"🛒 Produk yang paling laris 🔥: ***{top_product}***")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,         # batas
        value=[min_date, max_date]  # range awal di widget
    )

main_df = revenue[(revenue["order_purchase_timestamp"] >= str(start_date)) & 
                (revenue["order_purchase_timestamp"] <= str(end_date))]

# Panggil Helper Function
orderan_delay = create_delayed_orders_df(main_df,delay)
monthly_orders = create_monthly_orders_df(main_df)
rating_dist = create_rating_distribution_df(main_df,dist_rate)

#____________
# VISUALISASI
#____________

st.markdown("""
<h1 style='text-align: center; color: #2e7d32;'>
🛍️ E-Commerce Dashboard <br>
<small style='color: grey; font-size: 20px;'>📊 Olist E-Commerce Analysis</small>
</h1>
""", unsafe_allow_html=True)

st.subheader('Monthly Orders')

# Kolom untuk total pesanan dan pendapatan 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = monthly_orders.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(monthly_orders.revenue.sum(), "BRL", locale='pt_BR') 
    st.metric("Total Revenue", value=total_revenue)

# Kolom untuk Plot Jumlah Pesanan Setiap Bulan 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders["order_purchase_timestamp"],
    monthly_orders["order_count"],
    marker='o', 
    linewidth=2,
    color="#2E99F0"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.grid(True, linestyle='--', alpha=0.6, color ='grey')
 
st.pyplot(fig)

# Kolom untuk Persentase Pengiriman terlambat dan Jumlah Orderan dari setiap Review Score 
col1, col2 = st.columns(2)

with col1:
    st.markdown(
    "<h3 style='text-align: center;'>Persentase Pengiriman <br> Pesananan yang Terlambat</h3>",
    unsafe_allow_html=True
)
    # Menampilkan pie plot dari persentase pengiriman
    fig2, ax2 = plt.subplots(figsize=(6,6)) 
    ax2.pie(
        orderan_delay['Count'],
        labels=orderan_delay['Delivery Status'],
        autopct='%1.2f%%',
        startangle=90,
        colors=sns.color_palette('Spectral')
    )
    st.pyplot(fig2)

with col2:
    st.markdown(
    "<h3 style='text-align: center;'>Jumlah Orderan pada setiap <br> Review Score</h3>",
    unsafe_allow_html=True
)   
    # Mengurutkan rating dari yang terbesar
    rating_sorted = rating_dist.sort_values(by="review_score", ascending=False)

    # Membuat kolom review menjadi kategorikal agar bisa diurutkan
    rating_sorted["review_score"] = pd.Categorical(
        rating_sorted["review_score"], # ambil
        categories=rating_sorted["review_score"].tolist(), # buat ke list dan jadikan list tsb jadi urutan nantinya(bukan otomatis)
        ordered=True # agar menjadi berurutan
    )

    # Menampilkan bar plot dari review Score
    fig3, ax3 = plt.subplots(figsize=(6,6)) 
    ax3.bar(
        rating_sorted["review_score"].astype(str),
        rating_sorted["jumlah_order"],
        color=sns.color_palette('pastel',n_colors=len(rating_sorted))
    )
    ax3.set_xlabel("Review Score")
    ax3.set_ylabel("Jumlah Order")
    ax3.grid(axis='y', linestyle='--', alpha=0.7, color ='grey')
    st.pyplot(fig3)

# Kolom Untuk kategori yang sering dan jarang di beli
col1, col2 = st.columns(2)

with col1:
    st.subheader("Kategori Paling Sering Dibeli")

    # Memfilter data 5 kategori tertinggi
    top_5 = kategori.head(5).sort_values(by="jumlah_pembelian", ascending=True)

    # Menyoroti kategori yang jumlah pembeliannya terbanyak
    max_value = top_5['jumlah_pembelian'].max()
    colors = ["#23FF0B" if v == max_value else 'lightgreen' for v in top_5['jumlah_pembelian']]

    # Menampilkan horizontal bar plot 
    fig, ax4 = plt.subplots(figsize=(6, 3))
    ax4.barh(top_5['product_category_name_english'], top_5['jumlah_pembelian'],color=colors)
    ax4.set_ylabel("Kategori Produk")
    ax4.grid(axis='x', linestyle='--', alpha=0.7, color ='grey')
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.subheader("Kategori Yang Jarang Dibeli")

    # Memfilter data 5 kategori terendah
    bottom_5 = kategori.tail(5).sort_values(by="jumlah_pembelian", ascending=False)

    # Menyoroti kategori yang jumlah pembeliannya sedikit
    min_value = bottom_5['jumlah_pembelian'].min()
    colors2 = ["#ff6600" if v == min_value else '#ffcc99' for v in bottom_5['jumlah_pembelian']]

    # Menampilkan horizontal bar plot
    fig, ax5 = plt.subplots(figsize=(6, 3))
    ax5.barh(bottom_5['product_category_name_english'], bottom_5['jumlah_pembelian'], color=colors2)
    ax5.set_xticks(range(0, 20, 5))
    ax5.set_ylabel("Kategori Produk")
    ax5.grid(axis='x', linestyle='--', alpha=0.7, color ='grey')
    plt.tight_layout()
    st.pyplot(fig)

# Kolom Untuk Penjual yang memiliki jumlah pesanan terbanyak
st.subheader("10 Penjual dengan Jumlah Pesanan dan Total Harga Penjualan Tertinggi")

# Memfilter data penjual berdasarkan jumlah order terbanyak yang diterima
top_seller = seller.head(10)

# Ambil 3 huruf dari seller id agar terlihat lebih rapi dan tidak kepanjangan
top_seller['short_id'] = top_seller['seller_id'].apply(lambda x: x[:3])

# Menyoroti penjual yang jumlah orderan diterima paling banyak
colors3 = ['skyblue' if v != max(top_seller['jumlah_order']) else 'dodgerblue' for v in top_seller['jumlah_order']]

# Menampilkan bar plot dan line chart (twinx)
fig, ax6 = plt.subplots(figsize=(10, 6))

# Bar chart untuk jumlah order (warna biru)
ax6.bar(top_seller['short_id'], top_seller['jumlah_order'], color=colors3)
ax6.set_ylabel('Jumlah Order', color='dodgerblue')
ax6.tick_params(axis='y', labelcolor='dodgerblue')
ax6.tick_params(axis='x')

# Line chart untuk total penjualan (warna orange)
ax7 = ax6.twinx()
color = 'orange'
ax7.plot(top_seller['short_id'], top_seller['total_penjualan'], color=color, marker='o')
ax7.set_ylabel('Total Penjualan', color=color)
ax7.tick_params(axis='y', labelcolor=color)
ax6.grid(True, linestyle='--', alpha=0.6, color ='grey')
plt.tight_layout()
st.pyplot(fig)

# Kolom Untuk kategori produk yang mendapat review rendah
st.subheader("Kategori Produk yang sering Mendapat Review Rendah (%)")

# Memfilter data kategori dengan review terendah
low_rate = rating.head(10)

# Menampilkan bar plot
fig, ax8 = plt.subplots(figsize=(9, 4))
sns.barplot(
    data=low_rate,
    y='product_category_name_english',
    x='low_review_ratio',
    palette='crest_r',
    ax=ax8,
    orient='h' 
)
ax8.set_xlabel('Persentase Review(%)')
ax8.set_ylabel('Kategori Produk')
ax8.set_xlim(0, 100)
ax8.grid(axis='x', linestyle='--', alpha=0.7, color ='grey')
plt.tight_layout()
st.pyplot(fig)

# Kolom Untuk Demografi Pelanggan
st.markdown("## 🌍 Demografi Customer Berdasarkan Letak Geografi")

# Menggabungkan kota di setiap provinsi(negara bagian) dan dijumlahkan
state_agg = (
    cust.groupby('geolocation_state', as_index=False).agg({
        'geolocation_lat': 'mean',
        'geolocation_lng': 'mean',
        'jumlah_customer': 'sum'
    })
)

# Mengambil URL GEOJSON (bentuk peta wilayah) Brazil dimana file ini menyimpan batas geografis wilayah
url_geojson = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

# Membuat Peta Dasar dengan koordinat yang ditempatkan di brazil
m = folium.Map(location=[-15.788497, -47.879873], zoom_start=4)

# Membuat Choropleth Layer agar wilayah diwarnai dengan bentuk poligon/area
folium.Choropleth(
    geo_data=url_geojson,
    name='choropleth',
    data=state_agg,
    columns=['geolocation_state', 'jumlah_customer'], # key, value
    key_on='feature.properties.sigla',                # ambil sigla dari GeoJSON
    fill_color='YlOrRd',                              # skema warnanya(Yellow, Green, dan Blue)
    fill_opacity=0.7,                                 # opasitas warna
    line_opacity=0.2,
    legend_name='Jumlah Customer di setiap Provinsi/State'
).add_to(m)

# Membuat Marker Pop-up untuk setiap Provinsi
for _, row in state_agg.iterrows(): # iterasi berdasarkan baris 
    
    # Membuat tanda di peta folium
    folium.Marker(                  
        location=[row['geolocation_lat'], row['geolocation_lng']],
        popup=f"""
        <div style="font-family:Arial; font-size:12px; width:100px;">
            <strong>State📍:</strong> {row['geolocation_state']}<br>
            <strong>Jumlah Cust🛒 :</strong> {row['jumlah_customer']:,} Pelanngan
        </div>
        """,
        icon=folium.Icon(color='blue', icon='info-sign') 
    ).add_to(m)

# Menampilkan Peta
st_folium(m, width=800, height=500)
