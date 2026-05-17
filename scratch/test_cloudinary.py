import cloudinary
import cloudinary.uploader
import os

# Configuration       
cloudinary.config( 
    cloud_name = "dezmwbvms", 
    api_key = "148796495294218", 
    api_secret = "z_bZnewokAjAb7NHRVIWrjavSsw",
    secure=True
)

try:
    print("Testing Cloudinary upload...")
    upload_result = cloudinary.uploader.upload("https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg",
                                               public_id="test_shoes_alphahome")
    print("Upload Successful!")
    print(f"Secure URL: {upload_result.get('secure_url')}")
except Exception as e:
    print(f"Upload Failed: {e}")
