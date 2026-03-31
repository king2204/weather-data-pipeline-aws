import pandas as pd
import logging

logger = logging.getLogger(__name__)

def transform_weather_data(df):
    """ล้างและตรวจสอบข้อมูลสภาพอากาศ"""

    if df is None or df.empty:
        logger.warning("⚠️ ข้อมูล DataFrame ว่าง")
        return None

    try:
        # Copy DataFrame เพื่อไม่ให้แก้ original
        df_clean = df.copy()

        # ตรวจสอบข้อมูลว่างเปล่า
        if df_clean.isnull().any().any():
            logger.warning(f"⚠️ พบข้อมูลว่างเปล่า:\n{df_clean.isnull().sum()}")
            df_clean = df_clean.dropna()

        # ล้างข้อมูล - ลบช่องว่างด้านหน้า-หลัง (สำหรับ string columns)
        if df_clean['city'].dtype == 'object':
            df_clean['city'] = df_clean['city'].str.strip()
        if df_clean['description'].dtype == 'object':
            df_clean['description'] = df_clean['description'].str.strip()

        # แปลงอุณหภูมิให้เป็นทศนิยม 2 ตำแหน่ง
        df_clean['temperature'] = df_clean['temperature'].round(2)
        df_clean['humidity'] = df_clean['humidity'].astype(int)

        # ตรวจสอบค่าความสมควร
        if (df_clean['temperature'] < -273.15).any():
            logger.warning("⚠️ พบอุณหภูมิที่ไม่สมเหตุสมผล (ต่ำกว่า Absolute Zero)")
            df_clean = df_clean[df_clean['temperature'] >= -273.15]

        if (df_clean['humidity'] < 0).any() or (df_clean['humidity'] > 100).any():
            logger.warning("⚠️ พบความชื้นที่ไม่สมเหตุสมผล (นอกช่วง 0-100)")
            df_clean = df_clean[(df_clean['humidity'] >= 0) & (df_clean['humidity'] <= 100)]

        logger.info(f"✅ ล้างข้อมูลเสร็จ! (จำนวน {len(df_clean)} แถว)")
        return df_clean

    except Exception as e:
        logger.error(f"❌ Error ในการล้างข้อมูล: {e}")
        return None

if __name__ == "__main__":
    # ตัวอย่าง (ใช้ extract.py ก่อน)
    from extract import extract_weather_data

    df = extract_weather_data("Bangkok")
    df_clean = transform_weather_data(df)
    if df_clean is not None:
        print("\n✨ ข้อมูลหลังล้าง:")
        print(df_clean)
        print(f"\nData Types:\n{df_clean.dtypes}")
