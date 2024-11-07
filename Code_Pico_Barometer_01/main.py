from machine import ADC, Pin, SPI
import framebuf
import math
import time
import utime

#########################################################        
################ waveshare screen driver ################
#########################################################

WF_PARTIAL_2IN13_V3= [
    0x0,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x80,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x14,0x0,0x0,0x0,0x0,0x0,0x0,  
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,
    0x22,0x17,0x41,0x00,0x32,0x36,
]

WS_20_30_2IN13_V3 = [ 
    0x80,0x4A,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x4A,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x80,0x4A,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x4A,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0xF,0x0,0x0,0x0,0x0,0x0,0x0,    
    0xF,0x0,0x0,0xF,0x0,0x0,0x2,    
    0xF,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,  
    0x22,0x17,0x41,0x0,0x32,0x36  
]

EPD_WIDTH       = 122
EPD_HEIGHT      = 250

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

class EPD_2in13_V3_Portrait(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        if EPD_WIDTH % 8 == 0:
            self.width = EPD_WIDTH
        else :
            self.width = (EPD_WIDTH // 8) * 8 + 8
        self.height = EPD_HEIGHT
        
        self.full_lut = WF_PARTIAL_2IN13_V3
        self.partial_lut = WS_20_30_2IN13_V3
        
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.init()
    
    '''
    function :Change the pin state
    parameter:
        pin : pin
        value : state
    '''
    def digital_write(self, pin, value):
        pin.value(value)

    '''
    function : Read the pin state 
    parameter:
        pin : pin
    '''
    def digital_read(self, pin):
        return pin.value()

    '''
    function : The time delay function
    parameter:
        delaytime : ms
    '''
    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)
        
    '''
    function : Write data to SPI
    parameter:
        data : data
    '''
    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    '''
    function :Hardware reset
    parameter:
    '''
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)   

    '''
    function :send command
    parameter:
     command : Command register
    '''
    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)
    
    '''
    function :send data
    parameter:
     data : Write data
    '''
    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)
    
    '''
    function :Wait until the busy_pin goes LOW
    parameter:
    '''
    def ReadBusy(self):
        print('busy')
        self.delay_ms(10)
        while(self.digital_read(self.busy_pin) == 1):      # 0: idle, 1: busy
            self.delay_ms(10)    
        print('busy release')
    
    '''
    function : Turn On Display
    parameter:
    '''
    def TurnOnDisplay(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20)  #  Activate Display Update Sequence    
        self.ReadBusy()
    
    '''
    function : Turn On Display Part
    parameter:
    '''
    def TurnOnDisplayPart(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0x0F)     # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20)  # Activate Display Update Sequence 
        self.ReadBusy()
    
    '''
    function : Set lut
    parameter:
        lut : lut data
    '''
    def LUT(self, lut):
        self.send_command(0x32)
        self.send_data1(lut[0:153])
        self.ReadBusy()
    
    '''
    function : Send lut data and configuration
    parameter:
        lut : lut data 
    '''
    def LUT_by_host(self, lut):
        self.LUT(lut)             # lut
        self.send_command(0x3F)
        self.send_data(lut[153])
        self.send_command(0x03)   # gate voltage
        self.send_data(lut[154])
        self.send_command(0x04)   # source voltage
        self.send_data(lut[155])  # VSH
        self.send_data(lut[156])  # VSH2
        self.send_data(lut[157])  # VSL
        self.send_command(0x2C)   # VCOM
        self.send_data(lut[158])
    
    '''
    function : Setting the display window
    parameter:
        Xstart : X-axis starting position
        Ystart : Y-axis starting position
        Xend : End position of X-axis
        Yend : End position of Y-axis
    '''
    def SetWindows(self, Xstart, Ystart, Xend, Yend):
        self.send_command(0x44)                #  SET_RAM_X_ADDRESS_START_END_POSITION
        self.send_data((Xstart >> 3) & 0xFF)
        self.send_data((Xend >> 3) & 0xFF)
        
        self.send_command(0x45)                #  SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(Ystart & 0xFF)
        self.send_data((Ystart >> 8) & 0xFF)
        self.send_data(Yend & 0xFF)
        self.send_data((Yend >> 8) & 0xFF)
        
    '''
    function : Set Cursor
    parameter:
        Xstart : X-axis starting position
        Ystart : Y-axis starting position
    '''
    def SetCursor(self, Xstart, Ystart):
        self.send_command(0x4E)             #  SET_RAM_X_ADDRESS_COUNTER
        self.send_data(Xstart & 0xFF)
        
        self.send_command(0x4F)             #  SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(Ystart & 0xFF)
        self.send_data((Ystart >> 8) & 0xFF)

    '''
    function : Initialize the e-Paper register
    parameter:
    '''
    def init(self):
        print('init')
        self.reset()
        self.delay_ms(100)
        
        self.ReadBusy()
        self.send_command(0x12)  # SWRESET
        self.ReadBusy()
        
        self.send_command(0x01)  # Driver output control 
        self.send_data(0xf9)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x11)  #data entry mode 
        self.send_data(0x03)
        
        self.SetWindows(0, 0, self.width-1, self.height-1)
        self.SetCursor(0, 0)
        
        self.send_command(0x3C)  # BorderWaveform
        self.send_data(0x05)
        
        self.send_command(0x21) # Display update control
        self.send_data(0x00)
        self.send_data(0x80)
        
        self.send_command(0x18) # Read built-in temperature sensor
        self.send_data(0x80)
        
        self.ReadBusy()
        self.LUT_by_host(self.partial_lut)
       
    '''
    function : Clear screen
    parameter:
    '''
    def Clear(self):
        self.send_command(0x24)
        self.send_data1([0xff] * self.height * int(self.width / 8))
                
        self.TurnOnDisplay()    
    
    '''
    function : Sends the image buffer in RAM to e-Paper and displays
    parameter:
        image : Image data
    '''
    def display(self, image):
        self.send_command(0x24)
        self.send_data1(image)
                
        self.TurnOnDisplay()
    
    '''
    function : Refresh a base image
    parameter:
        image : Image data
    '''
    def Display_Base(self, image):
        self.send_command(0x24)
        self.send_data1(image)
                
        self.send_command(0x26)
        self.send_data1(image)
                
        self.TurnOnDisplay()
        
    '''
    function : Sends the image buffer in RAM to e-Paper and partial refresh
    parameter:
        image : Image data
    '''    
    def display_Partial(self, image):
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(1)
        self.digital_write(self.reset_pin, 1)
        
        self.LUT_by_host(self.full_lut)
        
        self.send_command(0x37)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x40)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x3C)
        self.send_data(0x80)
        
        self.send_command(0x22)
        self.send_data(0xC0)
        self.send_command(0x20)
        self.ReadBusy()
        
        self.SetWindows(0,0,self.width-1,self.height-1)
        self.SetCursor(0,0)
        
        self.send_command(0x24)
        self.send_data1(image)

        self.TurnOnDisplayPart()
    
    '''
    function : Enter sleep mode
    parameter:
    '''
    def sleep(self):
        self.send_command(0x10) #enter deep sleep
        self.send_data(0x01)
        self.delay_ms(100)
        

