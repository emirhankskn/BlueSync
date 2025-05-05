class BluetoothDevice:
    def __init__(self, address:str, name:str, paired:bool=False, connected:bool=False,
                 auto_connect:bool=False, device_class:str=None, custom_name:str=None,
                 battery_level:int=None):
        """
        Initialize a Bluetooth device.
        
        Args:
            address (str): MAC address of the device.
            name (str): Name of the device.
            paired (bool): Whether the device is paired.
            connected (bool): Whether the device is connected.
            auto_connect (bool): Whether the device should auto-connect.
            device_class (str): Bluetooth device class code.
            custom_name (str): User-defined custom name for device.
            battery_level (int): Battery level percentage or None if not available.
        """
        self.address = address
        self.name = name if name else "Unknown Device"
        self.paired = paired
        self.connected = connected
        self.auto_connect = auto_connect
        self.device_class = device_class
        self.custom_name = custom_name
        self.battery_level = battery_level

    def get_display_name(self) -> str:
        """Get the custom name if set, otherwise the device name."""
        return self.custom_name if self.custom_name else self.name
    
    def get_device_type(self) -> str:
        """Determine the device type based on the name or device class."""
        name_lower = self.name.lower()

        if any(word in name_lower for word in ["headphone", "headset", "earphone", "earbud", "airpod"]):
            return "headphones"
        if any(word in name_lower for word in ["speaker", "sound", "audio"]):
            return "speaker"
        if any(word in name_lower for word in ["mouse", "mx", "trackpad"]):
            return "mouse"
        if any(word in name_lower for word in ["keyboard", "keychron", "magic keyboard"]):
            return "keyboard"
        if any(word in name_lower for word in ["controller", "gamepad", "playstation", "xbox", "joy-con"]):
            return "controller"
        if any(word in name_lower for word in ["phone", "iphone", "android", "pixel", "galaxy"]):
            return "phone"
            
        return "generic"

    def __eq__(self, other) -> bool:
        """Check if two devices are equal based on their address."""
        if not isinstance(other, BluetoothDevice): return False
        return self.address == other.address
    