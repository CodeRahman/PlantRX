from app.database import supabase
"""saves prefiction to the database using the python client"""
def save_prediction(user_id, image, label, confidence):
    
    supabase.table("predictions").insert({
        "user_id": user_id,
        "image": image,
        "label": label,
        "confidence": confidence
    }).execute()

"""Gets the users 10 previous predictions"""
def get_user_predictions(user_id, limit=10):
    
    response = supabase.table("predictions") \
                       .select("*") \
                       .eq("user_id", user_id) \
                       .order("created_at", desc=True) \
                       .limit(limit) \
                       .execute()
    return response.data if response.data else []
