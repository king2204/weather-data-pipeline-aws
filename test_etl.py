import os
import json
import requests
import boto3
from datetime import datetime
from dotenv import load_dotenv

# 1. โหลดค่าตัวแปรจากไฟล์ .env
load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

city = "Bangkok"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

try:
    # 2. ดึงข้อมูลสภาพอากาศจาก API
    print(f"⏳ กำลังดึงข้อมูลสภาพอากาศของเมือง {city}...")
    response = requests.get(url)
    data = response.json()
    
    # 3. สร้างชื่อไฟล์ (ใส่คำว่า local ลงไปให้รู้ว่ารันจากเครื่องเรา)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"raw_data/weather_{city}_local_{timestamp}.json"
    
    # 4. เอาเข้าสู่ระบบ AWS S3
    print("⏳ กำลังเชื่อมต่อ AWS S3...")
    s3 = boto3.client(
        's3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file_name,
        Body=json.dumps(data),
        ContentType='application/json'
    )
    
    print(f"✅ สำเร็จ! อัปโหลดไฟล์ {file_name} ขึ้น S3 เรียบร้อยแล้ว")

except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")