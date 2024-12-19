def handle_chatbot_command(transcription, chatbot, tts, extra_query):
    query = transcription.lower().split("jarvis", 1)[1].strip()
    if query:
        response = chatbot.respond(query + " " + extra_query)
        response = response.split(">")[0].strip()
        print(f"Bot says: {response}")
        tts.speak(response)
        return response
    else:
        message = "No query detected."
        print(message)
        tts.speak(message)
        return message
