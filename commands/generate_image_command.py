import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def handle_generate_image_command(transcription, tts):
    # Get API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment variables")
        tts.speak("Sorry, I'm not configured to generate images yet.")
        return

    genai.configure(api_key=api_key)

    prompt = transcription.lower().split("generate image of", 1)[1].strip()

    if prompt:
        try:
            imagen = genai.ImageGenerationModel("imagen-3.0-generate-001")
            result = imagen.generate_images(
                prompt=prompt,
                number_of_images=1,
                safety_filter_level="block_only_high",
                person_generation="allow_adult",
                aspect_ratio="3:4",
                negative_prompt="Dont add a blury background",
            )

            if result.images:
                image = result.images[0]
                image_url = image.url
                image_response = requests.get(image_url)

                if image_response.status_code == 200:
                    folder_path = "generated_images"
                    os.makedirs(folder_path, exist_ok=True)
                    image_path = os.path.join(
                        folder_path, f"{prompt.replace(' ', '_')}.png"
                    )

                    with open(image_path, "wb") as image_file:
                        image_file.write(image_response.content)

                    print(f"Generated image saved at: {image_path}")
                    tts.speak(
                        f"Here is the generated image for {prompt}. Saved it in {folder_path}."
                    )
                else:
                    print("Failed to download the generated image.")
                    tts.speak("Sorry, I couldn't save the generated image.")
            else:
                print("No images generated.")
                tts.speak("Sorry, I couldn't generate the image.")
        except Exception as e:
            print(f"Error generating image: {e}")
            tts.speak("Sorry, I encountered an error while generating the image.")
    else:
        print("No description detected.")
        tts.speak("Please provide a description for the image.")
