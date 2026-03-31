import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

# ตั้งค่า Thai font สำหรับแสดงภาษาไทย
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial']

def visualize_weather_data(csv_file="data/weather_data.csv"):
    """
    แสดงผลข้อมูลสภาพอากาศเป็นกราฟ Pie Chart และ Donut Chart
    """
    
    try:
        # โหลดข้อมูล
        df = pd.read_csv(csv_file)
        logger.info(f"โหลดข้อมูลจากไฟล์ {csv_file}")
        
        # เลือกเฉพาะ Top 25 อุณหภูมิสูง + 5 อุณหภูมิต่ำสุด
        top_temps = df.nlargest(25, 'temperature')
        bottom_temps = df.nsmallest(5, 'temperature')
        df_display = pd.concat([top_temps, bottom_temps]).drop_duplicates().reset_index(drop=True)
        
        # เรียงลำดับจากสูงสุดไปต่ำสุด
        df_display = df_display.sort_values('temperature', ascending=False).reset_index(drop=True)
        
        # สร้าง figure
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        fig.suptitle('Thailand Weather Data Analysis (Central Region)', fontsize=22, fontweight='bold', y=0.98)
        
        # ========== Pie Chart 1: อุณหภูมิที่จัดกลุ่ม ==========
        ax1 = fig.add_subplot(gs[0, 0])

        # จัดกลุ่มอุณหภูมิ
        hot = len(df[df['temperature'] > 28])
        warm = len(df[(df['temperature'] >= 25) & (df['temperature'] <= 28)])
        cool = len(df[df['temperature'] < 25])

        sizes = [hot, warm, cool]
        labels = [f'Hot (>28°C)', f'Warm (25-28°C)', f'Cool (<25°C)']
        colors = ['#FF4444', '#FFA500', '#4488FF']
        explode = (0.15, 0.1, 0.1)

        # Pie chart โดยไม่แสดง labels รอบๆวงกลม
        wedges, texts, autotexts = ax1.pie(sizes, colors=colors, autopct='%1.1f%%',
                startangle=90, explode=explode, textprops={'fontsize': 11, 'fontweight': 'bold', 'color': 'white'},
                pctdistance=0.85)

        # ปรับตำแหน่งเปอร์เซ็นต์
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')

        # เพิ่มกล่องข้อมูลรายละเอียดด้านบนอักษร
        legend_text = '\n'.join([f'{labels[i]}: {sizes[i]} cities' for i in range(len(labels))])
        ax1.text(0.5, -0.15, legend_text, transform=ax1.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8, pad=0.8),
                ha='center', fontweight='bold')

        ax1.set_title('Temperature Distribution', fontsize=13, fontweight='bold', pad=15)
        
        # ========== Bar Chart: City Temperature Percentage ==========
        ax2 = fig.add_subplot(gs[0, 1])

        # คำนวณเปอร์เซ็นต์อุณหภูมิเทียบกับอุณหภูมิสูงสุด
        df_sorted = df.sort_values('temperature', ascending=False)
        max_temp = df_sorted['temperature'].max()
        df_sorted['temp_pct'] = (df_sorted['temperature'] / max_temp * 100).round(1)

        # เลือกเฉพาะ top 12
        df_top = df_sorted.head(12)

        # สีตามอุณหภูมิ
        colors_bar = ['#FF1111' if t > 28 else '#FF9900' if t >= 25 else '#4488FF'
                      for t in df_top['temperature'].values]

        # สร้าง horizontal bar chart
        bars = ax2.barh(range(len(df_top)), df_top['temp_pct'].values, color=colors_bar, edgecolor='black', linewidth=0.5)

        # ตั้ง labels
        ax2.set_yticks(range(len(df_top)))
        ax2.set_yticklabels([f"{city} ({temp:.1f}°C)" for city, temp in
                             zip(df_top['city'].values, df_top['temperature'].values)], fontsize=9, fontweight='bold')

        # เพิ่มค่าเปอร์เซ็นต์บนบาร์
        for i, (bar, val) in enumerate(zip(bars, df_top['temp_pct'].values)):
            ax2.text(val + 1, i, f'{val:.1f}%', va='center', fontsize=9, fontweight='bold')

        ax2.set_xlabel('Temperature %', fontsize=11, fontweight='bold')
        ax2.set_xlim(0, 110)
        ax2.set_title('Top Cities by Temperature (%)', fontsize=13, fontweight='bold', pad=15)
        ax2.invert_yaxis()
        ax2.grid(axis='x', linestyle='--', alpha=0.3)
        
        # ========== Pie Chart 2: ความชื้น ==========
        ax3 = fig.add_subplot(gs[1, 0])

        # จัดกลุ่มความชื้น
        very_humid = len(df[df['humidity'] > 80])
        humid = len(df[(df['humidity'] >= 60) & (df['humidity'] <= 80)])
        dry = len(df[df['humidity'] < 60])

        sizes_humidity = [very_humid, humid, dry]
        labels_humidity = ['Very Humid (>80%)', 'Humid (60-80%)', 'Dry (<60%)']
        colors_humidity = ['#2E7D9E', '#5BA3C9', '#87CEEB']
        explode_humidity = (0.1, 0.05, 0.05)

        # Pie chart โดยไม่แสดง labels รอบๆวงกลม
        ax3.pie(sizes_humidity, colors=colors_humidity,
                autopct='%1.1f%%', startangle=90, explode=explode_humidity,
                textprops={'fontsize': 11, 'fontweight': 'bold', 'color': 'white'})

        # เพิ่มกล่องข้อมูลรายละเอียดด้านล่าง
        humidity_text = '\n'.join([f'{labels_humidity[i]}: {sizes_humidity[i]} cities'
                                  for i in range(len(labels_humidity))])
        ax3.text(0.5, -0.15, humidity_text, transform=ax3.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8, pad=0.8),
                ha='center', fontweight='bold')

        ax3.set_title('Humidity Distribution', fontsize=13, fontweight='bold', pad=15)
        
        # ========== สถิติทั่วไป ==========
        ax4 = fig.add_subplot(gs[1, 1])  # Position below Top Cities bar chart
        ax4.axis('off')

        stats_text = f"""Total Cities: {len(df)}  |  Temperature: Max {df['temperature'].max():.2f}°C | Min {df['temperature'].min():.2f}°C | Avg {df['temperature'].mean():.2f}°C
Humidity: Max {df['humidity'].max()}% | Min {df['humidity'].min()}%  | Avg {df['humidity'].mean():.1f}%  |  Hottest: {df.loc[df['temperature'].idxmax(), 'city']} ({df['temperature'].max():.1f}°C)
Coolest: {df.loc[df['temperature'].idxmin(), 'city']} ({df['temperature'].min():.1f}°C)  |  Most Humid: {df.loc[df['humidity'].idxmax(), 'city']} ({df['humidity'].max()}%)"""

        ax4.text(0.5, 0.5, stats_text, fontsize=10,
                verticalalignment='center', horizontalalignment='center',
                transform=ax4.transAxes,
                bbox=dict(boxstyle='round,pad=1.2', facecolor='lightyellow',
                         edgecolor='orange', alpha=0.9, linewidth=2.5))

        # ปรับระยะห่าง
        plt.subplots_adjust(hspace=0.3, wspace=0.3)
        
        # บันทึกเป็นไฟล์
        output_file = "weather_analysis.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        logger.info(f"✅ บันทึกกราฟเสร็จ: {output_file}")
        
        # แสดงบนหน้าจอ
        plt.show()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error ในการแสดงผล: {e}")
        return False

if __name__ == "__main__":
    visualize_weather_data()
