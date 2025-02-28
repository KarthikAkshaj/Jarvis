import subprocess
import pygame
import asyncio
import webbrowser
from typing import Dict, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from concurrent.futures import ThreadPoolExecutor

from chatbot.chatbot import ChatBot
from commands import open_command
from commands import play_command
from commands import search_command
from commands.open_command import handle_open_command
from commands.play_command import handle_play_command
from commands.search_command import  parse_search_command
from commands.generate_image_command import handle_generate_image_command
from commands.screen_recording_command import ScreenRecorder
from commands.take_screenshot_command import handle_take_screenshot_command
from commands.weather_command import WeatherSystem
from commands.time_management import ReminderSystem  
from config.config_manager import ConfigManager
from text_to_speech.text_to_speech import TextToSpeech
from commands.system_controls.volume_control import VolumeController
from commands.system_controls.brightness_control import BrightnessController
from commands.system_controls.system_command import SystemController
from commands.calendar.event_handler import EventHandler
from commands.notes.note_manager import NoteManager
from commands.notes.voice_memo import VoiceMemoRecorder


@dataclass
class CommandContext:
    transcription: str
    tts: "TextToSpeech"
    chatbot: Optional["ChatBot"] = None
    config: Optional["ConfigManager"] = None


class Command(ABC):
    """Abstract base class for all commands"""

    @abstractmethod
    async def execute(self, context: CommandContext) -> str:
        pass


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


class OpenCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        app_name = context.transcription.lower().split("open", 1)[1].strip()
        if not app_name:
            await context.tts.speak("Please specify the application to open.")
            return "continue"

        try:
            open_command.handle_open_command(app_name, context.tts)
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
            play_command.handle_play_command(song_name, context.tts)
            return "continue"
        except Exception as e:
            logging.error(f"Failed to play {song_name}: {e}")
            await context.tts.speak(f"Sorry, I couldn't play {song_name}.")
            return "continue"


class SearchCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        try:
            search_result = SearchCommand(context.transcription)
            if search_result:
                item, app = search_result
                if app.lower() == "google":
                    search_command.handle_search_command(item, app, context.tts)
            return "continue"
        except Exception as e:
            logging.error(f"Failed to perform search: {e}")
            await context.tts.speak("Sorry, I couldn't perform the search.")
            return "continue"


class GenerateImageCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        prompt = context.transcription.lower().split("generate image", 1)[1].strip()
        if not prompt:
            await context.tts.speak("Please provide a description for the image.")
            return "continue"

        try:
            handle_generate_image_command(prompt, context.tts)
            return "continue"
        except Exception as e:
            logging.error(f"Failed to generate image: {e}")
            await context.tts.speak("Sorry, I couldn't generate the image.")
            return "continue"


class SystemControlCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        from commands.system_controls.system_command import SystemController

        command = context.transcription.lower()
        controller = SystemController()

        try:
            if "shutdown" in command:
                # Parse delay if specified
                delay = 0
                if "in" in command or "after" in command:
                    try:
                        delay = int("".join(filter(str.isdigit, command)))
                    except:
                        delay = 0
                controller.shutdown(delay)
                await context.tts.speak(
                    f"Shutting down system{' in '+str(delay)+' minutes' if delay else ''}."
                )
            elif "restart" in command or "reboot" in command:
                controller.restart()
                await context.tts.speak("Restarting system.")
            elif "sleep" in command:
                controller.sleep()
                await context.tts.speak("Putting system to sleep.")
            elif "lock" in command:
                controller.lock_screen()
                await context.tts.speak("Locking screen.")
            return "continue"
        except Exception as e:
            logging.error(f"Error executing system command: {e}")
            await context.tts.speak("Sorry, I couldn't execute that system command.")
            return "continue"


class VolumeCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        from commands.system_controls.volume_control import VolumeController

        command = context.transcription.lower()
        controller = VolumeController()

        try:
            if "mute" in command:
                controller.mute()
                await context.tts.speak("Audio muted.")
            elif "unmute" in command:
                controller.unmute()
                await context.tts.speak("Audio unmuted.")
            elif "volume" in command:
                if "up" in command or "increase" in command:
                    controller.adjust_volume(10)
                    await context.tts.speak("Volume increased.")
                elif "down" in command or "decrease" in command:
                    controller.adjust_volume(-10)
                    await context.tts.speak("Volume decreased.")
                else:
                    try:
                        volume = int("".join(filter(str.isdigit, command)))
                        controller.set_volume(volume)
                        await context.tts.speak(f"Volume set to {volume} percent.")
                    except:
                        current = controller.get_volume()
                        await context.tts.speak(f"Current volume is {current} percent.")
            return "continue"
        except Exception as e:
            logging.error(f"Error controlling volume: {e}")
            await context.tts.speak("Sorry, I couldn't control the volume.")
            return "continue"


