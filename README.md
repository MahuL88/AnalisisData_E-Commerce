# 🛍️ E-Commerce Dashboard  

Dashboard ini dibuat menggunakan **Streamlit** untuk menganalisis data _E-Commerce_ dari [Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Analisis mencakup penjualan, pengiriman, rating pelanggan, kategori produk, serta persebaran pelanggan secara geografis.

---

## ⚙️ Setup Environment 

### 1️⃣ Clone Repository
```bash
git clone https://github.com/MahuL88/AnalisisData_E-Commerce.git
cd AnalisisData_E-Commerce
```

### 2️⃣ Buat Virtual Environment
python -m venv env

### 3️⃣ Aktifkan Environment
```bash
# Windows
env\Scripts\activate

# Mac/Linux
source env/bin/activate
```
### 4️⃣ Install Dependencies
pip install -r requirements.txt

## ▶️ Run steamlit app
streamlit run dashboard.py

## Struktur Direktori

```plaintext
📦 AnalisisData_E-Commerce
 ┣ 📂dashboard
 ┃ ┣ 📂data
 ┃ ┃ ┣ 📜category_sales.csv
 ┃ ┃ ┣ 📜customer_geo_agg.csv
 ┃ ┃ ┣ 📜delayed_orders.csv
 ┃ ┃ ┣ 📜monthly_orders.csv
 ┃ ┃ ┣ 📜orders_shipping.csv
 ┃ ┃ ┣ 📜order_reviews.csv
 ┃ ┃ ┣ 📜rating_rendah.csv
 ┃ ┃ ┣ 📜revenue.csv
 ┃ ┃ ┣ 📜review_orderan.csv
 ┃ ┃ ┗ 📜seller_volume.csv
 ┃ ┗ 📜dashboard.py
 ┣ 📂E-commerce-public-dataset
 ┃ ┣ 📜customers_dataset.csv
 ┃ ┣ 📜geolocation_dataset.csv
 ┃ ┣ 📜New Text Document.txt
 ┃ ┣ 📜orders_dataset.csv
 ┃ ┣ 📜order_items_dataset.csv
 ┃ ┣ 📜order_payments_dataset.csv
 ┃ ┣ 📜order_reviews_dataset.csv
 ┃ ┣ 📜products_dataset.csv
 ┃ ┣ 📜product_category_name_translation.csv
 ┃ ┗ 📜sellers_dataset.csv
 ┣ 📜Proyek_Analisis_Data_Dicoding.ipynb
 ┣ 📜logo_eCom.png
 ┣ 📜README.md
 ┗ 📜requirements.txt
```
