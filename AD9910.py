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
        self.__init_communication(dev=dev, bus=bus, spi_speed=spi_speed, threewire=threewire)
        self.__init_gpio(PWR=PWR, RST=RST, PF0=PF0, PF1=PF1, PF2=PF2, OSK=OSK, IO_update=IO_update)
        self.__crf1 = CRF1()
        self.__crf2 = CRF2()
        self.__crf3 = CRF3()
        self.__SYSCLK = 1*G

    @property
    def SYSCLK(self) -> int:
        return self.__SYSCLK

    @property
    def crf1(self) -> CRF1:
        return self.__crf1

    @property
    def crf2(self) -> CRF2:
        return self.__crf2

    @property
    def crf3(self) -> CRF3:
        return self.__crf3

    def __init_communication(self, dev: int = 0, bus: int = 0, spi_speed: Speed = Speed._3_9_MHz, threewire: int = True):
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
        self.__SYSCLK = 1*G
        self.__single_tone: Profile_SingleTone = Profile_SingleTone(freq=0, phase=0, amp=100,N=0, SYSCLK=self.SYSCLK)

    @property
    def SYSCLK(self) -> int:
        return self.__SYSCLK

    @SYSCLK.setter
    def SYSCLK(self, SLSCLK: int) -> None:
        self.__SYSCLK = SLSCLK
        self.single_tone.SYSCLK = SLSCLK

    @property
    def single_tone(self) -> Profile_SingleTone:
        return self.__single_tone

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
        self.SYSCLK = self.crf3.N*40*M
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

    def enable_RAM_DRG(self, RAM: bool, DRG: bool) -> None:
        self.crf1.RAM_enable = RAM
        self.crf2.digital_ramp_enable = DRG
        self.send_data(self.crf1.generate())
        self.send_data(self.crf2.generate())

    def enable_single_tone(self) -> None:
        self.enable_RAM_DRG(RAM=False, DRG=False)

    def enable_DRG(self, dest: DRD) -> None:
        self.crf2.digital_ramp_destination = dest
        self.crf2.digital_ramp_no_dwell_high = True
        self.crf2.digital_ramp_no_dwell_low = True
        self.crf1.autoclear_phase_accumulator = True
        self.enable_RAM_DRG(RAM=False, DRG=True)

    def enable_RAM(self) -> None:
        self.enable_RAM_DRG(RAM=True, DRG=False)

    def set_amplitute(self, amp_100) -> float:
        self.single_tone.amp = amp_100
        self.send_data(self.single_tone.generate())
        return self.single_tone.amp

    def output_single_tone(self, freq: float, amp: float, phase: float = 0) -> float:
        self.single_tone.set_value(freq=freq, amp=amp, phase=phase)
        self.send_data(self.single_tone.generate())
        self.enable_single_tone()
        return self.single_tone.fpa

    def output_sweep_freq(self, lower: float, upper: float, dt: float, df: float)->Tuple[float,float,float,float,float]:
        # return Tuple:freq_lower,freq_upper,dt,df,speed(Hz/s)
        ramp_limit = DigitalRampLimit(freq_lower=lower, freq_upper=upper, SYSCLK=self.SYSCLK)
        step_size = DigitalRampStepSize(dx_dec=df, dx_inc=df, ramp_dest=DRD.Frequency, SYSCLK=self.SYSCLK)
        ramp_rate = DigitalRampRate(dt_negative=dt, dt_positive=dt, SYSCLK=self.SYSCLK)
        self.send_data(ramp_limit.generate())
        self.send_data(step_size.generate())
        self.send_data(ramp_rate.generate())
        self.enable_DRG(dest=DRD.Frequency)
        return ramp_limit.freq_lower, ramp_limit.freq_upper, ramp_rate.negative, step_size.dec,step_size.dec/ramp_rate.negative
