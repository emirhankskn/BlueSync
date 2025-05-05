import pystray
import threading
import logging
from components.ui.icons import IconFactory

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TrayIconManager:
    """Manages the system tray icon"""
    def __init__(self, show_window_callback, quit_callback, quit_disconnect_callback):
        self.show_window_callback = show_window_callback
        self.quit_callback = quit_callback
        self.quit_disconnect_callback = quit_disconnect_callback
        self.tray_icon = None
        self._setup_tray()
    
    def _setup_tray(self):
        """Setup the system tray icon and menu"""
        try:
            icon_image = IconFactory.create_bluetooth_icon()
            if not icon_image:
                logging.error("Failed to load tray icon image.")
                return

            menu = (
                pystray.MenuItem('Show Bluetooth Manager', self.show_window),
                pystray.MenuItem('Exit', self.quit_app),
                pystray.MenuItem('Exit and Close All Connections', self.quit_and_close_connections)
            )

            self.tray_icon = pystray.Icon("bluetooth_manager", icon_image, "Bluetooth Manager", menu)
            logging.info("Tray icon setup completed successfully.")
        except Exception as e:
            logging.error(f"Error setting up tray icon: {e}")

    def run(self):
        """Run the tray icon in a separate thread"""
        try:
            if self.tray_icon:
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
                logging.info("Tray icon is running.")
            else:
                logging.error("Tray icon is not initialized.")
        except Exception as e:
            logging.error(f"Error running tray icon: {e}")
    
    def stop(self):
        """Stop the tray icon"""
        try:
            if self.tray_icon:
                self.tray_icon.stop()
                logging.info("Tray icon stopped.")
            else:
                logging.error("Tray icon is not initialized.")
        except Exception as e:
            logging.error(f"Error stopping tray icon: {e}")
    
    def show_window(self, icon=None, item=None):
        """Show the main window"""
        if self.show_window_callback: self.show_window_callback()
    
    def quit_app(self, icon=None, item=None):
        """Quit the application"""
        if self.quit_callback: self.quit_callback()
    
    def quit_and_close_connections(self, icon=None, item=None):
        """Quit the application and close all connections"""
        if self.quit_disconnect_callback: self.quit_disconnect_callback()