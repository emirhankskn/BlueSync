import customtkinter as ctk
from components.ui.icons import IconFactory
from components.utils.constants import *
from components.utils.notifications import NotificationManager

class DeviceCard(ctk.CTkFrame):
    """Custom frame for displaying a device in a card-like style."""
    def __init__(self, master, device, callbacks):
        super().__init__(master, fg_color=("gray95", "gray20"), corner_radius=CORNER_RADIUS)
        
        self.device = device
        self.callbacks = callbacks
        self.is_editing = False
        
        self.status_color = CONNECTED_COLOR if device.connected else DISCONNECTED_COLOR
        
        self._create_layout()
    
    def _create_layout(self):
        """Create the card layout"""
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        self._create_left_section()
        self._create_middle_section()
        self._create_right_section()
    
    def _create_left_section(self):
        """Create the left section with status indicator and icon"""
        self.left_frame = ctk.CTkFrame(self.container, fg_color="transparent", width=50)
        self.left_frame.pack(side="left", padx=(0, PADDING))
        
        self.status_frame = ctk.CTkFrame(self.left_frame, fg_color=self.status_color,
                                        width=10, height=40, corner_radius=5)
        self.status_frame.pack(side="left", fill="y", padx=(0, 5))
        
        self.icon = IconFactory.create_device_icon(self.device.get_device_type())
        if self.icon:
            self.icon_label = ctk.CTkLabel(self.left_frame, text="", image=self.icon)
            self.icon_label.pack(side="left")
    
    def _create_middle_section(self):
        """Create the middle section with device info"""
        self.middle_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.middle_frame.pack(side="left", fill="both", expand=True)
        
        self.name_container = ctk.CTkFrame(self.middle_frame, fg_color="transparent")
        self.name_container.pack(anchor="w", pady=(0, 2), fill="x")
        
        display_name = self.device.get_display_name()
        self.name_label = ctk.CTkLabel(self.name_container, text=display_name,
                                     font=ctk.CTkFont(size=14, weight="bold"))
        self.name_label.pack(anchor="w")
        
        self.name_label.bind("<Double-Button-1>", self.on_name_double_click)
        
        self.name_entry = ctk.CTkEntry(self.name_container, font=ctk.CTkFont(size=14))
        
        self.address_label = ctk.CTkLabel(self.middle_frame, text=self.device.address,
                                         font=ctk.CTkFont(size=11),
                                         text_color=("gray50", "gray70"))
        self.address_label.pack(anchor="w")
        
        self.status_info_frame = ctk.CTkFrame(self.middle_frame, fg_color="transparent")
        self.status_info_frame.pack(anchor="w", fill="x", pady=(2, 0))
        
        status_text = "Connected" if self.device.connected else "Disconnected"
        self.status_label = ctk.CTkLabel(self.status_info_frame, text=status_text,
                                       font=ctk.CTkFont(size=12),
                                       text_color=self.status_color)
        self.status_label.pack(side="left", anchor="w")
        
        if self.device.connected:
            if self.device.battery_level is not None:
                battery_text = f" • {self.device.battery_level}%"
                battery_color = CRITICAL_BATTERY_COLOR if self.device.battery_level < CRITICAL_BATTERY_THRESHOLD else NORMAL_BATTERY_COLOR
                self.battery_label = ctk.CTkLabel(self.status_info_frame, text=battery_text,
                                              font=ctk.CTkFont(size=12),
                                              text_color=battery_color)
                self.battery_label.pack(side="left", anchor="w", padx=(5, 0))
                
                if self.device.battery_level < CRITICAL_BATTERY_THRESHOLD:
                    self.after(1000, lambda: self._send_low_battery_notification())
            else:
                self.battery_label = ctk.CTkLabel(self.status_info_frame, text=" • No battery info",
                                              font=ctk.CTkFont(size=12),
                                              text_color=("gray50", "gray70"))
                self.battery_label.pack(side="left", anchor="w", padx=(5, 0))
                
            self.refresh_battery_button = ctk.CTkButton(
                self.status_info_frame,
                text="↺",
                command=self.on_refresh_battery,
                width=24,
                height=24,
                corner_radius=CORNER_RADIUS,
                fg_color=BUTTON_COLOR,
                hover_color="#2a5a8b",
                font=ctk.CTkFont(size=14)
            )
            self.refresh_battery_button.pack(side="left", padx=(5, 0))
    
    def _create_right_section(self):
        """Create the right section with buttons"""
        self.right_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.right_frame.pack(side="right", padx=(PADDING, 0))
        
        if self.device.connected:
            self.connect_button = ctk.CTkButton(
                self.right_frame, 
                text="Disconnect",
                command=self.on_disconnect,
                fg_color="#f44336",
                hover_color="#d32f2f",
                width=100,
                height=32,
                corner_radius=CORNER_RADIUS
            )
        else:
            self.connect_button = ctk.CTkButton(
                self.right_frame, 
                text="Connect",
                command=self.on_connect,
                fg_color="#4CAF50",
                hover_color="#388E3C",
                width=100,
                height=32,
                corner_radius=CORNER_RADIUS
            )
        self.connect_button.pack(pady=(0, 5))
        
        self.auto_connect_var = ctk.BooleanVar(value=self.device.auto_connect)
        self.auto_connect_check = ctk.CTkCheckBox(
            self.right_frame, 
            text="Auto-Connect", 
            variable=self.auto_connect_var,
            command=self.on_auto_connect,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=2
        )
        self.auto_connect_check.pack()
    
    def _send_low_battery_notification(self):
        """Send notification about low battery level"""
        NotificationManager.send_low_battery_notification(
            self.device.get_display_name(),
            self.device.battery_level
        )
    
    def update_battery_display(self, battery_level:int):
        """Update the battery level display."""
        if hasattr(self, 'battery_label'):
            if battery_level is not None:
                battery_text = f" • {battery_level}%"
                battery_color = CRITICAL_BATTERY_COLOR if battery_level < CRITICAL_BATTERY_THRESHOLD else NORMAL_BATTERY_COLOR
                self.battery_label.configure(text=battery_text, text_color=battery_color)
                
                if battery_level < CRITICAL_BATTERY_THRESHOLD:
                    self._send_low_battery_notification()
            else:
                self.battery_label.configure(text=" • No battery info", text_color=("gray50", "gray70"))
        elif self.device.connected:
            self.status_info_frame = getattr(self, 'status_info_frame', None)
            if self.status_info_frame:
                if battery_level is not None:
                    battery_text = f" • {battery_level}%"
                    battery_color = CRITICAL_BATTERY_COLOR if battery_level < CRITICAL_BATTERY_THRESHOLD else NORMAL_BATTERY_COLOR
                    self.battery_label = ctk.CTkLabel(self.status_info_frame, text=battery_text,
                                                  font=ctk.CTkFont(size=12),
                                                  text_color=battery_color)
                    
                    if battery_level < CRITICAL_BATTERY_THRESHOLD:
                        self._send_low_battery_notification()
                else:
                    self.battery_label = ctk.CTkLabel(self.status_info_frame, text=" • No battery info",
                                                  font=ctk.CTkFont(size=12),
                                                  text_color=("gray50", "gray70"))
                
                self.battery_label.pack(side="left", anchor="w", padx=(5, 0))
    
    def update_name_display(self, new_name:str):
        """Update the display name"""
        self.name_label.configure(text=new_name)
    
    def on_name_double_click(self, event):
        """Handle double-click on name label"""
        if not self.device.connected:
            return
            
        if not self.is_editing:
            self.is_editing = True
            self.name_label.pack_forget()
            
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, self.device.get_display_name())
            self.name_entry.pack(anchor="w", fill="x")
            self.name_entry.focus_set()
            
            self.name_entry.bind("<Return>", self.on_name_change)
            self.name_entry.bind("<Escape>", self.cancel_edit)
            self.name_entry.bind("<FocusOut>", self.on_name_change)
    
    def on_name_change(self, event):
        """Handle name change"""
        if self.is_editing:
            new_name = self.name_entry.get().strip()
            self.callbacks['rename'](self.device.address, new_name)
            self.cancel_edit_ui()
    
    def cancel_edit(self, event):
        """Cancel name editing"""
        self.cancel_edit_ui()
    
    def cancel_edit_ui(self):
        """Cancel editing and restore UI"""
        self.is_editing = False
        self.name_entry.pack_forget()
        self.name_label.pack(anchor="w")
    
    def on_connect(self):
        """Handle connect button click"""
        self.callbacks['connect'](self.device.address)
    
    def on_disconnect(self):
        """Handle disconnect button click"""
        self.callbacks['disconnect'](self.device.address)
    
    def on_auto_connect(self):
        """Handle auto-connect checkbox change"""
        self.callbacks['auto_connect'](
            self.device.address, 
            self.auto_connect_var.get(), 
            self.device
        )
        
    def on_refresh_battery(self):
        """Handle battery refresh button click"""
        self.callbacks['refresh_battery'](self.device.address) 