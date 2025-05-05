from components.config.config_manager import ConfigManager
from components.core.bluetooth_backend import LinuxBluetoothBackend

class BluetoothManager:
    """Main bluetooth manager class that orchestrates all Bluetooth operations."""
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or ConfigManager()
        self.backend = LinuxBluetoothBackend(self.config_manager)

    def get_devices(self) -> list:
        return self.backend.get_devices()
    
    def scan_devices(self) -> bool:
        return self.backend.scan_devices()
    
    def connect_device(self, address) -> bool:
        return self.backend.connect_device(address)
    
    def disconnect_device(self, address) -> bool:
        return self.backend.disconnect_device(address)
    
    def disconnect_all_devices(self) -> bool:
        return self.backend.disconnect_all_devices()
    
    def rename_device(self, address, name) -> bool:
        return self.config_manager.set_device_name(address, name)
    
    def set_auto_connect(self, address, auto_connect=True) -> bool:
        if auto_connect: return self.config_manager.set_auto_connect_device(address)
        else:
            if self.config_manager.get_auto_connect_device() == address:
                return self.config_manager.set_auto_connect_device(None)
            return True