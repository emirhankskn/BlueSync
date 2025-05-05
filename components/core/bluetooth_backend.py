import re
import abc
import dbus
import subprocess
from components.core.device import BluetoothDevice

class BluetoothBackend(abc.ABC):
    """Abstract base class for Bluetooth backend implementations."""
    @abc.abstractmethod
    def get_devices(self) -> list: pass

    @abc.abstractmethod
    def scan_devices(self) -> bool: pass

    @abc.abstractmethod
    def connect_device(self, address:str) -> bool: pass

    @abc.abstractmethod
    def disconnect_device(self, address:str) -> bool: pass

    @abc.abstractmethod
    def disconnect_all_devices(self) -> bool: pass

    @abc.abstractmethod
    def get_battery_level(self, device_path:str) -> int: pass

class LinuxBluetoothBackend(BluetoothBackend):
    """Linux implementation of BluetoothBackend using dbus"""
    def __init__(self, config_manager):
        self.bus = dbus.SystemBus()
        self.config_manager = config_manager

    def get_devices(self):
        devices = []
        try:
            obj = self.bus.get_object('org.bluez', '/')
            manager = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
            objects = manager.GetManagedObjects()

            auto_connect_device = self.config_manager.get_auto_connect_device()
            renamed_devices = self.config_manager.get_renamed_devices()

            for path, interfaces in objects.items():
                if 'org.bluez.Device1' in interfaces:
                    device_props = interfaces['org.bluez.Device1']

                    if 'Address' not in device_props: continue
                    address = str(device_props['Address'])
                    if 'Name' not in device_props: continue

                    name = str(device_props.get('Name'))
                    paired = bool(device_props.get('Paired', False))
                    connected = bool(device_props.get('Connected', False))
                    device_class = device_props.get('Class', 0)

                    auto_connect = (address == auto_connect_device)
                    custom_name = renamed_devices.get(address, None)

                    battery_level = None
                    if connected:
                        print(f"\n Checking battery for connected device: {name} ({address})")

                        if 'org.bluez.Battery1' in interfaces:
                            print(f'Device has Battery1 interface')
                            battery_props = interfaces['org.bluez.Battery1']                        
                            if 'Percentage' in battery_props:
                                battery_level = int(battery_props['Percentage'])
                                print(f'Battery level from interfaces: {battery_level}%')
                        else:
                            print(f'Device does not have Battery1 interface in GetManagedObjects.')
                            battery_level = self.get_battery_level(path)

                        if battery_level is not None: print(f'Final battery level: {battery_level}%')
                        else: print('Could not determine battery level.')

                    device = BluetoothDevice(
                        address, name, paired, connected, auto_connect,
                        device_class, custom_name, battery_level
                    )
                    devices.append(device)
        except Exception as e: print(f'Error getting devices: {e}')
        return devices
    
    def scan_devices(self):
        try:
            subprocess.run(['bluetoothctl', 'scan', 'on'], timeout=5)
            return True
        except subprocess.TimeoutExpired: return True
        except Exception as e: 
            print(f'Error scanning for devices: {e}')
            return False
        
    def connect_device(self, address):
        try:
            subprocess.run(['bluetoothctl', 'trust', address])
            result = subprocess.run(
                ['bluetoothctl', 'connect', address],
                capture_output=True,
                text=True
            )

            if 'Failed' in result.stdout or 'failed' in result.stderr:
                print(f'Error connecting to device: {result.stderr or result.stdout}')
                return False
            return True
        except Exception as e:
            print(f'Error connecting to device: {e}')
            return False
        
    def disconnect_device(self, address):
        try:
            result = subprocess.run(
                ['bluetoothctl', 'disconnect', address], 
                capture_output=True, 
                text=True
            )
            
            if "Failed" in result.stdout or "failed" in result.stderr:
                print(f"Error disconnecting device: {result.stderr or result.stdout}")
                return False
                
            return True
        except Exception as e:
            print(f"Error disconnecting device: {e}")
            return False
        

    def disconnect_all_devices(self):
        devices = self.get_devices()
        success = True
        for device in devices:
            if device.connected:
                if not self.disconnect_device(device.address):
                    success = False
        return success
    

    def get_battery_level(self, path):
        try:
            print(f"Attempting to get battery level for device at path: {path}")
            
            try:
                device_obj = self.bus.get_object('org.bluez', path)
                battery_props = dbus.Interface(device_obj, 'org.freedesktop.DBus.Properties')
                try:
                    battery_level = battery_props.Get('org.bluez.Battery1', 'Percentage')
                    print(f"Found battery level via Battery1 interface: {battery_level}")
                    return int(battery_level)
                except dbus.exceptions.DBusException as e:
                    print(f"No Battery1 interface available: {e}")
            except Exception as e:
                print(f"Error accessing device object: {e}")
                
            try:
                device_obj = self.bus.get_object('org.bluez', path)
                props_iface = dbus.Interface(device_obj, 'org.freedesktop.DBus.Properties')
                props = props_iface.GetAll('org.bluez.Device1')
                
                if 'BatteryPercentage' in props:
                    print(f"Found battery level in device properties: {props['BatteryPercentage']}")
                    return int(props['BatteryPercentage'])
                print("No BatteryPercentage property found in device properties")
            except Exception as e:
                print(f"Error getting device properties: {e}")
                
            try:
                address = self._get_address_from_path(path)
                print(f"Checking UPower for device with address: {address}")
                
                upower_bus = dbus.SystemBus()
                upower_proxy = upower_bus.get_object('org.freedesktop.UPower', '/org/freedesktop/UPower')
                upower_interface = dbus.Interface(upower_proxy, 'org.freedesktop.UPower')
                
                device_paths = upower_interface.EnumerateDevices()
                
                for device_path in device_paths:
                    dev_proxy = upower_bus.get_object('org.freedesktop.UPower', device_path)
                    dev_props = dbus.Interface(dev_proxy, 'org.freedesktop.DBus.Properties')
                    
                    try:
                        device_type = dev_props.Get('org.freedesktop.UPower.Device', 'Type')
                        if device_type == 7:
                            device_native_path = str(dev_props.Get('org.freedesktop.UPower.Device', 'NativePath'))
                            print(f"Found Bluetooth device in UPower: {device_native_path}")
                            
                            if address.replace(':', '_').lower() in device_native_path.lower():
                                percentage = dev_props.Get('org.freedesktop.UPower.Device', 'Percentage')
                                print(f"Found battery level via UPower: {percentage}%")
                                return int(percentage)
                    except Exception as e:
                        print(f"Error checking UPower device: {e}")
                
                print("Device not found in UPower")
            except Exception as e:
                print(f"Error using UPower method: {e}")
                
            try:
                address = self._get_address_from_path(path)
                
                print(f"Trying bluetoothctl info for address: {address}")
                result = subprocess.run(['bluetoothctl', 'info', address], capture_output=True, text=True)
                output = result.stdout
                
                battery_matches = re.findall(r'Battery Percentage: .*?(\d+)%', output)
                if battery_matches:
                    battery_level = int(battery_matches[0])
                    print(f"Found battery level via bluetoothctl: {battery_level}")
                    return battery_level
                    
                battery_matches = re.findall(r'Battery Level: .*?(\d+)%', output)
                if battery_matches:
                    battery_level = int(battery_matches[0])
                    print(f"Found battery level via bluetoothctl: {battery_level}")
                    return battery_level
                    
                print("No battery information found in bluetoothctl output")
            except Exception as e:
                print(f"Error using bluetoothctl method: {e}")
                
            print("All battery detection methods failed for this device")
            return None
        except Exception as e:
            print(f"Error getting battery level: {e}")
            return None
        
    def _get_address_from_path(self, path):
        address = path.split('/')[-1]
        if '_' in address: address = address.replace('_', ':')
        return address
            

            



