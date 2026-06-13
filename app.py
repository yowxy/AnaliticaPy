from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import base64
import json

app = Flask(__name__)

# ── Generate synthetic e-commerce sales data ──────────────────────────────────
np.random.seed(42)
n = 500

categories  = ['Elektronik', 'Fashion', 'Makanan', 'Olahraga', 'Kecantikan']
cities      = ['Surabaya', 'Jakarta', 'Bandung', 'Medan', 'Semarang']
months      = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des']

raw = {
    'bulan'    : np.random.choice(months, n),
    'kategori' : np.random.choice(categories, n),
    'kota'     : np.random.choice(cities, n),
    'penjualan': np.random.randint(1, 50, n),
    'harga'    : np.random.choice([150000, 250000, 500000, 750000, 1000000], n),
    'rating'   : np.round(np.random.uniform(3.0, 5.0, n), 1),
}
df = pd.DataFrame(raw)
df['total_pendapatan'] = df['penjualan'] * df['harga']

MONTH_ORDER = {m: i for i, m in enumerate(months)}

PALETTE = {
    'Elektronik' : '#7F77DD',
    'Fashion'    : '#D4537E',
    'Makanan'    : '#1D9E75',
    'Olahraga'   : '#BA7517',
    'Kecantikan' : '#D85A30',
}

def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=110, bbox_inches='tight',
                facecolor='none', transparent=True)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded

# ── Chart helpers ─────────────────────────────────────────────────────────────

def chart_tren_pendapatan():
    monthly = (df.groupby('bulan')['total_pendapatan']
                 .sum()
                 .reindex(months))
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.fill_between(range(len(months)), monthly.values / 1e6,
                    alpha=0.18, color='#7F77DD')
    ax.plot(range(len(months)), monthly.values / 1e6,
            color='#7F77DD', linewidth=2.5, marker='o', markersize=5)
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, fontsize=10)
    ax.set_ylabel('Pendapatan (Juta Rp)', fontsize=10)
    ax.yaxis.set_tick_params(labelsize=9)
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_color('#e0e0e0')
    ax.grid(axis='y', color='#f0f0f0', linewidth=0.8)
    fig.tight_layout()
    return fig_to_b64(fig)

def chart_kategori():
    cat = (df.groupby('kategori')['total_pendapatan']
             .sum()
             .sort_values(ascending=True))
    colors = [PALETTE[k] for k in cat.index]
    fig, ax = plt.subplots(figsize=(7, 3.4))
    bars = ax.barh(cat.index, cat.values / 1e6, color=colors,
                   height=0.55, edgecolor='none')
    for bar, val in zip(bars, cat.values):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'Rp {val/1e6:.0f} Jt', va='center', fontsize=9,
                color='#555')
    ax.set_xlabel('Pendapatan (Juta Rp)', fontsize=10)
    ax.spines[['top','right','left']].set_visible(False)
    ax.spines['bottom'].set_color('#e0e0e0')
    ax.grid(axis='x', color='#f0f0f0', linewidth=0.8)
    ax.tick_params(axis='y', labelsize=10)
    fig.tight_layout()
    return fig_to_b64(fig)

def chart_kota():
    kota = (df.groupby('kota')[['penjualan','total_pendapatan']]
              .agg({'penjualan':'sum','total_pendapatan':'sum'})
              .sort_values('total_pendapatan', ascending=False))
    x     = np.arange(len(kota))
    width = 0.38
    fig, ax1 = plt.subplots(figsize=(8, 3.6))
    ax2 = ax1.twinx()
    b1 = ax1.bar(x - width/2, kota['penjualan'],
                 width, color='#5DCAA5', label='Unit Terjual', edgecolor='none')
    b2 = ax2.bar(x + width/2, kota['total_pendapatan']/1e6,
                 width, color='#7F77DD', label='Pendapatan (Jt Rp)', edgecolor='none', alpha=0.85)
    ax1.set_xticks(x)
    ax1.set_xticklabels(kota.index, fontsize=10)
    ax1.set_ylabel('Unit Terjual', color='#1D9E75', fontsize=10)
    ax2.set_ylabel('Pendapatan (Jt Rp)', color='#534AB7', fontsize=10)
    ax1.tick_params(axis='y', colors='#1D9E75')
    ax2.tick_params(axis='y', colors='#534AB7')
    for sp in ['top']: ax1.spines[sp].set_visible(False)
    ax1.spines['bottom'].set_color('#e0e0e0')
    lines = [mpatches.Patch(color='#5DCAA5', label='Unit Terjual'),
             mpatches.Patch(color='#7F77DD', label='Pendapatan')]
    ax1.legend(handles=lines, loc='upper right', fontsize=9,
               frameon=False)
    fig.tight_layout()
    return fig_to_b64(fig)

