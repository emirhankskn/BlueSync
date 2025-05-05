import os
from PIL import Image
import customtkinter as ctk

class IconFactory:
    """Factory class for loading UI icons."""

    ASSETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')

    @staticmethod
    def create_device_icon(device_type:str, size:tuple=(24,24)) -> ctk.CTkImage:
        """Load an icon for a device type."""
        icon_map = {
            "headphones": "headphones.png",
            "speaker": "speaker.png",
            "mouse": "mouse.png",
            "keyboard": "keyboard.png",
            "controller": "controller.png",
            "phone": "phone.png"
        }

        icon_file = icon_map.get(device_type, 'generic.png')
        icon_path = os.path.join(IconFactory.ASSETS_PATH, icon_file)

        try:
            icon = Image.open(icon_path)
            icon = icon.resize(size, Image.LANCZOS)
            return ctk.CTkImage(light_image=icon, dark_image=icon, size=size)
        except Exception as e:
            print(f'Error loading icon {icon_file}: {e}')
            if icon_file != 'generic.png':
                try:
                    generic_path = os.path.join(IconFactory.ASSETS_PATH, 'generic.png')
                    icon = Image.open(generic_path)
                    icon = icon.resize(size, Image.LANCZOS)
                    return ctk.CTkImage(light_image=icon, dark_image=icon, size=size)
                except Exception: return None
            return None
        
    @staticmethod
    def create_bluetooth_icon(size:tuple=(64, 64)) -> Image:
        """Load bluetooth icon for the system tray"""
        icon_path = os.path.join(IconFactory.ASSETS_PATH, 'bluetooth.png')

        try:
            icon = Image.open(icon_path)
            icon = icon.resize(size, Image.LANCZOS)
            return icon
        except Exception as e:
            print(f'Error loading Bluetooth icon: {e}')
            return None