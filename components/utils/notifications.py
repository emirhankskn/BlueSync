import subprocess

class NotificationManager:
    """Handles system notifications."""

    @staticmethod
    def send_notification(title:str, message:str, urgency:str='normal', icon:str=None):
        try:
            cmd = ['notify-send']
            if urgency: cmd.extend(['-u', urgency])
            if icon: cmd.extend(['-i', icon])
            cmd.extend([title, message])

            subprocess.Popen(cmd)
            return True
        except Exception as e:
            print(f'Error sending notification: {e}')
            return False
        
    @staticmethod
    def send_low_battery_notification(device_name:str, battery_level:int):
        """Send a notification about low battery level."""
        return NotificationManager.send_notification(
            f'Low Battery: {device_name}',
            f'Battery level is critically low ({battery_level}%)',
            urgency='critical',
            icon='battery_low'
        )