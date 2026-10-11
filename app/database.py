import os

from flask import g, session
from supabase import create_client
from supabase.lib.client_options import ClientOptions


def get_supabase():
    if "supabase" not in g:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_KEY must be configured"
            )

        client = create_client(
            url,
            key,
            options=ClientOptions(
                persist_session=False,
                auto_refresh_token=False,
            ),
        )

        access_token = session.get("access_token")
        if access_token:
            client.postgrest.auth(access_token)

        g.supabase = client

    return g.supabase