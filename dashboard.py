import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
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


def create_rating_distribution_df(df):
    """Membuat distribusi jumlah order berdasarkan skor review."""
    dist = (
        df
        .groupby('review_score')['order_id']
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

def create_delayed_orders_df(df):
    """Menghitung pesanan yang terlambat dikirim ke kurir."""
    df['delay_days'] = (
        df['order_delivered_carrier_date'] - df['shipping_limit_date']
    ).dt.days

    delayed_orders = df[df['late_delivery'] == True]
    return delayed_orders

def create_review_orderan_df(df,dfs):
    """Menggabungkan data review dengan tanggal pengiriman dan estimasi."""
    review_orderan = pd.merge(
        df[['order_id', 'order_delivered_customer_date', 'order_estimated_delivery_date']],
        dfs[['order_id', 'review_score']],
        on='order_id',
        how='left'
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

kategori = pd.read_csv("data/category_sales.csv")