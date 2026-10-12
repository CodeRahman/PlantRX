from uuid import uuid4

from app.database import get_supabase


PREDICTION_BUCKET = "prediction-images"


def upload_prediction_image(user_id, image_bytes):
    image_path = f"{user_id}/{uuid4().hex}.jpg"

    client = get_supabase()

    client.storage.from_(PREDICTION_BUCKET).upload(
        path=image_path,
        file=image_bytes,
        file_options={
            "content-type": "image/jpeg",
            "upsert": "false",
        },
    )

    return image_path


def get_prediction_image_url(image_path):
    client = get_supabase()

    response = (
        client.storage
        .from_(PREDICTION_BUCKET)
        .create_signed_url(image_path, 600)
    )

    return response["signedURL"]


def delete_prediction_image(image_path):
    client = get_supabase()

    client.storage.from_(PREDICTION_BUCKET).remove(
        [image_path]
    )