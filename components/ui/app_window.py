import time
import threading
import customtkinter as ctk
from components.ui.device_card import DeviceCard
from components.ui.tray_icon import TrayIconManager
from components.utils.constants import (
    PADDING, CORNER_RADIUS, BUTTON_COLOR, SCANNING_COLOR,
    BATTERY_CHECK_INTERVAL_MS
)

class BluetoothManagerApp(ctk.CTk):
    """Main application window for Bluetooth Manager"""
    def __init__(self, bluetooth_manager):
        super().__init__()
        self.bt_manager = bluetooth_manager
        self.devices = []
        self.scanning = False
        self.exit_app = False
        self.battery_check_job = None
        
        self.title("Bluetooth Manager")
        self.geometry("700x600")
        self.minsize(600, 450)
        self._create_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.tray_icon = TrayIconManager(
            self.show_window,
            self.quit_app,
            self.quit_and_close_connections
        )
        self.tray_icon.run()
        
        self.refresh_devices()
        self.try_auto_connect()
        self.start_battery_check_timer()
    
    def _create_ui(self):
        """Create the application UI"""
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        self._create_header()
        self._create_button_frame()
        self._create_devices_section()
        self._create_status_bar()
    
    def _create_header(self):
        """Create the header with title and theme switch"""
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, PADDING))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Bluetooth Manager", 
                                      font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(side="left")

        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self.header_frame,
            values=["System", "Light", "Dark"],
            command=self.change_appearance_mode,
            width=100
        )
        self.appearance_mode_menu.pack(side="right")
        self.appearance_mode_menu.set("System")
    
    def _create_button_frame(self):
        """Create the button frame with scan and refresh buttons"""
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", pady=(0, PADDING))
        
        self.scan_button = ctk.CTkButton(
            self.button_frame, 
            text="Scan for Devices", 
            command=self.toggle_scan,
            fg_color=BUTTON_COLOR,
            corner_radius=CORNER_RADIUS,
            height=36
        )
        self.scan_button.pack(side="left", padx=(0, PADDING))
        
        self.refresh_button = ctk.CTkButton(
            self.button_frame, 
            text="Refresh List", 
            command=self.refresh_devices,
            fg_color=BUTTON_COLOR,
            corner_radius=CORNER_RADIUS,
            height=36
        )
        self.refresh_button.pack(side="left")
    
    def _create_devices_section(self):
        """Create the devices section with devices list"""
        self.devices_title = ctk.CTkLabel(self.main_frame, text="Devices", 
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        anchor="w")
        self.devices_title.pack(fill="x", pady=(0, 5))
        
        self.devices_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.devices_container.pack(fill="both", expand=True)
        
        self.devices_frame = ctk.CTkScrollableFrame(
            self.devices_container,
            fg_color=("gray90", "gray17"),
            corner_radius=CORNER_RADIUS
        )
        self.devices_frame.pack(fill="both", expand=True)
    
    def _create_status_bar(self):
        """Create the status bar"""
        self.status_frame = ctk.CTkFrame(self.main_frame, height=30, 
                                       fg_color=("gray85", "gray25"),
                                       corner_radius=CORNER_RADIUS)
        self.status_frame.pack(fill="x", pady=(PADDING, 0))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready", anchor="w", padx=10)
        self.status_label.pack(fill="x", pady=5)
    
    def change_appearance_mode(self, new_appearance_mode):
        """Change the appearance mode"""
        ctk.set_appearance_mode(new_appearance_mode)
    
    def start_battery_check_timer(self):
        """Start periodic timer to check battery levels"""
        self.check_battery_levels()
        
    def check_battery_levels(self):
        """Periodically check battery levels for connected devices"""
        if self.battery_check_job: self.after_cancel(self.battery_check_job)

        if self.winfo_viewable(): self.update_battery_levels()
        
        self.battery_check_job = self.after(BATTERY_CHECK_INTERVAL_MS, self.check_battery_levels)
    
    def update_battery_levels(self):
        """Refresh battery levels for connected devices"""
        updated_devices = self.bt_manager.get_devices()
        device_widgets = [w for w in self.devices_frame.winfo_children() if isinstance(w, DeviceCard)]
        
        for widget in device_widgets:
            for device in updated_devices:
                if widget.device.address == device.address and device.connected:
                    if device.battery_level is not None:
                        widget.device.battery_level = device.battery_level
                        widget.update_battery_display(device.battery_level)
    
    def try_auto_connect(self):
        """Attempt to connect to the auto-connect device"""
        self.update_status("Checking for auto-connect device...")
        
        def connect_thread():
            self.devices = self.bt_manager.get_devices()
            auto_device = next((d for d in self.devices if d.auto_connect), None)
            
            if auto_device:
                if not auto_device.connected:
                    self.update_status(f"Auto-connecting to {auto_device.name}...")
                    success = self.bt_manager.connect_device(auto_device.address)
                    if success: self.update_status(f"Auto-connected to {auto_device.name}")
                    else: self.update_status(f"Failed to auto-connect to {auto_device.name}")
                else: self.update_status(f"Auto-connect device {auto_device.name} already connected")
            else: self.update_status("No auto-connect device configured")
            
            self.after(1000, self.refresh_devices)
        
        thread = threading.Thread(target=connect_thread)
        thread.daemon = True
        thread.start()
    
    def update_status(self, message):
        """Update the status bar with a message"""
        self.after(0, lambda: self.status_label.configure(text=message))
    
    def show_window(self):
        """Show the application window from the system tray"""
        self.deiconify()
        self.lift()
        self.focus_force()
        self.refresh_devices()
    
    def on_close(self):
        """Handle window close event"""
        self.withdraw()
    
    def quit_app(self):
        """Quit the application"""
        self.exit_app = True
        if self.tray_icon: self.tray_icon.stop()
        self.destroy()
        
    def quit_and_close_connections(self):
        """Quit the application and close all connections"""
        self.update_status("Closing all connections...")
        
        def disconnect_and_quit():
            success = self.bt_manager.disconnect_all_devices()
            self.update_status("All connections closed" if success else "Failed to close all connections")
            self.after(500, self.quit_app)
        
        thread = threading.Thread(target=disconnect_and_quit)
        thread.daemon = True
        thread.start()
    
    def toggle_scan(self):
        """Toggle device scanning"""
        if not self.scanning:
            self.scanning = True
            self.scan_button.configure(text="Stop Scanning", fg_color=SCANNING_COLOR)
            self.update_status("Scanning for devices...")
            
            scan_thread = threading.Thread(target=self.scan_for_devices)
            scan_thread.daemon = True
            scan_thread.start()
        else:
            self.scanning = False
            self.scan_button.configure(text="Scan for Devices", fg_color=BUTTON_COLOR)
            self.update_status("Scan stopped")
    
    def scan_for_devices(self):
        """Scan for new devices"""
        self.bt_manager.scan_devices()
        end_time = time.time() + 10
        while self.scanning and time.time() < end_time:
            self.refresh_devices()
            time.sleep(2)
        
        self.scanning = False
        self.after(0, lambda: self.scan_button.configure(text="Scan for Devices", fg_color=BUTTON_COLOR))
        self.after(0, lambda: self.update_status("Scan completed"))
    
    def refresh_devices(self):
        """Refresh the devices list"""
        self.devices = self.bt_manager.get_devices()
        self.update_device_list()
        
    def update_device_list(self):
        """Update the devices list UI"""
        for widget in self.devices_frame.winfo_children(): widget.destroy()
        
        if not self.devices:
            no_devices_label = ctk.CTkLabel(
                self.devices_frame, 
                text="No devices found", 
                font=ctk.CTkFont(size=14),
                text_color=("gray50", "gray70")
            )
            no_devices_label.pack(pady=50)
            return
        
        for device in self.devices:
            callbacks = {
                'connect': self.connect_device,
                'disconnect': self.disconnect_device,
                'auto_connect': self.toggle_auto_connect,
                'rename': self.rename_device,
                'refresh_battery': self.refresh_battery
            }
            
            device_card = DeviceCard(self.devices_frame, device, callbacks)
            device_card.pack(fill="x", pady=5, padx=5)
    
    def connect_device(self, address):
        """Connect to a device"""
        self.update_status(f"Connecting to device...")
        
        def connect_thread():
            success = self.bt_manager.connect_device(address)
            if success: self.update_status("Device connected successfully")
            else: self.update_status("Failed to connect device")
            self.after(1000, self.refresh_devices)
        
        thread = threading.Thread(target=connect_thread)
        thread.daemon = True
        thread.start()
        
    def disconnect_device(self, address):
        """Disconnect from a device"""
        self.update_status(f"Disconnecting device...")
        
        def disconnect_thread():
            success = self.bt_manager.disconnect_device(address)
            if success: self.update_status("Device disconnected successfully")
            else: self.update_status("Failed to disconnect device")
            self.after(1000, self.refresh_devices)
        
        thread = threading.Thread(target=disconnect_thread)
        thread.daemon = True
        thread.start()
    
    def toggle_auto_connect(self, address, auto_connect, device):
        """Toggle auto-connect for a device"""
        self.update_status(f"{'Setting' if auto_connect else 'Removing'} auto-connect device...")
        
        def auto_connect_thread():
            if auto_connect:
                for dev in self.devices:
                    if dev.auto_connect and dev.address != address:
                        self.bt_manager.config_manager.set_auto_connect_device(None)
            
            success = self.bt_manager.config_manager.set_auto_connect_device(address if auto_connect else None)
            
            if success:
                device_name = device.get_display_name()
                if auto_connect: self.update_status(f"{device_name} will auto-connect on startup")
                else: self.update_status(f"{device_name} will no longer auto-connect")
            else: self.update_status(f"Failed to update auto-connect settings")
            
            self.after(1000, self.refresh_devices)
        
        thread = threading.Thread(target=auto_connect_thread)
        thread.daemon = True
        thread.start()
    
    def rename_device(self, address, new_name):
        """Rename a device"""
        self.update_status(f"Renaming device...")
        
        device = next((d for d in self.devices if d.address == address), None)
        if not device:
            self.update_status("Device not found")
            return
        
        if not device.connected:
            self.update_status("Only connected devices can be renamed")
            return
        
        success = self.bt_manager.config_manager.set_device_name(address, new_name)
        
        if success:
            device.custom_name = new_name if new_name else None
            
            for widget in self.devices_frame.winfo_children():
                if isinstance(widget, DeviceCard) and widget.device.address == address:
                    display_name = device.get_display_name()
                    widget.update_name_display(display_name)
                    break
            
            self.update_status(f"Device renamed successfully")
        else: self.update_status(f"Failed to rename device")
    
    def refresh_battery(self, address):
        """Manually refresh the battery level for a specific device"""
        self.update_status(f"Refreshing battery information...")
        
        def refresh_thread():
            devices = self.bt_manager.get_devices()
            
            device = next((d for d in devices if d.address == address), None)
            if not device:
                self.update_status("Device not found")
                return
            
            if device.connected:
                device_cards = [w for w in self.devices_frame.winfo_children() 
                              if isinstance(w, DeviceCard) and w.device.address == address]
                
                if device_cards:
                    device_card = device_cards[0]
                    device_card.device.battery_level = device.battery_level
                    device_card.update_battery_display(device.battery_level)
                
                if device.battery_level is not None: self.update_status(f"Battery level: {device.battery_level}%")
                else: self.update_status("Battery information not available for this device")
            else: self.update_status("Device not connected")
        
        thread = threading.Thread(target=refresh_thread)
        thread.daemon = True
        thread.start()
    
    def mainloop(self, *args, **kwargs):
        """Override mainloop to properly exit the application"""
        try: super().mainloop(*args, **kwargs)
        finally:
            if hasattr(self, 'tray_icon') and self.tray_icon and not self.exit_app: self.tray_icon.stop()
            if self.battery_check_job: self.after_cancel(self.battery_check_job) 