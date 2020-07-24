import serial
import time

'''  To call this code only
import pantilt_control_code as pt
pantil = pt.PanTilt('/dev/ttyUSB0')  # Enter with the pantilt USB port
# For choose string == 'pan' or 'tilt' in the entry
pantilt.set_angle('tilt or pan', angle)
pantilt.set_pan_angle(angle)
pantilt.set_tilt_angle(angle)
pantilt.get_pan_angle()
pantilt.get_tilt_angle()
del pantilt

Structure of the pelco-D frame
[sincronismo, addres, command 1, command 2, data 1, data 2, checksun]
'''


class PanTilt():

    def __init__(self, port):
        self._data_write = [255, 1, 0, 0, 0, 0, 0]  # Pelco-D frame
        self._data_read = [255, 1, 0, 0, 0, 0, 0]
        self._ser = serial.Serial(port, 2400, timeout=1)
        self._byte_query_pan = 81  # Query Pan Position
        self._byte_query_tilt = 83  # Query Tilt position
        # pdb.set_trace()

    def stop(self):
        print('Stop \n')
        self._data_write = [255, 1, 0, 0, 0, 0, 0]
        self._ser.write(self._data_write)  # Write in the serial port

    def get_pan_angle(self):
        return self.read_serial_port_and_returns_angle(self._byte_query_pan)

    def get_tilt_angle(self):
        return self.read_serial_port_and_returns_angle(self._byte_query_tilt)

    def read_serial_port_and_returns_angle(self, byte_query):
        self._cont_byte = 0
        self._ser.write([255, 1, 0, byte_query, 0, 0, byte_query + 1])
        while self._cont_byte < 7:
            self._data_str = self._ser.read(1)
            self._byte = int.from_bytes(self._data_str, byteorder='big')
            self._data_read.insert(self._cont_byte, self._byte)
            self._cont_byte = self._cont_byte + 1
            angle = self._data_read[4]*256/100 + self._data_read[5]/100
        return angle

    def __del__(self):
        self._ser.close()
        print('Destructor...')


#  S. C. is used to teleoperated the pan tilt
class StandardCommands(PanTilt):
    def __init__(self, port):
        super().__init__(port)
        self._pan_right_byte = 2
        self._pan_left_byte = 4
        self._tilt_up_byte = 16  # 8
        self._tilt_down_byte = 8  # 16
        self._pan_right_and_tilt_up_byte = 18  # 10
        self._pan_right_and_tilt_down_byte = 10  # 12
        self._pan_left_and_tilt_up_byte = 20 # 18
        self._pan_left_and_tilt_down_byte = 12 # 20

    def teleoperation(self, operation_specification,
                      required_value):
        self._movement_orientation = operation_specification
        self._valid_command = False
        #  print('valid_command initializes --> ', self._valid_command)

        try:
            self._speed = int(required_value)  # 0 <= speed <= 60
            # print('self._speed = ', self._speed)

            if (self._speed >= 0 and self._speed <= 60):
                # print('Speed is ok!')

                if self._movement_orientation == 'right':
                    self._data_write[3] = self._pan_right_byte
                    self._data_write[4] = self._speed
                    self._data_write[5] = 0
                    self._valid_command = True

                elif self._movement_orientation == 'left':
                    self._data_write[3] = self._pan_left_byte
                    self._data_write[4] = self._speed
                    self._data_write[5] = 0
                    self._valid_command = True

                elif self._movement_orientation == 'up':
                    self._data_write[3] = self._tilt_up_byte
                    self._data_write[4] = 0
                    self._data_write[5] = self._speed
                    self._valid_command = True

                elif self._movement_orientation == 'down':
                    self._data_write[3] = self._tilt_down_byte
                    self._data_write[4] = 0
                    self._data_write[5] = self._speed
                    self._valid_command = True

                elif self._movement_orientation == 'right_and_up':
                    self._data_write[3] = self._pan_right_and_tilt_up_byte
                    self._data_write[4] = self._speed
                    self._data_write[5] = self._speed
                    self._valid_command = True

                elif self._movement_orientation == 'right_and_down':
                    self._data_write[3] = self._pan_right_and_tilt_down_byte
                    self._data_write[4] = self._speed
                    self._data_write[5] = self._speed
                    self._valid_command = True

                elif self._movement_orientation == 'left_and_up':
                    self._data_write[3] = self._pan_left_and_tilt_up_byte
                    self._data_write[4] = self._speed
                    self._data_write[5] = self._speed
                    self._valid_command = True

                elif self._movement_orientation == 'left_and_down':
                    self._data_write[3] = self._pan_left_and_tilt_down_byte
                    self._data_write[4] = self._speed
                    self._data_write[5] = self._speed
                    self._valid_command = True
                else:
                    raise ValueError('The operation specification is not valid'
                                     '\n\t\t     Enter with a string')
            else:
                raise ValueError('Speed ranges from zero to sixty')

            # Send to pantilt

            if self._valid_command is True:
                print('Command is ok!')
                self._ser.write(self._data_write)

        except ZeroDivisionError as error:
            print('ZeroDivisionError')
            print("Description error:  ", error)
        except ValueError as error:
            print('ValueError')
            print("Description error:  ", error)
        except TypeError as error:
            print('TypeError')
            print("Description error:  ", error)
        except Exception as error:
            print('Exception')
            print("Description error:  ", error)


