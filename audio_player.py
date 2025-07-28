import pygame
import time
import soundfile as sf
import os
from mutagen.mp3 import MP3

# Try to import pygame._sdl2.audio for device selection
try:
    import pygame._sdl2.audio as sdl2_audio
    SDL2_AUDIO_AVAILABLE = True
except ImportError:
    SDL2_AUDIO_AVAILABLE = False

class AudioManager:

    def __init__(self, device_name=None):
        """
        Initialize audio manager with optional device selection
        device_name: Name of the audio device to use (e.g., "MIXLINE")
        """
        self.device_name = device_name
        self.target_device = None
        
        if device_name and SDL2_AUDIO_AVAILABLE:
            # Get list of available output devices
            try:
                output_devices = sdl2_audio.get_audio_device_names(False)
                print(f"Available output devices: {output_devices}")
                
                # Find the device that contains our target name
                for device in output_devices:
                    if device_name.lower() in device.lower():
                        self.target_device = device
                        break
                
                if self.target_device:
                    print(f"Found target device: {self.target_device}")
                else:
                    print(f"✗ FAILED: Could not find device containing '{device_name}'")
            except Exception as e:
                print(f"Error setting up device: {e}")
        
        pygame.mixer.init()

    def list_devices(self):
        """List all available audio devices"""
        if SDL2_AUDIO_AVAILABLE:
            try:
                output_devices = sdl2_audio.get_audio_device_names(False)
                input_devices = sdl2_audio.get_audio_device_names(True)
                
                print("=== AUDIO DEVICES ===")
                print("Output devices:")
                for i, device in enumerate(output_devices):
                    print(f"  {i}: {device}")
                
                print("\nInput devices:")
                for i, device in enumerate(input_devices):
                    print(f"  {i}: {device}")
            except Exception as e:
                print(f"Error listing devices: {e}")
        else:
            print("pygame._sdl2.audio not available")

    def play_audio(self, file_path, sleep_during_playback=True, delete_file=False, play_using_music=True):
        """
        Parameters:
        file_path (str): path to the audio file
        sleep_during_playback (bool): means program will wait for length of audio file before returning
        delete_file (bool): means file is deleted after playback (note that this shouldn't be used for multithreaded function calls)
        play_using_music (bool): means it will use Pygame Music, if false then uses pygame Sound instead
        """
        print(f"Playing file with pygame: {file_path}")
        
        # Pre-init with device if we have one
        if self.target_device:
            pygame.mixer.pre_init(devicename=self.target_device)
        
        pygame.mixer.init()
        
        if play_using_music:
            # Pygame Mixer only plays one file at a time, but audio doesn't glitch
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
        else:
            # Pygame Sound lets you play multiple sounds simultaneously, but the audio glitches for longer files
            pygame_sound = pygame.mixer.Sound(file_path) 
            pygame_sound.play()

        if sleep_during_playback:
            # Calculate length of the file, based on the file format
            _, ext = os.path.splitext(file_path) # Get the extension of this file
            if ext.lower() == '.wav':
                wav_file = sf.SoundFile(file_path)
                file_length = wav_file.frames / wav_file.samplerate
                wav_file.close()
            elif ext.lower() == '.mp3':
                mp3_file = MP3(file_path)
                file_length = mp3_file.info.length
            else:
                print("Cannot play audio, unknown file type")
                return

            # Sleep until file is done playing
            time.sleep(file_length)

            # Delete the file
            if delete_file:
                # Stop pygame so file can be deleted
                # Note, this can cause issues if this function is being run on multiple threads, since it quit the mixer for the other threads too
                pygame.mixer.music.stop()
                pygame.mixer.quit()

                try:  
                    os.remove(file_path)
                    print(f"Deleted the audio file.")
                except PermissionError:
                    print(f"Couldn't remove {file_path} because it is being used by another process.")

# TESTS
if __name__ == '__main__':
    print("=== AUDIO DEVICE TEST ===")
    
    # List devices
    manager = AudioManager()
    manager.list_devices()
    
    # Test with MIXLINE
    print(f"\n=== TESTING WITH 'MIXLINE' ===")
    mixline_manager = AudioManager("MIXLINE")
    