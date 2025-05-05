import os
import signal
import sys
import customtkinter as ctk
from components.core.bluetooth_manager import BluetoothManager
from components.ui.app_window import BluetoothManagerApp

def main():
    """Main entry point for Bluetooth Manager application"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    bt_manager = BluetoothManager()
    app = BluetoothManagerApp(bt_manager)
    app.mainloop()

if __name__ == "__main__":
    main() 