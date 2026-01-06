"""
Aplikasi Streamlit: Simulasi Antrian Drive-Thru Restaurant
TA-14 Praktikum Pemodelan dan Simulasi

Aplikasi web interaktif untuk mensimulasikan dan menganalisis 
sistem antrian drive-thru dengan berbagai skenario.
"""

import streamlit as st
import simpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

# Konfigurasi halaman
st.set_page_config(
    page_title="Simulasi Drive-Thru",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS custom
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# CLASS SIMULASI (SAMA SEPERTI DI NOTEBOOK)
# ============================================================================

class DriveThruSimulation:
    """Class untuk simulasi sistem antrian drive-thru"""
    
    def __init__(self, env, num_counters, warm_up_period, 
                 inter_arrival_mean, service_time_min, service_time_max):
        """
        Inisialisasi simulasi
        
        Parameters:
        - env: SimPy environment
        - num_counters: Jumlah loket yang tersedia
        - warm_up_period: Durasi warm-up period (menit)
        - inter_arrival_mean: Mean inter-arrival time (menit)
        - service_time_min: Waktu layanan minimum (menit)
        - service_time_max: Waktu layanan maksimum (menit)
        """
        self.env = env
        self.counter = simpy.Resource(env, capacity=num_counters)
        self.num_counters = num_counters
        self.warm_up_period = warm_up_period
        self.inter_arrival_mean = inter_arrival_mean
        self.service_time_min = service_time_min
        self.service_time_max = service_time_max
        
        # Data logging
        self.customers_data = []
        self.queue_length = []
        self.customer_count = 0
    
    def car_arrival_generator(self):
        """Generator untuk membangkitkan kedatangan mobil"""
        while True:
            inter_arrival = np.random.exponential(self.inter_arrival_mean)
            yield self.env.timeout(inter_arrival)
            
            self.customer_count += 1
            customer_id = self.customer_count
            
            self.env.process(self.service_process(customer_id))
    
    def service_process(self, customer_id):
        """Proses layanan untuk setiap mobil/customer"""
        arrival_time = self.env.now
        queue_len = len(self.counter.queue)
        self.queue_length.append((arrival_time, queue_len))
        
        with self.counter.request() as request:
            yield request
            
            service_start_time = self.env.now
            service_duration = np.random.uniform(self.service_time_min, self.service_time_max)
            
            yield self.env.timeout(service_duration)
            
            service_end_time = self.env.now
            queue_time = service_start_time - arrival_time
            total_time_in_system = service_end_time - arrival_time
            
            if arrival_time >= self.warm_up_period:
                self.customers_data.append({
                    'customer_id': customer_id,
                    'arrival_time': arrival_time,
                    'service_start_time': service_start_time,
                    'service_end_time': service_end_time,
                    'queue_time': queue_time,
                    'service_duration': service_duration,
                    'total_time_in_system': total_time_in_system
                })
    
    def run_simulation(self, sim_time):
        """Jalankan simulasi"""
        self.env.process(self.car_arrival_generator())
        self.env.run(until=sim_time)
        df = pd.DataFrame(self.customers_data)
        return df

# ============================================================================
# FUNGSI HELPER
# ============================================================================

def calculate_metrics(df, num_counters, analysis_time):
    """Hitung metrik performa dari hasil simulasi"""
    if len(df) == 0:
        return {}
    
    total_service_time = df['service_duration'].sum()
    utilization = (total_service_time / (num_counters * analysis_time)) * 100
    long_wait_pct = ((df['queue_time'] > 10).sum() / len(df)) * 100
    
    metrics = {
        'total_customers': len(df),
        'avg_queue_time': df['queue_time'].mean(),
        'median_queue_time': df['queue_time'].median(),
        'max_queue_time': df['queue_time'].max(),
        'std_queue_time': df['queue_time'].std(),
        'avg_total_time': df['total_time_in_system'].mean(),
        'avg_service_time': df['service_duration'].mean(),
        'utilization': utilization,
        'long_wait_pct': long_wait_pct
    }
    
    return metrics

def create_histogram(df_A, df_B, scenario_A_name, scenario_B_name):
    """Buat histogram perbandingan waktu tunggu"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram Skenario A
    axes[0].hist(df_A['queue_time'], bins=25, color='#FF6B6B', alpha=0.7, edgecolor='black')
    axes[0].axvline(df_A['queue_time'].mean(), color='red', linestyle='--', linewidth=2, 
                    label=f"Mean = {df_A['queue_time'].mean():.2f} menit")
    axes[0].set_xlabel('Waktu Tunggu (menit)', fontsize=11)
    axes[0].set_ylabel('Frekuensi', fontsize=11)
    axes[0].set_title(f'{scenario_A_name}\nDistribusi Waktu Tunggu', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Histogram Skenario B
    axes[1].hist(df_B['queue_time'], bins=25, color='#4ECDC4', alpha=0.7, edgecolor='black')
    axes[1].axvline(df_B['queue_time'].mean(), color='red', linestyle='--', linewidth=2, 
                    label=f"Mean = {df_B['queue_time'].mean():.2f} menit")
    axes[1].set_xlabel('Waktu Tunggu (menit)', fontsize=11)
    axes[1].set_ylabel('Frekuensi', fontsize=11)
    axes[1].set_title(f'{scenario_B_name}\nDistribusi Waktu Tunggu', fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_boxplot(df_combined):
    """Buat box plot perbandingan"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    sns.boxplot(x='Skenario', y='queue_time', data=df_combined, 
                palette=['#FF6B6B', '#4ECDC4'], ax=axes[0])
    axes[0].set_ylabel('Waktu Tunggu (menit)', fontsize=11)
    axes[0].set_title('Perbandingan Waktu Tunggu', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')
    
    sns.boxplot(x='Skenario', y='total_time_in_system', data=df_combined, 
                palette=['#FF6B6B', '#4ECDC4'], ax=axes[1])
    axes[1].set_ylabel('Total Waktu di Sistem (menit)', fontsize=11)
    axes[1].set_title('Perbandingan Total Waktu', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig

def create_line_chart(queue_A, queue_B, warm_up_period, plot_duration):
    """Buat line chart panjang antrian"""
    fig, ax = plt.subplots(figsize=(12, 5))
    
    queue_A_plot = queue_A[queue_A['time'] <= warm_up_period + plot_duration]
    queue_B_plot = queue_B[queue_B['time'] <= warm_up_period + plot_duration]
    
    ax.plot(queue_A_plot['time'], queue_A_plot['queue_length'], 
            color='#FF6B6B', alpha=0.7, linewidth=1.5, label='Skenario A')
    ax.plot(queue_B_plot['time'], queue_B_plot['queue_length'], 
            color='#4ECDC4', alpha=0.7, linewidth=1.5, label='Skenario B')
    
    ax.set_xlabel('Waktu Simulasi (menit)', fontsize=11)
    ax.set_ylabel('Panjang Antrian (mobil)', fontsize=11)
    ax.set_title(f'Panjang Antrian Seiring Waktu\n({plot_duration} menit setelah warm-up)', 
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

# ============================================================================
# APLIKASI STREAMLIT
# ============================================================================

def main():
    # Header
    st.markdown('<p class="main-header">🚗 Simulasi Antrian Drive-Thru Restaurant</p>', 
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">TA-14 Praktikum Pemodelan dan Simulasi</p>', 
                unsafe_allow_html=True)
    
    # Sidebar untuk konfigurasi
    st.sidebar.header("⚙️ Konfigurasi Simulasi")
    
    # Parameter simulasi
    st.sidebar.subheader("Parameter Kedatangan")
    inter_arrival = st.sidebar.slider(
        "Rata-rata Waktu Antar Kedatangan (menit)",
        min_value=2.0, max_value=10.0, value=5.0, step=0.5,
        help="Mean dari distribusi eksponensial untuk kedatangan mobil"
    )
    
    st.sidebar.subheader("Parameter Layanan")
    service_min = st.sidebar.slider(
        "Waktu Layanan Minimum (menit)",
        min_value=1.0, max_value=5.0, value=3.0, step=0.5
    )
    service_max = st.sidebar.slider(
        "Waktu Layanan Maksimum (menit)",
        min_value=5.0, max_value=15.0, value=7.0, step=0.5
    )
    
    st.sidebar.subheader("Parameter Simulasi")
    sim_time = st.sidebar.slider(
        "Total Waktu Simulasi (menit)",
        min_value=500, max_value=2000, value=1100, step=100,
        help="Termasuk warm-up period"
    )
    warm_up = st.sidebar.slider(
        "Warm-up Period (menit)",
        min_value=50, max_value=200, value=100, step=25,
        help="Data pada periode ini akan dibuang"
    )
    
    st.sidebar.subheader("Skenario Perbandingan")
    num_counters_A = st.sidebar.number_input(
        "Jumlah Loket Skenario A",
        min_value=1, max_value=5, value=1, step=1
    )
    num_counters_B = st.sidebar.number_input(
        "Jumlah Loket Skenario B",
        min_value=1, max_value=5, value=2, step=1
    )
    
    # Random seed
    random_seed = st.sidebar.number_input(
        "Random Seed (untuk reproducibility)",
        min_value=1, max_value=999, value=42, step=1
    )
    
    # Tombol run simulasi
    run_button = st.sidebar.button("🚀 Jalankan Simulasi", type="primary", use_container_width=True)
    
    # Tabs untuk organisasi konten
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Info & Parameter", 
        "📊 Hasil Simulasi", 
        "📈 Visualisasi", 
        "💡 Kesimpulan"
    ])
    
    with tab1:
        st.header("Identifikasi Topik")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Studi Kasus")
            st.info("""
            **Antrean Mobil pada Layanan Drive-Thru Restoran Cepat Saji**
            
            **Alur Proses:**
            Mobil datang → Memesan → Membayar → Mengambil makanan → Pergi
            """)
            
            st.subheader("Parameter yang Digunakan")
            st.write(f"- **Pola Kedatangan:** Eksponensial (λ = {inter_arrival} menit)")
            st.write(f"- **Waktu Layanan:** Uniform ({service_min}-{service_max} menit)")
            st.write(f"- **Waktu Simulasi:** {sim_time} menit")
            st.write(f"- **Warm-up Period:** {warm_up} menit")
        
        with col2:
            st.subheader("Formulir Desain Simulasi")
            
            design_data = {
                "Komponen": [
                    "Entitas (Yang Antre)",
                    "Resource (Yang Melayani)",
                    "Kapasitas Resource",
                    "Pola Kedatangan",
                    "Waktu Layanan"
                ],
                "Spesifikasi": [
                    "Mobil",
                    "Loket Drive-Thru",
                    f"Skenario A: {num_counters_A} loket, Skenario B: {num_counters_B} loket",
                    f"Rata-rata {inter_arrival} menit (Eksponensial)",
                    f"{service_min}-{service_max} menit (Uniform)"
                ]
            }
            
            df_design = pd.DataFrame(design_data)
            st.table(df_design)
    
    # Jalankan simulasi saat button ditekan
    if run_button:
        analysis_time = sim_time - warm_up
        
        with st.spinner('🔄 Menjalankan simulasi... Mohon tunggu...'):
            # Set random seed
            np.random.seed(random_seed)
            
            # SIMULASI SKENARIO A
            env_A = simpy.Environment()
            sim_A = DriveThruSimulation(
                env_A, num_counters_A, warm_up, 
                inter_arrival, service_min, service_max
            )
            df_A = sim_A.run_simulation(sim_time)
            metrics_A = calculate_metrics(df_A, num_counters_A, analysis_time)
            
            # Reset seed untuk fair comparison
            np.random.seed(random_seed)
            
            # SIMULASI SKENARIO B
            env_B = simpy.Environment()
            sim_B = DriveThruSimulation(
                env_B, num_counters_B, warm_up, 
                inter_arrival, service_min, service_max
            )
            df_B = sim_B.run_simulation(sim_time)
            metrics_B = calculate_metrics(df_B, num_counters_B, analysis_time)
        
        st.success('✅ Simulasi selesai!')
        
        # Simpan hasil ke session state
        st.session_state['df_A'] = df_A
        st.session_state['df_B'] = df_B
        st.session_state['metrics_A'] = metrics_A
        st.session_state['metrics_B'] = metrics_B
        st.session_state['sim_A'] = sim_A
        st.session_state['sim_B'] = sim_B
        st.session_state['scenario_names'] = {
            'A': f"Skenario A ({num_counters_A} Loket)",
            'B': f"Skenario B ({num_counters_B} Loket)"
        }
        st.session_state['params'] = {
            'warm_up': warm_up,
            'analysis_time': analysis_time,
            'num_counters_A': num_counters_A,
            'num_counters_B': num_counters_B
        }
    
    # Tampilkan hasil jika sudah ada di session state
    if 'df_A' in st.session_state and 'df_B' in st.session_state:
        df_A = st.session_state['df_A']
        df_B = st.session_state['df_B']
        metrics_A = st.session_state['metrics_A']
        metrics_B = st.session_state['metrics_B']
        sim_A = st.session_state['sim_A']
        sim_B = st.session_state['sim_B']
        scenario_names = st.session_state['scenario_names']
        params = st.session_state['params']
        
        with tab2:
            st.header("📊 Hasil Simulasi")
            
            # Metrics cards
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"🔴 {scenario_names['A']}")
                
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                metric_col1.metric("Total Mobil", f"{metrics_A['total_customers']}")
                metric_col2.metric("Rata-rata Tunggu", f"{metrics_A['avg_queue_time']:.2f} min")
                metric_col3.metric("Utilization", f"{metrics_A['utilization']:.1f}%")
                
                st.markdown("**Statistik Detail:**")
                stats_A = pd.DataFrame({
                    'Metrik': [
                        'Rata-rata Waktu Tunggu',
                        'Median Waktu Tunggu',
                        'Max Waktu Tunggu',
                        'Std Dev Waktu Tunggu',
                        'Rata-rata Total Waktu',
                        'Mobil Tunggu > 10 menit'
                    ],
                    'Nilai': [
                        f"{metrics_A['avg_queue_time']:.2f} menit",
                        f"{metrics_A['median_queue_time']:.2f} menit",
                        f"{metrics_A['max_queue_time']:.2f} menit",
                        f"{metrics_A['std_queue_time']:.2f} menit",
                        f"{metrics_A['avg_total_time']:.2f} menit",
                        f"{metrics_A['long_wait_pct']:.1f}%"
                    ]
                })
                st.dataframe(stats_A, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader(f"🔵 {scenario_names['B']}")
                
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                metric_col1.metric("Total Mobil", f"{metrics_B['total_customers']}")
                metric_col2.metric("Rata-rata Tunggu", f"{metrics_B['avg_queue_time']:.2f} min")
                metric_col3.metric("Utilization", f"{metrics_B['utilization']:.1f}%")
                
                st.markdown("**Statistik Detail:**")
                stats_B = pd.DataFrame({
                    'Metrik': [
                        'Rata-rata Waktu Tunggu',
                        'Median Waktu Tunggu',
                        'Max Waktu Tunggu',
                        'Std Dev Waktu Tunggu',
                        'Rata-rata Total Waktu',
                        'Mobil Tunggu > 10 menit'
                    ],
                    'Nilai': [
                        f"{metrics_B['avg_queue_time']:.2f} menit",
                        f"{metrics_B['median_queue_time']:.2f} menit",
                        f"{metrics_B['max_queue_time']:.2f} menit",
                        f"{metrics_B['std_queue_time']:.2f} menit",
                        f"{metrics_B['avg_total_time']:.2f} menit",
                        f"{metrics_B['long_wait_pct']:.1f}%"
                    ]
                })
                st.dataframe(stats_B, use_container_width=True, hide_index=True)
            
            # Tabel perbandingan
            st.subheader("📋 Tabel Perbandingan")
            
            improvement_wait = ((metrics_A['avg_queue_time'] - metrics_B['avg_queue_time']) / 
                               metrics_A['avg_queue_time']) * 100
            improvement_long = ((metrics_A['long_wait_pct'] - metrics_B['long_wait_pct']) / 
                               max(metrics_A['long_wait_pct'], 0.01)) * 100
            
            comparison_df = pd.DataFrame({
                'Metrik': [
                    'Rata-rata Waktu Tunggu',
                    'Max Waktu Tunggu',
                    'Utilization Rate',
                    'Mobil Tunggu > 10 menit'
                ],
                scenario_names['A']: [
                    f"{metrics_A['avg_queue_time']:.2f} menit",
                    f"{metrics_A['max_queue_time']:.2f} menit",
                    f"{metrics_A['utilization']:.1f}%",
                    f"{metrics_A['long_wait_pct']:.1f}%"
                ],
                scenario_names['B']: [
                    f"{metrics_B['avg_queue_time']:.2f} menit",
                    f"{metrics_B['max_queue_time']:.2f} menit",
                    f"{metrics_B['utilization']:.1f}%",
                    f"{metrics_B['long_wait_pct']:.1f}%"
                ],
                'Improvement': [
                    f"{improvement_wait:+.1f}%",
                    f"{((metrics_A['max_queue_time'] - metrics_B['max_queue_time']) / metrics_A['max_queue_time']) * 100:+.1f}%",
                    f"{((metrics_A['utilization'] - metrics_B['utilization']) / metrics_A['utilization']) * 100:+.1f}%",
                    f"{improvement_long:+.1f}%"
                ]
            })
            
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        with tab3:
            st.header("📈 Visualisasi Hasil")
            
            # Histogram
            st.subheader("1. Histogram Waktu Tunggu")
            fig_hist = create_histogram(df_A, df_B, scenario_names['A'], scenario_names['B'])
            st.pyplot(fig_hist)
            st.caption("Histogram menunjukkan distribusi waktu tunggu pelanggan. "
                      "Skenario dengan distribusi lebih ke kiri menunjukkan performa lebih baik.")
            
            st.divider()
            
            # Box Plot
            st.subheader("2. Box Plot Perbandingan")
            df_A_copy = df_A.copy()
            df_B_copy = df_B.copy()
            df_A_copy['Skenario'] = scenario_names['A']
            df_B_copy['Skenario'] = scenario_names['B']
            df_combined = pd.concat([df_A_copy, df_B_copy])
            
            fig_box = create_boxplot(df_combined)
            st.pyplot(fig_box)
            st.caption("Box plot menampilkan median, kuartil, dan outliers. "
                      "Box yang lebih rendah = performa lebih baik.")
            
            st.divider()
            
            # Line Chart
            st.subheader("3. Panjang Antrian Seiring Waktu")
            
            queue_A = pd.DataFrame(sim_A.queue_length, columns=['time', 'queue_length'])
            queue_B = pd.DataFrame(sim_B.queue_length, columns=['time', 'queue_length'])
            queue_A = queue_A[queue_A['time'] >= params['warm_up']]
            queue_B = queue_B[queue_B['time'] >= params['warm_up']]
            
            plot_duration = st.slider("Durasi yang ditampilkan (menit)", 
                                     min_value=100, max_value=500, value=200, step=50)
            
            fig_line = create_line_chart(queue_A, queue_B, params['warm_up'], plot_duration)
            st.pyplot(fig_line)
            st.caption("Line chart menunjukkan fluktuasi panjang antrian. "
                      "Garis yang lebih rendah = antrian lebih pendek = performa lebih baik.")
        
        with tab4:
            st.header("💡 Kesimpulan dan Rekomendasi")
            
            # Temuan utama
            st.subheader("🎯 Temuan Utama")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="Pengurangan Waktu Tunggu",
                    value=f"{improvement_wait:.1f}%",
                    delta=f"{metrics_A['avg_queue_time'] - metrics_B['avg_queue_time']:.2f} menit lebih cepat",
                    delta_color="normal"
                )
            
            with col2:
                st.metric(
                    label="Pengurangan Mobil Tunggu Lama",
                    value=f"{improvement_long:.1f}%",
                    delta=f"{metrics_A['long_wait_pct'] - metrics_B['long_wait_pct']:.1f}% lebih sedikit",
                    delta_color="normal"
                )
            
            # Analisis
            st.subheader("📊 Analisis Cost-Benefit")
            
            benefits_col, costs_col = st.columns(2)
            
            with benefits_col:
                st.success("**✅ Keuntungan Penambahan Loket:**")
                st.write(f"- Waktu tunggu berkurang **{improvement_wait:.1f}%**")
                st.write(f"- Pelanggan dengan tunggu > 10 menit turun dari **{metrics_A['long_wait_pct']:.1f}%** ke **{metrics_B['long_wait_pct']:.1f}%**")
                st.write("- Kepuasan pelanggan meningkat")
                st.write("- Throughput sistem lebih stabil")
                st.write("- Mengurangi risiko customer churn")
            
            with costs_col:
                st.warning("**💰 Biaya yang Perlu Dipertimbangkan:**")
                st.write("- Biaya investasi loket tambahan")
                st.write("- Biaya operasional (gaji karyawan)")
                st.write("- Biaya maintenance")
                st.write(f"- Utilization turun dari **{metrics_A['utilization']:.1f}%** ke **{metrics_B['utilization']:.1f}%**")
                st.write("- Ada idle time pada loket")
            
            # Rekomendasi
            st.subheader("📋 Rekomendasi")
            
            if improvement_wait > 50 and metrics_A['long_wait_pct'] > 20:
                st.success("""
                **✅ SANGAT DIREKOMENDASIKAN** untuk menambah loket!
                
                **Alasan:**
                - Improvement waktu tunggu sangat signifikan
                - Banyak pelanggan mengalami tunggu lama di kondisi baseline
                - ROI kemungkinan positif karena peningkatan kepuasan dan pengurangan customer churn
                - Kapasitas tambahan memungkinkan melayani lebih banyak pelanggan di jam sibuk
                """)
            elif improvement_wait > 30:
                st.info("""
                **💡 DIREKOMENDASIKAN** dengan pertimbangan bisnis.
                
                **Saran:**
                - Implementasikan sistem loket dinamis (1-2 loket tergantung jam)
                - 1 loket saat sepi (pagi/sore hari)
                - 2 loket saat jam sibuk (lunch time, dinner time)
                - Monitor pola kedatangan untuk optimasi jadwal
                """)
            else:
                st.warning("""
                **⚠️ PERTIMBANGKAN ALTERNATIF** lainnya.
                
                **Saran:**
                - Optimasi proses layanan untuk mengurangi service time
                - Training karyawan untuk meningkatkan kecepatan
                - Sistem pre-order untuk mengurangi waktu di loket
                - Analisis lebih lanjut tentang peak hours
                """)
            
            # Download hasil
            st.divider()
            st.subheader("📥 Download Hasil Simulasi")
            
            col1, col2 = st.columns(2)
            
            with col1:
                csv_A = df_A.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📄 Download Data {scenario_names['A']}",
                    data=csv_A,
                    file_name=f"simulasi_scenario_A_{params['num_counters_A']}_loket.csv",
                    mime="text/csv"
                )
            
            with col2:
                csv_B = df_B.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📄 Download Data {scenario_names['B']}",
                    data=csv_B,
                    file_name=f"simulasi_scenario_B_{params['num_counters_B']}_loket.csv",
                    mime="text/csv"
                )
    
    else:
        # Instruksi jika belum run
        with tab2:
            st.info("👈 Silakan atur parameter di sidebar dan klik **Jalankan Simulasi** untuk melihat hasil.")
        with tab3:
            st.info("👈 Silakan atur parameter di sidebar dan klik **Jalankan Simulasi** untuk melihat visualisasi.")
        with tab4:
            st.info("👈 Silakan atur parameter di sidebar dan klik **Jalankan Simulasi** untuk melihat kesimpulan.")
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #888; padding: 2rem 0;'>
            <p><strong>TA-14: Simulasi Drive-Thru Restaurant</strong></p>
            <p>Praktikum Pemodelan dan Simulasi | Powered by SimPy & Streamlit</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
