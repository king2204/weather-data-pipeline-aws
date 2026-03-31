import logging
from extract import extract_weather_data
from transform import transform_weather_data
from load import load_to_s3, load_to_local_csv
from visualize import visualize_weather_data

# ตั้งค่า Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_weather_etl_pipeline(cities=None, use_s3=False):
    """
    รัน ETL Pipeline สำหรับข้อมูลสภาพอากาศ

    Args:
        cities: List ของชื่อเมือง (default เป็น Bangkok)
        use_s3: True เพื่ออัปโหลดไป AWS S3, False เพื่อบันทึกลง CSV
    """

    if cities is None:
        cities = ["Bangkok"]

    logger.info("=" * 50)
    logger.info("🚀 เริ่มต้น Weather ETL Pipeline")
    logger.info("=" * 50)

    all_data = []

    for city in cities:
        logger.info(f"\n📍 ประมวลผลเมือง: {city}")

        # Extract
        logger.info(f"1️⃣ Extract: ดึงข้อมูล {city}")
        df_raw = extract_weather_data(city)

        if df_raw is None:
            logger.error(f"❌ ไม่สามารถดึงข้อมูล {city}")
            continue

        # Transform
        logger.info(f"2️⃣ Transform: ล้างข้อมูล {city}")
        df_clean = transform_weather_data(df_raw)

        if df_clean is None:
            logger.error(f"❌ ไม่สามารถล้างข้อมูล {city}")
            continue

        all_data.append(df_clean)

    if not all_data:
        logger.error("❌ ไม่มีข้อมูลที่ประมวลผลสำเร็จ")
        return False

    # รวมข้อมูลทั้งหมด
    import pandas as pd
    df_final = pd.concat(all_data, ignore_index=True)

    logger.info(f"\n3️⃣ Load: บันทึกข้อมูล ({len(df_final)} แถว)")

    if use_s3:
        logger.info("📤 ส่งข้อมูลไป AWS S3...")
        success = load_to_s3(df_final)
    else:
        logger.info("💾 บันทึกลงไฟล์ CSV ในเครื่อง...")
        success = load_to_local_csv(df_final)

    if success:
        logger.info("\n" + "=" * 50)
        logger.info("✅ ETL Pipeline สำเร็จ!")
        logger.info("=" * 50)
        print("\n📊 ข้อมูลที่ประมวลผล:")
        print(df_final)

        # 🎨 แสดงผลเป็นกราฟ
        visualize_weather_data()

        return True
    else:
        logger.error("❌ ETL Pipeline ล้มเหลว")
        return False

if __name__ == "__main__":
    # เฉพาะเมือง ภาคกลาง
    central_cities = [
        "Bangkok", "Nakhon Pathom", "Samut Sakhon", "Samut Prakan",
        "Ang Thong", "Ayutthaya", "Chachoengsao", "Chai Nat",
        "Chon Buri", "Lopburi", "Nakhon Nayok", "Saraburi",
        "Sing Buri", "Samut Songkhram"
    ]
    
    # รันเฉพาะเมืองภาคกลาง
    run_weather_etl_pipeline(cities=central_cities, use_s3=False)

    # หรือส่งไป AWS S3:
    # run_weather_etl_pipeline(cities=central_cities, use_s3=True)