class EPD_2in13_V3_Landscape(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        if EPD_WIDTH % 8 == 0:
            self.width = EPD_WIDTH
        else :
            self.width = (EPD_WIDTH // 8) * 8 + 8

        self.height = EPD_HEIGHT
        
        self.full_lut = WF_PARTIAL_2IN13_V3
        self.partial_lut = WS_20_30_2IN13_V3
        
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.height, self.width, framebuf.MONO_VLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        print('busy')
        self.delay_ms(10)
        while(self.digital_read(self.busy_pin) == 1):      # 0: idle, 1: busy
            self.delay_ms(10)    
        print('busy release')

    def TurnOnDisplay(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20)  #  Activate Display Update Sequence    
        self.ReadBusy()

    def TurnOnDisplayPart(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0x0F)     # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20)  # Activate Display Update Sequence 
        self.ReadBusy()

    def LUT(self, lut):
        self.send_command(0x32)
        self.send_data1(lut[0:153])
        self.ReadBusy()

    def LUT_by_host(self, lut):
        self.LUT(lut)             # lut
        self.send_command(0x3F)
        self.send_data(lut[153])
        self.send_command(0x03)   # gate voltage
        self.send_data(lut[154])
        self.send_command(0x04)   # source voltage
        self.send_data(lut[155])  # VSH
        self.send_data(lut[156])  # VSH2
        self.send_data(lut[157])  # VSL
        self.send_command(0x2C)   # VCOM
        self.send_data(lut[158])

    def SetWindows(self, Xstart, Ystart, Xend, Yend):
        self.send_command(0x44)                #  SET_RAM_X_ADDRESS_START_END_POSITION
        self.send_data((Xstart >> 3) & 0xFF)
        self.send_data((Xend >> 3) & 0xFF)
        
        self.send_command(0x45)                #  SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(Ystart & 0xFF)
        self.send_data((Ystart >> 8) & 0xFF)
        self.send_data(Yend & 0xFF)
        self.send_data((Yend >> 8) & 0xFF)

    def SetCursor(self, Xstart, Ystart):
        self.send_command(0x4E)             #  SET_RAM_X_ADDRESS_COUNTER
        self.send_data(Xstart & 0xFF)
        
        self.send_command(0x4F)             #  SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(Ystart & 0xFF)
        self.send_data((Ystart >> 8) & 0xFF)

    def init(self):
        print('init')
        self.reset()
        self.delay_ms(100)
        
        self.ReadBusy()
        self.send_command(0x12)  # SWRESET
        self.ReadBusy()
        
        self.send_command(0x01)  # Driver output control 
        self.send_data(0xf9)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x11)  #data entry mode 
        self.send_data(0x07)
        
        self.SetWindows(0, 0, self.width-1, self.height-1)
        self.SetCursor(0, 0)
        
        self.send_command(0x3C)  # BorderWaveform
        self.send_data(0x05)
        
        self.send_command(0x21) # Display update control
        self.send_data(0x00)
        self.send_data(0x80)
        
        self.send_command(0x18) # Read built-in temperature sensor
        self.send_data(0x80)
        
        self.ReadBusy()
        self.LUT_by_host(self.partial_lut)

    def Clear(self):
        self.send_command(0x24)
        self.send_data1([0xff] * self.height * int(self.width / 8))
                
        self.TurnOnDisplay()    

    def display(self, image):
        self.send_command(0x24)
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])

        self.TurnOnDisplay()

    def Display_Base(self, image):
        self.send_command(0x24)
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])
                
        self.send_command(0x26)
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])
                
        self.TurnOnDisplay()
        
    def display_Partial(self, image):
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(1)
        self.digital_write(self.reset_pin, 1)
        
        self.LUT_by_host(self.full_lut)
        
        self.send_command(0x37)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x40)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x3C)
        self.send_data(0x80)
        
        self.send_command(0x22)
        self.send_data(0xC0)
        self.send_command(0x20)
        self.ReadBusy()
        
        self.SetWindows(0,0,self.width-1,self.height-1)
        self.SetCursor(0,0)
        
        self.send_command(0x24)
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])
                
        self.TurnOnDisplayPart()
    
    def sleep(self):
        self.send_command(0x10) #enter deep sleep
        self.send_data(0x01)
        self.delay_ms(100)
              