class BrightnessCommand(Command):
    async def execute(self, context: CommandContext) -> str:

        command = context.transcription.lower()
        controller = BrightnessController()

        try:
            if "increase" in command or "up" in command:
                controller.adjust_brightness(10)
                await context.tts.speak("Brightness increased.")
            elif "decrease" in command or "down" in command:
                controller.adjust_brightness(-10)
                await context.tts.speak("Brightness decreased.")
            else:
                try:
                    level = int("".join(filter(str.isdigit, command)))
                    controller.set_brightness(level)
                    await context.tts.speak(f"Brightness set to {level} percent.")
                except:
                    current = controller.get_brightness()
                    await context.tts.speak(f"Current brightness is {current} percent.")
            return "continue"
        except Exception as e:
            logging.error(f"Error controlling brightness: {e}")
            await context.tts.speak("Sorry, I couldn't control the brightness.")
            return "continue"


class CalendarCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        from commands.calendar.event_handler import EventHandler

        try:
            handler = EventHandler()
            response = handler.process_event_command(context.transcription)
            await context.tts.speak(response)
            return "continue"
        except Exception as e:
            logging.error(f"Error handling calendar command: {e}")
            await context.tts.speak("Sorry, I couldn't process that calendar command.")
            return "continue"


class NoteCommand(Command):
    async def execute(self, context: CommandContext) -> str:
        from commands.notes.note_manager import NoteManager

        command = context.transcription.lower()
        manager = NoteManager()

        try:
            if "take note" in command or "add note" in command:
                content = command.split("note", 1)[1].strip()
                if not content:
                    await context.tts.speak("What would you like to note down?")
                    return "continue"

                result = manager.add_note(content)
                await context.tts.speak(result)

            elif "list notes" in command or "show notes" in command:
                notes = manager.get_notes()
                response = manager.format_notes_response(notes)
                await context.tts.speak(response)

            elif "search notes" in command:
                query = command.split("search notes", 1)[1].strip()
                notes = manager.search_notes(query)
                response = manager.format_notes_response(notes)
                await context.tts.speak(response)

            elif "export notes" in command:
                format = "txt" if "text" in command else "json"
                result = manager.export_notes(format)
                await context.tts.speak(result)

            return "continue"

        except Exception as e:
            logging.error(f"Error handling note command: {e}")
            await context.tts.speak("Sorry, I couldn't process that note command.")
            return "continue"


class VoiceMemoCommand(Command):
    def __init__(self):
        self.recorder = None
        self.current_stream = None
        self.current_filename = None

    async def execute(self, context: CommandContext) -> str:
        from commands.notes.voice_memo import VoiceMemoRecorder

        command = context.transcription.lower()

        try:
            if "start voice memo" in command:
                if not self.recorder:
                    self.recorder = VoiceMemoRecorder()
                self.current_filename, self.current_stream = (
                    self.recorder.start_recording()
                )
                await context.tts.speak("Starting voice memo recording")

            elif "stop voice memo" in command:
                if self.recorder and self.current_stream:
                    self.recorder.stop_recording(
                        self.current_filename, self.current_stream
                    )
                    await context.tts.speak("Voice memo saved")
                    self.current_stream = None

            elif "play voice memo" in command:
                if not self.recorder:
                    self.recorder = VoiceMemoRecorder()
                memos = self.recorder.list_memos()
                if memos:
                    self.recorder.play_memo(str(memos[-1]))  # Play latest memo
                    await context.tts.speak("Playing voice memo")
                else:
                    await context.tts.speak("No voice memos found")

            elif "list voice memos" in command:
                if not self.recorder:
                    self.recorder = VoiceMemoRecorder()
                memos = self.recorder.list_memos()
                memo_count = len(memos)
                await context.tts.speak(f"You have {memo_count} voice memos")

            return "continue"

        except Exception as e:
            logging.error(f"Error handling voice memo command: {e}")
            await context.tts.speak(
                "Sorry, I couldn't process that voice memo command."
            )
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
            "take screenshot": handle_take_screenshot_command(),
            "start recording": StartRecordingCommand(),
            "stop recording": StopRecordingCommand(),
            "search for": SearchCommand(),
            "weather": WeatherSystem(),
            "forecast": WeatherSystem(),
            "remind": ReminderSystem(),
            "list reminders": ReminderSystem(),
            "timer": ReminderSystem(),
            "list timers": ReminderSystem(),
            "calendar": CalendarCommand(),
            "schedule": CalendarCommand(),
            "event": CalendarCommand(),
            "note": NoteCommand(),
            "voice memo": VoiceMemoCommand(),
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
            "set a timer": "timer",
            "set timer": "timer",
            "show reminders": "list reminders",
            "show timers": "list timers",
            "check weather": "weather",
            "weather forecast": "forecast",
            "add event": "event",
            "new event": "event",
            "show events": "calendar",
            "list events": "calendar",
            "delete event": "event",
            "remove event": "event",
            "take note": "note",
            "add note": "note",
            "list notes": "note",
            "show notes": "note",
            "search notes": "note",
            "start recording memo": "voice memo",
            "stop recording memo": "voice memo",
            "play memo": "voice memo",
            "list memos": "voice memo",
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
