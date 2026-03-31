import os
import pandas as pd
import logging
import boto3
from dotenv import load_dotenv
from datetime import datetime

logger = logging.getLogger(__name__)
load_dotenv()

def load_to_s3(df, bucket_name=None, file_name=None):
    """
    อัปโหลดข้อมูล DataFrame ไปยัง AWS S3

    Args:
        df: DataFrame ที่ต้องอัปโหลด
        bucket_name: ชื่อ S3 bucket (default จากไฟล์ .env)
        file_name: ชื่อไฟล์ที่จะอัปโหลด
    """

    if df is None or df.empty:
        logger.warning("⚠️ ข้อมูล DataFrame ว่าง")
        return False

    # ดึง credentials จากไฟล์ .env
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "ap-southeast-1")
    bucket_name = bucket_name or os.getenv("AWS_S3_BUCKET")

    if not all([aws_access_key, aws_secret_key, bucket_name]):
        logger.error("❌ ไม่พบ AWS credentials หรือ S3 bucket name ในไฟล์ .env")
        return False

    try:
        # สร้าง S3 client
        logger.info(f"🔐 เชื่อมต่อ AWS S3 (region: {aws_region})...")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )

        # สร้างชื่อไฟล์ถ้ายังไม่มี (ใช้ timestamp)
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"weather_data_{timestamp}.csv"

        # แปลง DataFrame เป็น CSV
        csv_buffer = df.to_csv(index=False)

        # อัปโหลดไปยัง S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=csv_buffer
        )

        logger.info(f"✅ อัปโหลดสำเร็จ! (s3://{bucket_name}/{file_name})")
        return True

    except Exception as e:
        logger.error(f"❌ Error ในการอัปโหลด: {e}")
        return False

def load_to_local_csv(df, file_path="data/weather_data.csv"):
    """
    บันทึกข้อมูลลงไฟล์ CSV ในเครื่อง (ทดสอบ)
    """

    if df is None or df.empty:
        logger.warning("⚠️ ข้อมูล DataFrame ว่าง")
        return False

    try:
        # สร้างโฟลเดอร์ถ้าไม่มี
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        df.to_csv(file_path, index=False)
        logger.info(f"✅ บันทึกไฟล์สำเร็จ! ({file_path})")
        return True

    except Exception as e:
        logger.error(f"❌ Error ในการบันทึกไฟล์: {e}")
        return False

if __name__ == "__main__":
    from extract import extract_weather_data
    from transform import transform_weather_data

    # ทดสอบ
    df = extract_weather_data("Bangkok")
    df_clean = transform_weather_data(df)

    if df_clean is not None:
        # บันทึกลง CSV ในเครื่องก่อน (ทดสอบ)
        load_to_local_csv(df_clean)

        # อัปโหลดไป S3 (ต้องมี AWS credentials)
        # load_to_s3(df_clean)