###############################################################        
################ battery measurement functions ################
###############################################################

voltageInput = ADC(Pin(29)) # IMPORTANT! use ADC(Pin(29)) instead of ADC(29)
voltageConversionFactor = 3 * 3.3 / 65535
voltageFullBattery = 4.2
voltageEmptyBattery = 3.3

def GetBatteryPercentage():
    voltage = voltageInput.read_u16() * voltageConversionFactor
    batteryPercentage = 100 * ((voltage - voltageEmptyBattery) / (voltageFullBattery - voltageEmptyBattery))
    if batteryPercentage > 100:
        batteryPercentage = 100
    elif batteryPercentage < 0:
        batteryPercentage = 0
    return round(batteryPercentage)

batteryChargingPin = Pin(24, Pin.IN)

def GetBatteryChargingStatus():
    if batteryChargingPin.value() == 1:
        return True
    else:
        return False

##################################################################
################ temperature measurement functions ###############
##################################################################

temperatureInput = ADC(4)
temperatureConversionFactor = 3.3 / 65535

def GetTemperature():
    temperatureInVoltage = temperatureInput.read_u16() * temperatureConversionFactor
    temperature = 27 - (temperatureInVoltage - 0.706) / 0.001721
    return round(temperature, 1)
    
########################################################      
################ timer setter and getter ###############
########################################################

initialHour = 0
initialMinute = 0
initialSecond = 0
initialTimeStamp = time.time()

def SetTime(hour, minute, second):
    global initialHour, initialMinute, initialSecond
    initialHour = hour
    initialMinute = minute
    initialSecond = second

