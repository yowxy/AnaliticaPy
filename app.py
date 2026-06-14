from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Load dataset
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, 'data', 'online_sales_dataset.csv')

# Read CSV and clean column headers
df = pd.read_csv(csv_path)
df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

# Parse date column
df['date'] = pd.to_datetime(df['date'])
df['month_name'] = df['date'].dt.strftime('%b')
df['month_num'] = df['date'].dt.month

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summary')
def api_summary():
    total_revenue = float(df['total_revenue'].sum())
    total_transactions = int(df.shape[0])
    total_units_sold = int(df['units_sold'].sum())
    avg_unit_price = float(df['unit_price'].mean())
    
    top_category = df.groupby('product_category')['total_revenue'].sum().idxmax()
    top_region = df.groupby('region')['total_revenue'].sum().idxmax()
    
    return jsonify({
        'total_pendapatan': total_revenue,
        'total_transaksi': total_transactions,
        'total_unit': total_units_sold,
        'avg_harga': avg_unit_price,
        'top_kategori': top_category,
        'top_region': top_region
    })

@app.route('/api/charts/tren')
def api_tren():
    monthly = df.groupby(['month_num', 'month_name'])['total_revenue'].sum().reset_index()
    monthly = monthly.sort_values('month_num')
    return jsonify({
        'labels': monthly['month_name'].tolist(),
        'values': monthly['total_revenue'].tolist()
    })

@app.route('/api/charts/kategori')
def api_kategori():
    cat = df.groupby('product_category')['total_revenue'].sum().reset_index()
    cat = cat.sort_values('total_revenue', ascending=False)
    return jsonify({
        'labels': cat['product_category'].tolist(),
        'values': cat['total_revenue'].tolist()
    })

@app.route('/api/charts/payment')
def api_payment():
    pay = df.groupby('payment_method')['total_revenue'].sum().reset_index()
    pay = pay.sort_values('total_revenue', ascending=False)
    return jsonify({
        'labels': pay['payment_method'].tolist(),
        'values': pay['total_revenue'].tolist()
    })

@app.route('/api/charts/region')
def api_region():
    reg = df.groupby('region').agg(
        total_revenue=('total_revenue', 'sum'),
        units_sold=('units_sold', 'sum')
    ).reset_index().sort_values('total_revenue', ascending=False)
    return jsonify({
        'labels': reg['region'].tolist(),
        'revenue': reg['total_revenue'].tolist(),
        'units': reg['units_sold'].tolist()
    })

@app.route('/api/charts/top_produk')
def api_top_produk():
    top_p = df.groupby('product_name').agg(
        revenue=('total_revenue', 'sum'),
        units=('units_sold', 'sum')
    ).reset_index().sort_values('revenue', ascending=False).head(10)
    return jsonify({
        'labels': top_p['product_name'].tolist(),
        'revenue': top_p['revenue'].tolist(),
        'units': top_p['units'].tolist()
    })

@app.route('/api/charts/heatmap')
def api_heatmap():
    pivot = df.pivot_table(
        index='product_category',
        columns=['month_num', 'month_name'],
        values='units_sold',
        aggfunc='sum',
        fill_value=0
    )
    # Reindex columns to sort chronologically by month_num
    pivot = pivot.reindex(sorted(pivot.columns, key=lambda x: x[0]), axis=1)
    
    series = []
    for cat in pivot.index:
        data = []
        for (month_num, month_name) in pivot.columns:
            data.append({
                'x': month_name,
                'y': int(pivot.loc[cat, (month_num, month_name)])
            })
        series.append({
            'name': cat,
            'data': data
        })
    return jsonify(series)

@app.route('/api/tabel')
def api_tabel():
    table_df = df.groupby(['product_category', 'region']).agg(
        unit_terjual=('units_sold', 'sum'),
        total_pendapatan=('total_revenue', 'sum'),
        avg_harga=('unit_price', 'mean'),
        jumlah_transaksi=('transaction_id', 'count')
    ).reset_index().sort_values('total_pendapatan', ascending=False).head(20)
    
    table_df['avg_harga'] = table_df['avg_harga'].round(2)
    table_df = table_df.rename(columns={
        'product_category': 'kategori',
        'region': 'region'
    })
    return jsonify(table_df.to_dict(orient='records'))

@app.route('/api/transactions')
def api_transactions():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search = request.args.get('search', '').strip().lower()
    category = request.args.get('category', 'all')
    region = request.args.get('region', 'all')
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    
    filtered_df = df.copy()
    
    # Search filter
    if search:
        filtered_df = filtered_df[
            filtered_df['product_name'].str.lower().str.contains(search) |
            filtered_df['product_category'].str.lower().str.contains(search) |
            filtered_df['region'].str.lower().str.contains(search) |
            filtered_df['payment_method'].str.lower().str.contains(search)
        ]
        
    # Category filter
    if category != 'all':
        filtered_df = filtered_df[filtered_df['product_category'] == category]
        
    # Region filter
    if region != 'all':
        filtered_df = filtered_df[filtered_df['region'] == region]
        
    # Sort
    ascending = (sort_order == 'asc')
    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(sort_by, ascending=ascending)
    else:
        # Default to date
        filtered_df = filtered_df.sort_values('date', ascending=ascending)
        
    total_records = len(filtered_df)
    total_pages = max(1, int(np.ceil(total_records / limit)))
    
    # Page boundary check
    page = max(1, min(page, total_pages))
    
    # Slice for page
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    sliced_df = filtered_df.iloc[start_idx:end_idx].copy()
    
    # Format dates to string
    sliced_df['date'] = sliced_df['date'].dt.strftime('%Y-%m-%d')
    
    # Get lists for filters in UI
    categories_list = sorted(df['product_category'].unique().tolist())
    regions_list = sorted(df['region'].unique().tolist())
    
    return jsonify({
        'transactions': sliced_df.to_dict(orient='records'),
        'total_pages': total_pages,
        'total_records': total_records,
        'current_page': page,
        'categories': categories_list,
        'regions': regions_list
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
