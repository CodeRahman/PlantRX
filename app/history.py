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


def delete_prediction_batch(user_id, batch_size=100):
    client = get_supabase()

    response = (
        client.table("predictions")
        .select("id")
        .eq("user_id", user_id)
        .order("id")
        .limit(batch_size)
        .execute()
    )

    predictions = response.data or []

    if not predictions:
        return []

    prediction_ids = [
        prediction["id"]
        for prediction in predictions
    ]

    deleted_response = (
        client.table("predictions")
        .delete(returning="representation")
        .eq("user_id", user_id)
        .in_("id", prediction_ids)
        .execute()
    )

    deleted_predictions = deleted_response.data or []

    if not deleted_predictions:
        raise RuntimeError(
            "Predictions were found but none could be deleted"
        )

    return deleted_predictions