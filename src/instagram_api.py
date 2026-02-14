import requests
import time
import os
from dotenv import load_dotenv



def upload_to_instagram(
    image_url: str,
    caption: str
):
    load_dotenv()
    BASE_URL = os.getenv("BASE_URL")
    ig_user_id = os.getenv("IG_USER_ID")
    #page_access_token = os.getenv("PAGE_ACCESS_TOKEN")
    page_access_token=os.getenv("PAGE_ACCESS_TOKEN")
    
    print("🚀 Starting Instagram upload")

    # Create media container
    create_url = f"{BASE_URL}/{ig_user_id}/media"
    print(image_url)
    create_payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": page_access_token
    }

    create_response = requests.post(create_url, data=create_payload)
    create_result = create_response.json()
    print("📦 Create container response:", create_result)

    if "id" not in create_result:
        raise Exception(f"Failed to create media container: {create_result}")

    creation_id = create_result["id"]

    time.sleep(5)

    # Publish media
    publish_url = f"{BASE_URL}/{ig_user_id}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": page_access_token
    }

    publish_response = requests.post(publish_url, data=publish_payload)
    publish_result = publish_response.json()
    print("🚀 Publish response:", publish_result)

    if "id" not in publish_result:
        raise Exception(f"Failed to publish media: {publish_result}")

    print("🎉 Instagram post uploaded successfully")
    return publish_result