#  A. C. is used to send the pan tilt to a certain angle
class AdvancedCommands(PanTilt):
    def __init__(self, port):
        super().__init__(port)
        self._byte_set_pan = 75  # Set Pan Position
        self._byte_set_tilt = 77  # Set Tilt position
        self._setter = None
        self._getter = None
        self._angle_difference_calculator = None

    def set_angle(self, command, new_angle):

        try:
            # Defines the getter and setter in the function below
            self.type_range_and_command_checker(command, new_angle)

            old_angle = self._getter()
            number_of_attempts = 3
            arrived_in_position = False

            for attempt in range(number_of_attempts):
                self._setter(new_angle)
                start_time = time.time()
                # time_variation = self.time_calculator(old_angle,
                # new_angle, start_time)
                self.time_calculator(old_angle, new_angle, start_time)
                # print(self._getter(), new_angle)
                self._difference = self._angle_difference_calculator(
                                            self._getter(), new_angle)
                arrived_in_position = self._difference <= 0.4
                if arrived_in_position is True:
                    break

            if not arrived_in_position:
                raise Exception("Failed to move to desired pan tilt position, "
                                "necessary maintenance")

            new_angle = self._getter()
            # displacement = self._angle_difference_calculator(old_angle,
            #                                                 new_angle)
            # speed = displacement/time_variation
            # print('\nold_angle, new_angle, displacement,'
            #       ' time_variation, speed')
            # print(f'{old_angle:.2f}   , {new_angle:.2f}   ,'
            #      f'{displacement:.2f}     , {time_variation:.2f}
            #      f,{speed:.2f}')

        except ZeroDivisionError as error:
            print('ZeroDivisionError')
            print("Description error:  ", error)
        except ValueError as error:
            print('ValueError')
            print("Description error:  ", error)
        except TypeError as error:
            print('TypeError')
            print("Description error:  ", error)
        except Exception as error:
            print('Exception')
            print("Description error:  ", error)

    # This function check the type, the range and the command
    def type_range_and_command_checker(self, command, new_angle):

        # Type Checker
        if not (type(new_angle) == int or type(new_angle) == float):
            raise TypeError('The new_angle variable must be either'
                            ' int or float')
        # Type command
        if command == 'pan':
            # print('command == pan')

            if not (new_angle > 0 and new_angle < 360):
                raise ValueError('Desired pan angle out of range'
                                 'Enter with 0< angle <360')

            self._getter = self.get_pan_angle
            self._setter = self.set_pan_angle
            self._angle_difference_calculator = self.tilt_displacement_calculator

        elif command == 'tilt':
            if (new_angle > 90) and (new_angle < 311):
                raise Exception('Desired tilt angle in dead zone')
            elif (new_angle < -49) or (new_angle >= 360):
                raise ValueError('Desired tilt angle out of range')
            elif (new_angle >= -49) and (new_angle < 0):
                new_angle = new_angle + 360  # For negative angle

            self._getter = self.get_tilt_angle
            self._setter = self.set_tilt_angle
            self._angle_difference_calculator = self.pan_displacement_calculator

        print('Command and angle input are OK!\n\n')

    def set_pan_angle(self, angle):
        angle = float(angle)
        self.frame_byte_calculator(angle, self._byte_set_pan)
        self._ser.write(self._data_write)

    def set_tilt_angle(self, angle):
        angle = float(angle)
        # print('set_tilt_angle \n')
        self.frame_byte_calculator(angle, self._byte_set_tilt)
        self._ser.write(self._data_write)

    # Frame byte calculator from angle and direction(byte3)
    def frame_byte_calculator(self, angle, byte3):
        self._data_write[3] = byte3
        self._data_write[4] = int(angle*100/256)
        # print(self._data_write[4])
        self._data_write[5] = int(angle*100) - self._data_write[4]*256

        if self._data_write[5] != 255:
            self._data_write[5] = self._data_write[5]
        else:
            self._data_write[5] = 254

        # print(self._data_write[5])
        print('Command sent:  ', self._data_write)
        self._data_write[6] = 10  # Can be any number
        """The correct thing is to put the checksum,
        but don't work in this hardware.
        self._data_write[6] = ( 1
                            + byte3
                            + self._data_write[4]
                            + self._data_write[5])%256
        """
        return self._data_write

    # Calcula o tempo ate chegar ao destino
    def time_calculator(self, old_angle, new_angle, start_time):
        """ iterations is number of correct iterations accumulated until you
        accept that Pan Tilt has entered the desired range.
        """
        iterations = 3
        cont = 1
        read_interval = 0.5
        previous_time = 0
        maximum_pantilt_speed = 10  # degrees/seconds, Estimated based on tests
        self._difference = self._angle_difference_calculator(old_angle,
                                                             new_angle)
        maximum_time = max(self._difference / maximum_pantilt_speed, 2)

        while cont <= iterations:
            if time.time() - previous_time >= read_interval:
                previous_time = time.time()
                current_time_variation = previous_time - start_time
                current_angle = self._getter()  # Take the current angle
                if current_time_variation > maximum_time:
                    break
                print('Current angle: ', current_angle)
                print('Counter: ', cont)
                self._difference = self._angle_difference_calculator(
                            current_angle, new_angle)
                if self._difference <= 0.4:
                    read_interval = 0.001
                    cont = cont + 1
            time.sleep(0.1)
        time_variation = time.time() - start_time
        return time_variation

    # Calcula o deslocamento em graus
    def tilt_displacement_calculator(self, old_or_current_angle, new_angle):
        self._difference = abs(new_angle - old_or_current_angle)
        return self._difference

    def pan_displacement_calculator(self, old_or_current_angle, new_angle):
        self._difference = new_angle - old_or_current_angle
        self._difference = abs((self._difference+180) % 360 - 180)
        return self._difference
