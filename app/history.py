from app.database import get_supabase


def save_prediction(user_id, image, label, confidence):
    client = get_supabase()

    client.table("predictions").insert({
        "user_id": user_id,
        "image": image,
        "label": label,
        "confidence": confidence,
    }).execute()


def get_user_predictions(user_id, limit=10):
    client = get_supabase()

    response = (
        client.table("predictions")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


def delete_prediction(user_id, prediction_id):
    client = get_supabase()

    response = (
        client.table("predictions")
        .delete(returning="representation")
        .eq("id", prediction_id)
        .eq("user_id", user_id)
        .execute()
    )

    deleted_rows = response.data or []

    if not deleted_rows:
        return None

    return deleted_rows[0]