def chart_rating():
    cat_rating = (df.groupby('kategori')['rating']
                    .mean()
                    .sort_values(ascending=False))
    colors = [PALETTE[k] for k in cat_rating.index]
    fig, ax = plt.subplots(figsize=(7, 3.2))
    bars = ax.bar(cat_rating.index, cat_rating.values,
                  color=colors, width=0.5, edgecolor='none')
    for bar, val in zip(bars, cat_rating.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', fontsize=9, color='#555')
    ax.set_ylim(3.0, 5.2)
    ax.set_ylabel('Rata-rata Rating', fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_color('#e0e0e0')
    ax.grid(axis='y', color='#f0f0f0', linewidth=0.8)
    ax.tick_params(axis='x', labelsize=10)
    fig.tight_layout()
    return fig_to_b64(fig)

def chart_heatmap():
    pivot = df.pivot_table(index='kategori', columns='bulan',
                           values='penjualan', aggfunc='sum')
    pivot = pivot.reindex(columns=months)
    fig, ax = plt.subplots(figsize=(11, 3.4))
    im = ax.imshow(pivot.values, aspect='auto', cmap='YlOrRd')
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, fontsize=9)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=10)
    for i in range(len(pivot.index)):
        for j in range(len(months)):
            ax.text(j, i, int(pivot.values[i, j]),
                    ha='center', va='center', fontsize=8,
                    color='white' if pivot.values[i,j] > pivot.values.max()*0.6 else '#333')
    plt.colorbar(im, ax=ax, label='Unit Terjual', shrink=0.8)
    ax.spines[:].set_visible(False)
    fig.tight_layout()
    return fig_to_b64(fig)

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summary')
def api_summary():
    return jsonify({
        'total_pendapatan' : int(df['total_pendapatan'].sum()),
        'total_transaksi'  : int(len(df)),
        'total_unit'       : int(df['penjualan'].sum()),
        'avg_rating'       : round(float(df['rating'].mean()), 2),
        'top_kategori'     : df.groupby('kategori')['total_pendapatan'].sum().idxmax(),
        'top_kota'         : df.groupby('kota')['total_pendapatan'].sum().idxmax(),
    })

@app.route('/api/charts/tren')
def api_tren():
    return jsonify({'image': chart_tren_pendapatan()})

@app.route('/api/charts/kategori')
def api_kategori():
    return jsonify({'image': chart_kategori()})

@app.route('/api/charts/kota')
def api_kota():
    return jsonify({'image': chart_kota()})

@app.route('/api/charts/rating')
def api_rating():
    return jsonify({'image': chart_rating()})

@app.route('/api/charts/heatmap')
def api_heatmap():
    return jsonify({'image': chart_heatmap()})

@app.route('/api/tabel')
def api_tabel():
    tabel = (df.groupby(['kategori','kota'])
               .agg(
                   unit_terjual   = ('penjualan','sum'),
                   total_pendapatan = ('total_pendapatan','sum'),
                   avg_rating     = ('rating','mean'),
               )
               .reset_index()
               .sort_values('total_pendapatan', ascending=False)
               .head(20))
    tabel['avg_rating'] = tabel['avg_rating'].round(2)
    return jsonify(tabel.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
