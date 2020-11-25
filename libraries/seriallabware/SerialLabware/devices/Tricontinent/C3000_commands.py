#!/usr/bin/python
"""
:mod:"C3000_C3000MP_commands" -- Commands for Tricontinent C3000 and C3000MP syringe pumps
===================================

.. module:: C3000_C3000MP_commands
   :platform: Windows, Linux
   :synopsis: Command set for Tricontinent C3000 and C3000MP syringe pumps (currently, DT protocol only)
.. moduleauthor:: Sergey Zalesskiy <sergey.zalesskiy@glasgow.ac.uk>

(c) 2018 The Cronin Group, University of Glasgow

This provides a python class listing the commands for the Tricontinent C3000 and C3000MP syringe pumps. The current implementation is based on the
Product Manual (Publication 8694-12 E), chapter 5 "Operating instructions" and chapter 9, section 3, "Data Terminal (DT) protocol"
"""

# Exception classes

class C3000Error(Exception):
    """General error"""
    pass

class C3000ProtocolError(C3000Error):
    """All errors returned by pump through status byte in the reply"""
    pass

class C3000_commands_DT():
    """DT protocol commands"""

    # This class just aggregates all command strings. It shouldn't be instantiated
    def __new__(cls, *args, **kwargs):
        raise C3000Error()

    # Mapping of rotary switch settings to apparent pump address on serial
    # Please, note, position F is not used (see p.23 of the manual)
    VALID_ADDRESSES = {
        "0": "1",
        "1": "2",
        "2": "3",
        "3": "4",
        "4": "5",
        "5": "6",
        "6": "7",
        "7": "8",
        "8": "9",
        "9": ":",
        "A": ";",
        "B": "<",
        "C":  "=",
        "D": ">",
        "E": "?",
        "all": "-"
        }
    
    # Allowed valve positions
    # Y-valves and T-valves use IOBE-notation
    # 6-pos valves use I1..I6/O1..O6 notation (I - moves CW, O - moves CCW)
    # 3-pos distribution valves can use either IOBE or I1..I3/O1..O3. We prefer the latter as being more intuitive.
    VLV_POS = (
        "I", # Input
        "O", # Output
        "B", # Bypass
        "E", # Extra
        "I1",
        "I2",
        "I3",
        "I4",
        "I5",
        "I6",
        "O1",
        "O2",
        "O3",
        "O4",
        "O5",
        "O6"
        )

    # Valve types
    VLV_TYPES = {}
    VLV_TYPES["3POS_Y"] = "1"
    # 11 - I1..I3/O1..O3 notation, 4 - IOBE notation
    VLV_TYPES["3POS_DISTR"] = "11"
    VLV_TYPES["4POS_90DEG"] = "2"
    VLV_TYPES["3POS_T"] = "5"
    VLV_TYPES["4POS_T"] = "5"
    VLV_TYPES["6POS_DISTR"] = "7"
    VLV_TYPES["4POS_LOOP"] = "9"
    
    # Plunger motor resolution modes
    RESOLUTION_MODES = {
        "N0":3000,  # Normal mode - power up default
        "N1":24000, # Positioning micro-increment mode
        "N2":24000  # Positioning & velocity micro-increment mode
    } 
    
    # Plunger motor ramp slope modes. Key - ramp code, Value - list of ramp slope in increments/sec^2 for N0-N1 and N2 modes
    RAMP_SLOPE_MODES = {
        "1" : [2500, 20000],
        "2" : [5000, 40000],
        "3" : [7500, 60000],
        "4" : [10000, 80000],
        "5" : [12500, 100000],
        "6" : [15000, 120000],
        "7" : [17500, 140000],
        "8" : [20000, 160000],
        "9" : [22500, 180000],
        "10" : [25000, 200000],
        "11" : [27500, 220000],
        "12" : [30000, 240000],
        "13" : [32500, 260000],
        "14" : [35000, 280000], # Power-up default
        "15" : [37500, 300000],
        "16" : [40000, 320000],
        "17" : [42500, 340000],
        "18" : [45000, 360000],
        "19" : [47500, 380000],
        "20" : [50000, 400000]
    }

    # Plunger motor speed. Key - speed code, Value - list of speeds in steps/sec for N0-N1 and N2 modes
    SPEED_MODES = {
        "0": [6000, 48000],
        "1": [5600, 44800],
        "2": [5000, 40000],
        "3": [4400, 35200],
        "4": [3800, 30400],
        "5": [3200, 25600],
        "6": [2600, 20800],
        "7": [2200, 17600],
        "8": [2000, 16000],
        "9": [1800, 14400],
        "10": [1600, 12800],
        "11": [1400, 11200], # Power-up default
        "12": [1200, 9600],
        "13": [1000, 8000],
        "14": [800, 6400],
        "15": [600, 4800],
        "16": [400, 3200],
        "17": [200, 1600],
        "18": [190, 1520],
        "19": [180, 1440],
        "20": [170, 1360],
        "21": [160, 1280],
        "22": [150, 1200],
        "23": [140, 1120],
        "24": [130, 1040],
        "25": [120, 960],
        "26": [110, 880],
        "27": [100, 800],
        "28": [90, 720],
        "29": [80, 640],
        "30": [70, 560],
        "31": [60, 480],
        "32": [50, 400],
        "33": [40, 320],
        "34": [30, 240],
        "35": [20, 160],
        "36": [18, 144],
        "37": [16, 128],
        "38": [14, 112],
        "39": [12, 96],
        "40": [10, 80]
    }

    ### C3000 error codes ###
    # Error codes are represented as bit masks for 4 right-most bits of status byte, according to C3000 manual, page 90
    ERROR_CODES = {
        0b0000: "No error.",
        0b0001: "Initialization failure!",
        0b0010: "Invalid command!",
        0b0011: "Invalid operand!",
        0b0100: "Invalid checksum!",
        0b0110: "EEPROM failure!",
        0b0111: "Device not initialized!",
        0b1000: "CAN bus failure!",
        0b1001: "Plunger overload!",
        0b1010: "Valve overload!",
        0b1011: "Plunger move not allowed! Check valve position.",
        0b1111: "Command overflow!"
    }

    ### C3000 DT protocol commands ###
    PREFIX = "/"
    SUFFIX = "\r\n"

    ## Execution flow control commands ##
    # Execute command string
    CMD_RUN = "R"
    # Repeat last command
    CMD_RPT_LAST = "X"
    # Store program string into EEPROM
    CMD_EEPROM_ST = "s"
    # Execute program string from EEPROM
    CMD_EEPROM_EXEC = "e"
    # Mark start of looped command sequence
    CMD_MARK_LOOP_START = "g"
    # Mark end of looped command sequence
    CMD_MARK_LOOP_END = "G"
    # Delay command execution
    CMD_DELAY_EXEC = "M"
    # Halt command execution (wait for R command and/or ext. input change)
    CMD_HALT = "H"
    # Terminate commands execution
    CMD_TERM = "T"
    
    ## Configuration commands ##
    # Set pump configuration (valve configuration, autorun, etc)
    SET_PUMP_CONF = "U"
    # Set system configuration (factory calibrations)
    SET_CALIB_CONF = "u"
    # Set internal position counter
    SET_POS_CTR = "z"
    # Set syringe gap volume
    SET_SYR_GAP = "R"
    # Set backlash increments
    SET_BACK_INC = "K"
    # Set acceleration/deceleration ramp slope
    SET_RAMP_SLOPE = "L"
    # Set start velocity (beginning of ramp)
    SET_START_VEL = "v"
    # Set maximum velocity (top of ramp) in increments/second
    SET_MAX_VEL = "V"
    # Set maximum velocity (top of ramp) with velocity code
    SET_MAX_VEL_CODE = "S"
    # Set cut-off velocity (end of ramp)
    SET_STOP_VEL = "c"
    # Set number of motor steps for cut-off
    SET_STOP_STEPS = "C"
    # Set resolution (stepping mode)
    SET_RES_MODE = "N"
    # Set external outputs
    SET_EXT_OUT = "J"
    # Set external outputs when syringe is at certain position
    SET_EXT_OUT_COND = "j"
    # Set motor hold current
    SET_MOT_HOLD = "h"
    # Set motor run current
    SET_MOT_RUN = "m"
    
    ## Report commands ##
    # Query pump status
    GET_STATUS = "?Q"
    # Query firmware version
    GET_FW_VER = "?20"
    # Query EEPROM data
    GET_EEPROM_DATA = "?27"
    # Query initialized status
    GET_INIT_STATUS = "?19"
    # Query plunger absolute position
    GET_SYR_POS = "?"
    # Query start velocity
    GET_START_VEL = "?1"
    # Query maximum velocity
    GET_MAX_VEL = "?2"
    # Query cut-off velocity
    GET_STOP_VEL = "?3"
    # Query acceleration/deceleration ramp
    GET_STEP_RAMP = "?7"
    # Query backlash increments setting
    GET_BACK_INC = "?12"
    # Query motor hold current
    GET_MOT_HOLD = "?25"
    # Query motor run current
    GET_MOT_RUN = "?26"
    # Query valve position
    GET_VLV_POS = "?6"

    ## Initialization commands ##
    # Initialize plunger & valves, valve numbering - CW from syringe (first on the left)
    # For non-distribution valves - set valve to the right
    INIT_ALL_CW = "Z"
    # Initialize plunger & valves, valve numbering - CCW from syringe (first on the right)
    # For non-distribution valves - set valve to the left
    INIT_ALL_CCW = "Y"
    # Initialize syringe only
    INIT_SYR = "W"
    # Initialize valve only
    INIT_VLV = "w"

    ## Plunger movement commands ##
    # Move plunger to absolute position
    SYR_POS_ABS = "A"
    # Move plunger to absolute position, do not set busy flag
    SYR_POS_ABS_NOBUSY = "a"
    # Relative pick-up
    SYR_SUCK_REL = "P"
    # Relative pick-up, do not set busy flag
    SYR_SUCK_REL_NOBUSY = "p"
    # Relative dispense
    SYR_SPIT_REL = "D"
    # Relative dispense, do not set busy flag
    SYR_SPIT_REL_NOBUSY = "d"

    ## Valve movement commands ##
    # Rotate valve CW to position <n>
    VLV_ROT_CW = "I"
    # Rotate valve CCW to position <n>
    VLV_ROT_CCW = "O"
