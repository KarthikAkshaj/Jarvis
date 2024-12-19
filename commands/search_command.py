def parse_search_command(transcription):
    if "search for" in transcription.lower() and "in" in transcription.lower():
        try:
            parts = (
                transcription.lower().split("search for", 1)[1].strip().split("in", 1)
            )
            item = parts[0].strip()
            app = parts[1].strip() if len(parts) > 1 else ""
            return item, app
        except Exception:
            return None
    return None
