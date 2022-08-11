from AD9910_CMD import *
from time import sleep
import spidev
import RPi.GPIO as GPIO


@unique
class Speed(Enum):
    _125_0_MHz = 125000000
    _62_5_MHz = 62500000
    _31_2_MHz = 31200000
    _15_6_MHz = 15600000
    _7_8_MHz = 7800000
    _3_9_MHz = 3900000
    _1953_kHz = 1953000
    _976_kHz = 976000
    _488_kHz = 488000
    _244_kHz = 244000
    _122_kHz = 122000
    _61_kHz = 61000
    _30_5_kHz = 30500
    _15_2_kHz = 15200
    _7629_Hz = 7629


def init_GIPO_out(gpio: int, state=False) -> None:
    GPIO.setup(gpio, GPIO.OUT)
    GPIO.output(gpio, state)


class AD9910:
    def __init__(self, PWR: int, RST: int, OSK: int, IO_update: int, PF0: int, PF1: int, PF2: int, dev: int = 0, bus: int = 0, spi_speed: Speed = Speed._3_9_MHz, threewire: int = True) -> None:
        self.__init_comunication(dev=dev, bus=bus, spi_speed=spi_speed, threewire=threewire)
        self.__init_gpio(PWR=PWR, RST=RST, PF0=PF0, PF1=PF1, PF2=PF2, OSK=OSK, IO_update=IO_update)
        self.__crf1 = CRF1()
        self.__crf2 = CRF2()
        self.__crf3 = CRF3()

    @property
    def crf1(self) -> CRF1:
        return self.__crf1

    @property
    def crf2(self) -> CRF2:
        return self.__crf2

    @property
    def crf3(self) -> CRF3:
        return self.__crf3

    def __init_comunication(self, dev: int = 0, bus: int = 0, spi_speed: Speed = Speed._3_9_MHz, threewire: int = True):
        # self.spi = spi
        self.spi = spidev.SpiDev()
        self.spi.open(dev, bus)
        # self.spi.open(dev, bus)
        self.spi.max_speed_hz = spi_speed.value
        self.spi.threewire = True

    def __init_gpio(self, PWR: int, RST: int, OSK: int, IO_update: int, PF0: int, PF1: int, PF2: int) -> None:
        self.PWR = PWR
        self.RST = RST
        self.OSK = OSK
        # self.DRG = DRG
        self.PF0 = PF0
        self.PF1 = PF1
        self.PF2 = PF2
        self.IO_update = IO_update
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        gpio_list = [self.PWR, self.OSK,  self.IO_update, self.PF0, self.PF1, self.PF2]
        for gpio in gpio_list:
            init_GIPO_out(gpio, False)
        init_GIPO_out(self.RST, True)
        sleep(0.005)
        GPIO.output(self.RST, False)

    def crf_init(self) -> None:
        # self.crf1.RAM_enable = True
        self.crf1.inverse_sinc_filter = True
        self.crf2.enable_amplitude_scale_from_single_tone_profiles = True
        self.crf2.SYNC_CLK_enable = False
        self.crf3.DRV0 = DRV0.disable
        self.crf3.VCO_SEL = VCO._920_1030_MHZ
        self.crf3.I_cp = PLL_CPC._237_uA
        self.crf3.PLL_enable = True
        self.crf3.REFCLK_input_divider_ResetB = True
        self.crf3.N = 25
        self.send_data(self.crf1.generate())
        self.send_data(self.crf2.generate())
        self.send_data(self.crf3.generate())

    def update(self) -> None:
        GPIO.output(self.IO_update, True)
        sleep(0.001)
        GPIO.output(self.IO_update, False)

    def send_data(self, data: List[int]) -> None:
        # for i in data:
        #     self.spi.writebytes([i])
        self.spi.writebytes(data)
        # self.spi.xfer(data)
        self.update()

    def clear(self) -> None:
        GPIO.cleanup()

    def enable_singel_tone(self) -> None:
        self.crf1.RAM_enable = False
        self.crf2.digital_ramp_enable = False
        self.send_data(self.crf1.generate())
        self.send_data(self.crf2.generate())

    def output_sigel_tone(self, freq: float, amp: float, phase: float = 0) -> float:
        pf0 = Profile_SingleTone(freq=freq, amp=amp, phase=phase)
        self.send_data(pf0.generate())
        self.enable_singel_tone()
        return pf0.fpa
