import subprocess
import pygame
import asyncio
import webbrowser
from typing import Dict, Callable, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from chatbot.chatbot import ChatBot
from commands.generate_image_command import handle_generate_image_command
from commands.screen_recording_command import ScreenRecorder
from commands.search_command import parse_search_command
from commands.take_screenshot_command import handle_take_screenshot_command
from config.config_manager import ConfigManager
from text_to_speech.text_to_speech import TextToSpeech


@dataclass
class CommandContext:
    """Context object containing all necessary dependencies for command execution"""

    transcription: str
    tts: "TextToSpeech"
    chatbot: Optional["ChatBot"] = None
    config: Optional["ConfigManager"] = None


class Command(ABC):
    """Abstract base class for all commands"""

    @abstractmethod
    async def execute(self, context: CommandContext) -> str:
        pass


class OpenCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        app_name = context.transcription.lower().split("open", 1)[1].strip()
        if not app_name:
            await context.tts.speak("Please specify the application to open.")
            return "continue"

        try:
            subprocess.Popen(app_name)
            await context.tts.speak(f"Opening {app_name}.")
            return "continue"
        except Exception as e:
            logging.error(f"Failed to open {app_name}: {e}")
            await context.tts.speak(f"Sorry, I couldn't open {app_name}.")
            return "continue"


class PlayCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        song_name = context.transcription.lower().split("play", 1)[1].strip()
        if not song_name:
            await context.tts.speak("Please specify the song to play.")
            return "continue"

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(f"audio/{song_name}.mp3")
            pygame.mixer.music.play()
            await context.tts.speak(f"Playing {song_name}.")
            return "continue"
        except Exception as e:
            logging.error(f"Failed to play {song_name}: {e}")
            await context.tts.speak(f"Sorry, I couldn't play {song_name}.")
            return "continue"


class GenerateImageCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        prompt = context.transcription.lower().split("generate image", 1)[1].strip()
        if not prompt:
            await context.tts.speak("Please provide a description for the image.")
            return "continue"

        try:
            # Assuming handle_generate_image_command is updated to be async
            await handle_generate_image_command(prompt, context.tts)
            return "continue"
        except Exception as e:
            logging.error(f"Failed to generate image: {e}")
            await context.tts.speak("Sorry, I couldn't generate the image.")
            return "continue"


class ScreenshotCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        try:
            await handle_take_screenshot_command(context.tts)
            return "continue"
        except Exception as e:
            logging.error(f"Failed to take screenshot: {e}")
            await context.tts.speak("Sorry, I couldn't take the screenshot.")
            return "continue"


class StartRecordingCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        try:
            ScreenRecorder.start_recording(context.tts)
            return "continue"
        except Exception as e:
            logging.error(f"Failed to start recording: {e}")
            await context.tts.speak("Sorry, I couldn't start the recording.")
            return "continue"


class StopRecordingCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        try:
            ScreenRecorder.stop_recording(context.tts)
            return "continue"
        except Exception as e:
            logging.error(f"Failed to stop recording: {e}")
            await context.tts.speak("Sorry, I couldn't stop the recording.")
            return "continue"


class SearchCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        try:
            search_result = parse_search_command(context.transcription)
            if search_result:
                item, app = search_result
                if app.lower() == "google":
                    url = f"https://www.google.com/search?q={item}"
                    webbrowser.open(url)
                    await context.tts.speak(f"Searching for {item} in Google.")
            return "continue"
        except Exception as e:
            logging.error(f"Failed to perform search: {e}")
            await context.tts.speak("Sorry, I couldn't perform the search.")
            return "continue"


class CommandHandler:
    def __init__(self, config_manager=None):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.tts = TextToSpeech()
        self.chatbot = ChatBot(config_manager)
        self.executor = ThreadPoolExecutor(max_workers=3)

        # Command registry with improved structure
        self.commands: Dict[str, Command] = {
            "open": OpenCommand(),
            "play": PlayCommand(),
            "generate image": GenerateImageCommand(),
            "take screenshot": ScreenshotCommand(),
            "start recording": StartRecordingCommand(),
            "stop recording": StopRecordingCommand(),
            "search for": SearchCommand(),
        }

        # Add dynamic command aliases
        self.command_aliases = {
            "launch": "open",
            "run": "open",
            "start": "play",
            "create image": "generate image",
            "make image": "generate image",
            "capture screen": "take screenshot",
            "record screen": "start recording",
            "end recording": "stop recording",
            "look up": "search for",
            "find": "search for",
        }

    def _create_context(self, transcription: str) -> CommandContext:
        return CommandContext(
            transcription=transcription,
            tts=self.tts,
            chatbot=self.chatbot,
            config=self.config,
        )

    def _get_command(self, command_text: str) -> Optional[Command]:
        # Check direct commands first
        for cmd_key, cmd in self.commands.items():
            if cmd_key in command_text:
                return cmd

        # Check aliases
        for alias, cmd_key in self.command_aliases.items():
            if alias in command_text:
                return self.commands.get(cmd_key)

        return None

    async def process_command(self, transcription: str) -> str:
        try:
            if not transcription:
                self.logger.warning("Received empty transcription")
                return "continue"

            transcription = transcription.lower()

            # Handle stop command
            if "stop listening" in transcription:
                await self.tts.speak("Stopping listening.")
                return "stop"

            # Handle thanks command
            if "thanks" in transcription or "thank you" in transcription:
                await self.tts.speak("You're welcome!")
                return "continue"

            # Handle Jarvis commands
            if "jarvis" in transcription:
                command_text = transcription.split("jarvis", 1)[1].strip()

                # Find and execute matching command
                command = self._get_command(command_text)
                if command:
                    context = self._create_context(command_text)
                    return await command.execute(context)

                # Default to chatbot if no command matches
                return await self._handle_chatbot_query(command_text)

            return "continue"

        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            await self.tts.speak("I encountered an error processing your command.")
            return "continue"

    async def _handle_chatbot_query(self, query: str) -> str:
        try:
            response = await self.chatbot.respond_async(query)
            await self.tts.speak(response)
            return "continue"
        except Exception as e:
            self.logger.error(f"Chatbot error: {e}")
            await self.tts.speak("I encountered an error processing your request.")
            return "continue"

    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
