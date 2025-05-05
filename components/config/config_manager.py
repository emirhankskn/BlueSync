import os
import json
from components.utils.constants import CONFIG_PATH

class ConfigManager:
    """Manages configuration storage and retrieval"""
    def __init__(self, config_path:str=None):
        self.config_path = config_path or CONFIG_PATH
        self.config=self.load_config()

    def load_config(self) -> dict:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f'Error parsing config file, using default config.')
                return self._get_default_config()
            except Exception as e:
                print(f'Error loading config: {e}')
                return self._get_default_config()
        return self._get_default_config()
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f)
            return True
        except Exception as e:
            print(f'Error savin config file: {e}')
            return False
        
    def _get_default_config(self) -> dict:
        """Get defaylt configuration."""
        return {'auto_connect_device':None, 'renamed_devices':{}}
    
    def get_auto_connect_device(self) -> str:
        """Get auto-connect device address"""
        return self.config.get('auto_connect_device', None)
    
    def set_auto_connect_device(self, address) -> bool:
        self.config['auto_connect_device'] = address
        return self.save_config()
    
    def get_renamed_devices(self) -> dict:
        """Get dictionary of renamed devices"""
        return self.config.get('renamed_devices', {})
    
    def set_device_name(self, address:str, name:str) -> bool:
        """Set custom name for a device."""
        renamed_devices = self.get_renamed_devices()
        if name and name.strip(): renamed_devices[address] = name.strip()
        elif address in renamed_devices: del renamed_devices[address]
        
        self.config['renamed_devices'] = renamed_devices
        return self.save_config()