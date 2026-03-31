import os
import requests
import pandas as pd
from dotenv import load_dotenv
import logging

# ตั้งค่า Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_weather_data(city="Bangkok"):
    """ดึงข้อมูลสภาพอากาศจาก OpenWeatherMap API"""

    # โหลด API Key ลับของเราจากไฟล์ .env
    load_dotenv()
    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        logger.error("❌ ไม่พบ API Key ในไฟล์ .env")
        return None

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        logger.info(f"🌍 กำลังดึงข้อมูลของเมือง: {city}...")
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ ดึงข้อมูลสำเร็จ!")

            # ตรวจสอบว่าข้อมูลที่จำเป็นมีอยู่
            if not data.get('main') or not data.get('weather'):
                logger.error("❌ ข้อมูล API ไม่สมบูรณ์ (ขาด 'main' หรือ 'weather')")
                return None

            # แปลงข้อมูลเป็น DataFrame
            weather_dict = {
                "city": [data.get('name', 'Unknown')],
                "temperature": [data['main'].get('temp')],
                "humidity": [data['main'].get('humidity')],
                "description": [data['weather'][0].get('description', 'N/A')],
                "timestamp": [pd.Timestamp.now()]
            }

            df = pd.DataFrame(weather_dict)
            logger.info("📊 แปลงข้อมูลเป็น DataFrame สำเร็จ")

            return df
        else:
            logger.error(f"❌ API Error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        logger.error("❌ API Request Timeout (>10 วินาที)")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network Error: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    df = extract_weather_data("Bangkok")
    if df is not None:
        print("\n📊 ข้อมูลที่ดึงมา:")
        print(df)