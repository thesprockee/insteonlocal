import pprint
#from time import sleep

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

class Dimmer():
    """This class defines an object for an INSTEON Dimmer"""
    def __init__(self, hub, device_id):
        self.device_id = device_id.upper()
        self.hub = hub
        self.logger = hub.logger


    def status(self, return_led=0):
        """Get status from device"""
        status = self.hub.get_device_status(self.device_id, return_led)
        self.logger.info("Dimmer %s status: %s", self.device_id,
                         pprint.pformat(status))
        return status


    def on(self, level):
        """Turn light on at saved ramp rate"""
        self.logger.info("Dimmer %s on level %s", self.device_id, level)

        self.hub.direct_command(self.device_id, '11', self.hub.brightness_to_hex(level))

        success = self.hub.check_success(self.device_id, '11', self.hub.brightness_to_hex(level))
        if success:
            self.logger.info("Dimmer %s on: Light turned on successfully",
                             self.device_id)
            self.hub.clear_device_command_cache(self.device_id)
        else:
            self.logger.error("Dimmer %s on: Light did not turn on", self.device_id)

        return success


    def on_saved(self):
        """Turn light on to saved state using 'fast'"""
        self.logger.info("Dimmer %s on_saved", self.device_id)

        self.hub.direct_command(self.device_id, '12', '00')

        success = self.hub.check_success(self.device_id, '12', '00')
        if success:
            self.logger.info("Dimmer %s on_saved: Light turned on successfully",
                             self.device_id)
            self.hub.clear_device_command_cache(self.device_id)
        else:
            self.logger.error("Dimmer %s on_saved: Light did not turn on",
                              self.device_id)

        return success


    def off(self):
        """Turn light off at saved ramp rate"""
        self.logger.info("Dimmer %s off", self.device_id)

        self.hub.direct_command(self.device_id, '13', '00')

        success = self.hub.check_success(self.device_id, '13', '00')
        if success:
            self.logger.info("Dimmer %s off: Light turned off successfully",
                             self.device_id)
            self.hub.clear_device_command_cache(self.device_id)
        else:
            self.logger.error("Dimmer %s off: Light did not turn off",
                              self.device_id)

        return success


    def off_instant(self):
        """Turn light off"""
        self.logger.info("Dimmer %s off_instant", self.device_id)

        self.hub.direct_command(self.device_id, '14', '00')

        success = self.hub.check_success(self.device_id, '14', '00')
        if success:
            self.logger.info("Dimmer %s off_instant: Light turned off successfully",
                             self.device_id)
            self.hub.clear_device_command_cache(self.device_id)
        else:
            self.logger.error("Dimmer %s off_instant: Light did not turn off",
                              self.device_id)

        return success


    def change_level(self, level):
        """Change light level"""
        self.logger.info("Dimmer %s change_level: level %s", self.device_id,
                         level)

        self.hub.direct_command(self.device_id, '21',
                                self.hub.brightness_to_hex(level))
        success = self.hub.check_success(self.device_id, '21',
                                         self.hub.brightness_to_hex(level))
        if success:
            self.logger.info("Dimmer %s change_level: Light level changed successfully",
                             self.device_id)
            self.hub.clear_device_command_cache(self.device_id)
        else:
            self.logger.error("Dimmer %s change_level: Light level was not changed",
                              self.device_id)

        return success


    def brighten_step(self):
        """Brighten light by one step"""
        self.logger.info("Dimmer %s brighten_step", self.device_id)

        self.hub.direct_command(self.device_id, '15', '00')
        success = self.hub.check_success(self.device_id, '15', '00')
        if success:
            self.logger.info("Dimmer %s brighten_step: Light brightened successfully",
                             self.device_id)
            self.hub.clear_device_command_cache(self.device_id)
        else:
            self.logger.error("Dimmer %s brighten_step: Light brightened failure",
                              self.device_id)


    def dim_step(self):
        """Dim light by one step"""
        self.logger.info("Dimmer %s dim_step", self.device_id)

        self.hub.direct_command(self.device_id, '16', '00')
        success = self.hub.check_success(self.device_id, '16', '00')
        if success:
            self.logger.info("Dimmer %s dim_step: Light dimmed successfully",
                             self.device_id)
            self.hub.clear_device_command_cache(self.device_id)
        else:
            self.logger.error("Dimmer %s dim_step: Light dim failure",
                              self.device_id)

        return success


    def start_change(self, direction):
        """Start changing light level manually. Direction should be 'up' or 'down'"""
        self.logger.info("Dimmer %s start_change: %s", self.device_id, direction)

        if direction == 'up':
            level = '01'
        elif direction == 'down':
            level = '00'
        else:
            self.logger.error("Dimmer %s start_change: %s is invalid, use up or down",
                              self.device_id, direction)
            return False

        self.hub.direct_command(self.device_id, '17', level)
        success = self.hub.check_success(self.device_id, '17',
                                         self.hub.brightness_to_hex(level))
        if success:
            self.logger.info("Dimmer %s start_change: Light started changing successfully",
                             self.device_id)
            self.hub.clear_device_command_cache(self.device_id)
        else:
            self.logger.error("Dimmer %s start_change: Light did not change",
                              self.device_id)

        return success


    def stop_change(self):
        """Stop changing light level manually"""
        self.logger.info("Dimmer %s stop_change", self.device_id)

        self.hub.direct_command(self.device_id, '18', '00')
        success = self.hub.check_success(self.device_id, '18', '00')
        if success:
            self.logger.info("Dimmer %s stop_change: Light stopped changing successfully",
                             self.device_id)
            self.hub.clear_device_command_cache(self.device_id)
        else:
            self.logger.error("Dimmer %s stop_change: Light did not stop",
                              self.device_id)

        return success


    def beep(self):
        """Make dimmer beep. Not all devices support this"""
        self.logger.info("Dimmer %s beep", self.device_id)

        self.hub.direct_command(self.device_id, '30', '00')

        success = self.hub.check_success(self.device_id, '30', '00')

        return success
