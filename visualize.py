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
        labels = [f'Hot\n(>28°C)\n{hot} cities', 
                  f'Warm\n(25-28°C)\n{warm} cities', 
                  f'Cool\n(<25°C)\n{cool} cities']
        colors = ['#FF4444', '#FFA500', '#4488FF']
        explode = (0.1, 0.05, 0.05)
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                startangle=90, explode=explode, textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax1.set_title('Temperature Distribution', fontsize=13, fontweight='bold', pad=15)
        
        # ========== Donut Chart: จังหวัดและอุณหภูมิ ==========
        ax2 = fig.add_subplot(gs[0, 1])

        temps = df_display['temperature'].values
        city_labels = [f"{city[:3].upper()}\n{t:.1f}°" for city, t in zip(df_display['city'], temps)]

        # สีตามอุณหภูมิ
        colors_temp = ['#FF1111' if t > 28 else '#FF9900' if t >= 25 else '#4488FF' for t in temps]

        # ใช้ pct_distance เพื่อให้ autolabels อยู่นอกวงกลม
        wedges, texts, autotexts = ax2.pie(temps, labels=None, autopct='',
                                            colors=colors_temp, startangle=90,
                                            textprops={'fontsize': 8, 'fontweight': 'bold'})

        # เพิ่มวงกลมตรงกลางให้เป็น Donut
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax2.add_artist(centre_circle)

        # สร้างคำอธิบายด้านบน
        legend_text = ", ".join([f"{city[:3].upper()} {t:.1f}°"
                                 for city, t in zip(df_display['city'], temps)])
        ax2.text(0.5, -1.35, legend_text, transform=ax2.transAxes,
                fontsize=8, ha='center', wrap=True,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        ax2.set_title('Temperature by City (Donut Chart)', fontsize=13, fontweight='bold', pad=15)
        
        # ========== Pie Chart 2: ความชื้น ==========
        ax3 = fig.add_subplot(gs[1, 0])
        
        # จัดกลุ่มความชื้น
        very_humid = len(df[df['humidity'] > 80])
        humid = len(df[(df['humidity'] >= 60) & (df['humidity'] <= 80)])
        dry = len(df[df['humidity'] < 60])
        
        sizes_humidity = [very_humid, humid, dry]
        labels_humidity = [f'Very Humid\n(>80%)\n{very_humid} cities', 
                          f'Humid\n(60-80%)\n{humid} cities', 
                          f'Dry\n(<60%)\n{dry} cities']
        colors_humidity = ['#2E7D9E', '#5BA3C9', '#87CEEB']
        explode_humidity = (0.1, 0.05, 0.05)
        
        ax3.pie(sizes_humidity, labels=labels_humidity, colors=colors_humidity, 
                autopct='%1.1f%%', startangle=90, explode=explode_humidity,
                textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax3.set_title('Humidity Distribution', fontsize=13, fontweight='bold', pad=15)
        
        # ========== สถิติทั่วไป ==========
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('off')
        
        stats_text = f"""
        WEATHER STATISTICS
        
        Total Cities: {len(df)}
        
        Temperature:
          Max: {df['temperature'].max():.2f}°C
          Min: {df['temperature'].min():.2f}°C
          Avg: {df['temperature'].mean():.2f}°C
        
        Humidity:
          Max: {df['humidity'].max()}%
          Min: {df['humidity'].min()}%
          Avg: {df['humidity'].mean():.1f}%
        
        🔴 Hottest:
          {df.loc[df['temperature'].idxmax(), 'city']}
          ({df['temperature'].max():.1f}°C)
        
        🔵 Coolest:
          {df.loc[df['temperature'].idxmin(), 'city']}
          ({df['temperature'].min():.1f}°C)
        
        💧 Most Humid:
          {df.loc[df['humidity'].idxmax(), 'city']}
          ({df['humidity'].max()}%)
        """
        
        ax4.text(0.05, 0.5, stats_text, fontsize=12, family='monospace',
                verticalalignment='center', bbox=dict(boxstyle='round', 
                facecolor='lightyellow', alpha=0.8, pad=1.5))
        
        # ปรับระยะห่าง
        plt.tight_layout()
        
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