def GetTime():
    elapsedSeconds = time.time() - initialTimeStamp
    totalSeconds = initialHour * 3600 + initialMinute * 60 + initialSecond + int(elapsedSeconds)
    currentHours = (totalSeconds // 3600) % 24
    currentMinutes = (totalSeconds % 3600) // 60
    #currentSeconds = totalSeconds % 60
    return currentHours, currentMinutes

##########################################################      
################ draw components in buffer ###############
##########################################################

def DrawNumberSlot():
    # draw 1st number slot on screen
    epd.rect(10, 26, 10, 80, 0x00)
    epd.rect(10, 26, 50, 10, 0x00)
    epd.rect(10, 60, 50, 10, 0x00)
    epd.rect(10, 96, 50, 10, 0x00)
    epd.rect(30, 26, 10, 80, 0x00)
    epd.rect(50, 26, 10, 80, 0x00)
    epd.line(10, 26, 59, 105, 0x00)
    epd.line(10, 105, 59, 26, 0x00)

    # draw 2nd number slot on screen
    epd.rect(10 + 60, 26, 10, 80, 0x00)
    epd.rect(10 + 60, 26, 50, 10, 0x00)
    epd.rect(10 + 60, 60, 50, 10, 0x00)
    epd.rect(10 + 60, 96, 50, 10, 0x00)
    epd.rect(30 + 60, 26, 10, 80, 0x00)
    epd.rect(50 + 60, 26, 10, 80, 0x00)
    epd.line(10 + 60, 26, 59 + 60, 105, 0x00)
    epd.line(10 + 60, 105, 59 + 60, 26, 0x00)

    # draw 3rd number slot on screen
    epd.rect(10 + 120, 26, 10, 80, 0x00)
    epd.rect(10 + 120, 26, 50, 10, 0x00)
    epd.rect(10 + 120, 60, 50, 10, 0x00)
    epd.rect(10 + 120, 96, 50, 10, 0x00)
    epd.rect(30 + 120, 26, 10, 80, 0x00)
    epd.rect(50 + 120, 26, 10, 80, 0x00)
    epd.line(10 + 120, 26, 59 + 120, 105, 0x00)
    epd.line(10 + 120, 105, 59 + 120, 26, 0x00)

    # draw 4th number slot on screen
    epd.rect(10 + 180, 26, 10, 80, 0x00)
    epd.rect(10 + 180, 26, 50, 10, 0x00)
    epd.rect(10 + 180, 60, 50, 10, 0x00)
    epd.rect(10 + 180, 96, 50, 10, 0x00)
    epd.rect(30 + 180, 26, 10, 80, 0x00)
    epd.rect(50 + 180, 26, 10, 80, 0x00)
    epd.line(10 + 180, 26, 59 + 180, 105, 0x00)
    epd.line(10 + 180, 105, 59 + 180, 26, 0x00)

def DrawNumberOneInSlot(slot):
    xOffset = (slot - 1) * 60
    epd.fill_rect(30 + xOffset, 26, 10, 80, 0x00)
    epd.fill_rect(10 + xOffset, 26, 20, 10, 0x00)
    epd.fill_rect(10 + xOffset, 96, 50, 10, 0x00)
    
def DrawNumberTwoInSlot(slot):
    xOffset = (slot - 1) * 60
    epd.fill_rect(10 + xOffset, 26, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 60, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 96, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 70, 10, 26, 0x00)
    epd.fill_rect(50 + xOffset, 36, 10, 24, 0x00)
    
def DrawNumberThreeInSlot(slot):
    xOffset = (slot - 1) * 60
    epd.fill_rect(10 + xOffset, 26, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 60, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 96, 50, 10, 0x00)
    epd.fill_rect(50 + xOffset, 26, 10, 80, 0x00)
    
def DrawNumberFourInSlot(slot):
    xOffset = (slot - 1) * 60
    epd.fill_rect(10 + xOffset, 60, 50, 10, 0x00)
    epd.fill_rect(50 + xOffset, 26, 10, 80, 0x00)
    epd.fill_rect(10 + xOffset, 26, 10, 34, 0x00)
    
def DrawNumberFiveInSlot(slot):
    xOffset = (slot - 1) * 60
    epd.fill_rect(10 + xOffset, 26, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 60, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 96, 50, 10, 0x00)
    epd.fill_rect(50 + xOffset, 70, 10, 26, 0x00)
    epd.fill_rect(10 + xOffset, 36, 10, 24, 0x00)
    
def DrawNumberSixInSlot(slot):
    xOffset = (slot - 1) * 60
    epd.fill_rect(10 + xOffset, 26, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 60, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 96, 50, 10, 0x00)
    epd.fill_rect(50 + xOffset, 70, 10, 26, 0x00)
    epd.fill_rect(10 + xOffset, 26, 10, 80, 0x00)
    
def DrawNumberSevenInSlot(slot):
    xOffset = (slot - 1) * 60
    epd.fill_rect(10 + xOffset, 26, 50, 10, 0x00)
    epd.fill_rect(50 + xOffset, 26, 10, 80, 0x00)

def DrawNumberEightInSlot(slot):
    xOffset = (slot - 1) * 60
    epd.fill_rect(10 + xOffset, 26, 10, 80, 0x00)
    epd.fill_rect(10 + xOffset, 26, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 60, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 96, 50, 10, 0x00)
    epd.fill_rect(50 + xOffset, 26, 10, 80, 0x00)
    
def DrawNumberNineInSlot(slot):
    xOffset = (slot - 1) * 60
    epd.fill_rect(10 + xOffset, 26, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 60, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 96, 50, 10, 0x00)
    epd.fill_rect(50 + xOffset, 26, 10, 80, 0x00)
    epd.fill_rect(10 + xOffset, 36, 10, 24, 0x00)
    
def DrawNumberZeroInSlot(slot):
    xOffset = (slot - 1) * 60
    epd.fill_rect(10 + xOffset, 26, 10, 80, 0x00)
    epd.fill_rect(10 + xOffset, 26, 50, 10, 0x00)
    epd.fill_rect(10 + xOffset, 96, 50, 10, 0x00)
    epd.fill_rect(50 + xOffset, 26, 10, 80, 0x00)
    
def DrawNumber(firstNum, secondNum, thirdNum, forthNum):
    firstSlot = {
        1: lambda: DrawNumberOneInSlot(1),
        2: lambda: DrawNumberTwoInSlot(1),
        3: lambda: DrawNumberThreeInSlot(1),
        4: lambda: DrawNumberFourInSlot(1),
        5: lambda: DrawNumberFiveInSlot(1),
        6: lambda: DrawNumberSixInSlot(1),
        7: lambda: DrawNumberSevenInSlot(1),
        8: lambda: DrawNumberEightInSlot(1),
        9: lambda: DrawNumberNineInSlot(1),
        0: lambda: DrawNumberZeroInSlot(1),
    }
    secondSlot = {
        1: lambda: DrawNumberOneInSlot(2),
        2: lambda: DrawNumberTwoInSlot(2),
        3: lambda: DrawNumberThreeInSlot(2),
        4: lambda: DrawNumberFourInSlot(2),
        5: lambda: DrawNumberFiveInSlot(2),
        6: lambda: DrawNumberSixInSlot(2),
        7: lambda: DrawNumberSevenInSlot(2),
        8: lambda: DrawNumberEightInSlot(2),
        9: lambda: DrawNumberNineInSlot(2),
        0: lambda: DrawNumberZeroInSlot(2),
    }
    thirdSlot = {
        1: lambda: DrawNumberOneInSlot(3),
        2: lambda: DrawNumberTwoInSlot(3),
        3: lambda: DrawNumberThreeInSlot(3),
        4: lambda: DrawNumberFourInSlot(3),
        5: lambda: DrawNumberFiveInSlot(3),
        6: lambda: DrawNumberSixInSlot(3),
        7: lambda: DrawNumberSevenInSlot(3),
        8: lambda: DrawNumberEightInSlot(3),
        9: lambda: DrawNumberNineInSlot(3),
        0: lambda: DrawNumberZeroInSlot(3),
    }
    forthSlot = {
        1: lambda: DrawNumberOneInSlot(4),
        2: lambda: DrawNumberTwoInSlot(4),
        3: lambda: DrawNumberThreeInSlot(4),
        4: lambda: DrawNumberFourInSlot(4),
        5: lambda: DrawNumberFiveInSlot(4),
        6: lambda: DrawNumberSixInSlot(4),
        7: lambda: DrawNumberSevenInSlot(4),
        8: lambda: DrawNumberEightInSlot(4),
        9: lambda: DrawNumberNineInSlot(4),
        0: lambda: DrawNumberZeroInSlot(4),
    }
    draw = firstSlot.get(firstNum)
    draw() if draw else print("Invalid Number")
    draw = secondSlot.get(secondNum)
    draw() if draw else print("Invalid Number")
    draw = thirdSlot.get(thirdNum)
    draw() if draw else print("Invalid Number")
    draw = forthSlot.get(forthNum)
    draw() if draw else print("Invalid Number")
    
def DrawBatterySlot():
    epd.rect(219, 10, 5, 8, 0x00)
    epd.rect(224, 10, 5, 8, 0x00)
    epd.rect(229, 10, 5, 8, 0x00)
    epd.rect(234, 10, 5, 8, 0x00)
    epd.rect(218, 9, 22, 10, 0x00)
    epd.fill_rect(239, 11, 3, 6, 0x00)
    
def DrawBattery(number):
    if number >= 75:
        epd.fill_rect(219, 10, 5, 8, 0x00)
        epd.fill_rect(224, 10, 5, 8, 0x00)
        epd.fill_rect(229, 10, 5, 8, 0x00)
        epd.fill_rect(234, 10, 5, 8, 0x00)
    elif number >= 50 and number < 75:
        epd.fill_rect(219, 10, 5, 8, 0x00)
        epd.fill_rect(224, 10, 5, 8, 0x00)
        epd.fill_rect(229, 10, 5, 8, 0x00)
    elif number >= 25 and number < 50:
        epd.fill_rect(219, 10, 5, 8, 0x00)
        epd.fill_rect(224, 10, 5, 8, 0x00)
    elif number >= 1 and number < 25:
        epd.fill_rect(219, 10, 5, 8, 0x00)
    
def DrawBatteryPercentage(number):
    if number == 100:
        epd.text(str(number) + "%", 185, 11, 0x00)
    elif number >= 10 and number < 100:
        epd.text(" " + str(number) + "%", 185, 11, 0x00)
    else:
        epd.text("  " + str(number) + "%", 185, 11, 0x00)
    
def DrawBatteryCharging(status):
    if status:
        # draw a circle
        x = 174
        y = 14
        radius = 3
        verticalOffset = 0
        decision_over_2 = 1 - radius
        while verticalOffset <= radius:
            epd.pixel(x + radius, y + verticalOffset, 0x00)
            epd.pixel(x + verticalOffset, y + radius, 0x00)
            epd.pixel(x - radius, y + verticalOffset, 0x00)
            epd.pixel(x - verticalOffset, y + radius, 0x00)
            epd.pixel(x - radius, y - verticalOffset, 0x00)
            epd.pixel(x - verticalOffset, y - radius, 0x00)
            epd.pixel(x + radius, y - verticalOffset, 0x00)
            epd.pixel(x + verticalOffset, y - radius, 0x00)
            verticalOffset += 1
            if decision_over_2 <= 0:
                decision_over_2 += 2 * verticalOffset + 1
            else:
                radius -= 1
                decision_over_2 += 2 * (verticalOffset - radius) + 1
        # draw several lines
        epd.hline(166, 14, 6, 0x00)
        epd.vline(176, 12, 5, 0x00)
        epd.fill_rect(176, 11, 4, 2, 0x00)
        epd.fill_rect(176, 16, 4, 2, 0x00)

###################################################    
################ program main logic ###############
###################################################

# initialize the screen
epd = EPD_2in13_V3_Landscape()
epd.Clear()
epd.fill(0xff)
# set start time
SetTime(0,0,0)
# count screen refresh time
screenRefreshTime = 0

while True:
    # get current time
    currentHour, currentMinute = GetTime()
    currentHourFirstNum = currentHour // 10
    currentHourSecondNum = currentHour % 10
    currentMinuteFirstNum = currentMinute //10
    currentMinuteSecondNum = currentMinute % 10
    # draw time components in buffer
    DrawNumberSlot()
    DrawNumber(currentHourFirstNum,currentHourSecondNum,currentMinuteFirstNum,currentMinuteSecondNum)
    # get battery status
    batteryPercentage = GetBatteryPercentage()
    batteryCharging = GetBatteryChargingStatus()
    # draw battery components in buffer
    DrawBatterySlot()
    DrawBattery(batteryPercentage)
    DrawBatteryPercentage(batteryPercentage)
    DrawBatteryCharging(batteryCharging)
    # display all components in buffer on screen
    epd.display(epd.buffer)
    # put screen into sleep mode for 10min
    epd.sleep()
    time.sleep(600)
    epd.init()
    # clean the screen
    screenRefreshTime += 1
    epd.Clear() if screenRefreshTime % 20 == 0 else None
    epd.fill(0xff)
