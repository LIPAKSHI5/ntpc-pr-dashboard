import matplotlib
matplotlib.use('Agg')

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime


def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_bytes = buf.read()
    base64_str = base64.b64encode(img_bytes).decode('utf-8')
    buf.close()
    return base64_str


def perform_analysis(database_path):
    with sqlite3.connect(database_path) as conn:
        df = pd.read_sql_query('SELECT * FROM pr_entries WHERE visible_to_user = 1', conn)

    if df.empty:
        return {"error": "No data available"}

    # 1️⃣ PR Status Chart
    status_counts = df['status'].value_counts()
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    status_counts.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_title('PR Status Count')
    ax1.set_xlabel('Status')
    ax1.set_ylabel('Count')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    pr_status_img = plot_to_base64(fig1)
    plt.close(fig1)

    # 2️⃣ Vendor Performance Chart (Enlarged & Clear)
    vendor_counts = df['vendor_name'].value_counts()
    fig2, ax2 = plt.subplots(figsize=(10, len(vendor_counts) * 1.2 if len(vendor_counts) > 0 else 6))
    vendor_counts.plot(kind='barh', ax=ax2, color='lightgreen')
    ax2.set_title('Vendor Performance (No. of PRs)', fontsize=14)
    ax2.set_xlabel('Number of PRs', fontsize=12)
    ax2.set_ylabel('Vendor Name', fontsize=12)
    ax2.tick_params(axis='y', labelsize=12)
    ax2.tick_params(axis='x', labelsize=10)
    ax2.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    vendor_perf_img = plot_to_base64(fig2)
    plt.close(fig2)

    # 3️⃣ PR Delay Prediction
    df['bod'] = pd.to_datetime(df['bod'], errors='coerce')
    df['delay_status'] = df['bod'].apply(lambda x: 'On Time' if pd.isnull(x) or x >= datetime.now() else 'Delayed')
    delay_counts = df['delay_status'].value_counts()
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    delay_counts.plot(kind='bar', ax=ax3, color='orange')
    ax3.set_title('PR Delay Prediction')
    ax3.set_xlabel('Status')
    ax3.set_ylabel('Count')
    ax3.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    delay_img = plot_to_base64(fig3)
    plt.close(fig3)

    # 4️⃣ High-Value Vendors (Total Vendor Amount)
    df['vendor_amount'] = pd.to_numeric(df['vendor_amount'], errors='coerce')
    vendor_amount_sum = df.groupby('vendor_name')['vendor_amount'].sum().sort_values(ascending=False)
    fig4, ax4 = plt.subplots(figsize=(8, len(vendor_amount_sum) * 0.6))
    vendor_amount_sum.plot(kind='barh', ax=ax4, color='purple')
    ax4.set_title('Total Vendor Amount (₹)')
    ax4.set_xlabel('Amount (₹)')
    ax4.set_ylabel('Vendor')
    plt.tight_layout()
    vendor_amount_img = plot_to_base64(fig4)
    plt.close(fig4)

    # 5️⃣ Payment Status Distribution
    payment_counts = df['vendor_payment_status'].value_counts()
    fig5, ax5 = plt.subplots(figsize=(5, 4))
    payment_counts.plot(kind='pie', ax=ax5, autopct='%1.1f%%', startangle=90, colors=['lightblue', 'lightgreen', 'pink'])
    ax5.set_ylabel('')
    ax5.set_title('Vendor Payment Status Distribution')
    plt.tight_layout()
    payment_status_img = plot_to_base64(fig5)
    plt.close(fig5)

    # 6️⃣ PRs Over Time (Monthly)
    df['updated_on_date'] = pd.to_datetime(df['updated_on_date'], errors='coerce')
    monthly_counts = df['updated_on_date'].dt.to_period('M').value_counts().sort_index()
    fig6, ax6 = plt.subplots(figsize=(8, 4))
    monthly_counts.plot(kind='bar', ax=ax6, color='orange')
    ax6.set_title('PRs Raised Over Time')
    ax6.set_xlabel('Month')
    ax6.set_ylabel('No. of PRs')
    plt.tight_layout()
    monthly_prs_img = plot_to_base64(fig6)
    plt.close(fig6)

    # 7️⃣ PRs by Location
    location_counts = df['location'].value_counts()
    fig7, ax7 = plt.subplots(figsize=(8, 4))
    location_counts.plot(kind='bar', ax=ax7, color='teal')
    ax7.set_title('PR Count by Location')
    ax7.set_xlabel('Location')
    ax7.set_ylabel('No. of PRs')
    plt.tight_layout()
    location_img = plot_to_base64(fig7)
    plt.close(fig7)

    return {
        'pr_status_img': pr_status_img,
        'vendor_perf_img': vendor_perf_img,
        'delay_prediction_img': delay_img,
        'vendor_amount_img': vendor_amount_img,
        'payment_status_img': payment_status_img,
        'monthly_prs_img': monthly_prs_img,
        'location_img': location_img
    }
