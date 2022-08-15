from dataclasses import dataclass
from enum import auto
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


class AD9910_IO:
    def __init__(self, PWR: int, RST: int, OSK: int, IOP: int, PF0: int, PF1: int, PF2: int, mode=GPIO.BCM) -> None:
        GPIO.setmode(mode)
        GPIO.setwarnings(False)
        self.__DRG_init: bool = False
        self.__init_gpio(PWR=PWR, RST=RST, PF0=PF0, PF1=PF1, PF2=PF2, OSK=OSK, IOP=IOP)

    @classmethod
    def IO_init(cls, gpio: int, output: bool = True) -> None:
        if output:
            GPIO.setup(gpio, GPIO.OUT)
        else:
            GPIO.setup(gpio, GPIO.IN)

    @classmethod
    def IO_set(cls, gpio: int, state: bool = False) -> None:
        GPIO.output(gpio, state)

    @classmethod
    def IO_get(cls, gpio: int) -> bool:
        return GPIO.input(gpio)

    @classmethod
    def init_GIPO_out(cls, gpio: int, state=False) -> None:
        cls.IO_init(gpio=gpio, output=True)
        cls.IO_set(gpio=gpio, state=state)

    def clear(self) -> None:
        GPIO.cleanup()

    def __init_gpio(self, PWR: int, RST: int, OSK: int, IOP: int, PF0: int, PF1: int, PF2: int) -> None:
        self.__PWR = PWR
        self.__RST = RST
        self.__OSK = OSK
        self.__PF0 = PF0
        self.__PF1 = PF1
        self.__PF2 = PF2
        self.__IOP = IOP
        gpio_list = [self.__PWR, self.__RST, self.__OSK,  self.__IOP, self.__PF0, self.__PF1, self.__PF2]
        for gpio in gpio_list:
            self.init_GIPO_out(gpio, False)
        self.init_GIPO_out(self.__RST, True)
        sleep(0.005)
        self.IO_set(self.__RST, False)

    def DRG_config(self, DRC: int, DRH: int, DRO: int) -> None:
        self.__DRC = DRC
        self.__DRH = DRH
        self.__DRO = DRO
        gpio_list = [self.__DRC, self.__DRH]
        for gpio in gpio_list:
            self.init_GIPO_out(gpio, False)
        self.IO_init(gpio=self.__DRO, output=False)
        self.__DRG_init = True

    def update_signal(self) -> None:
        IOP = self.__IOP
        self.IO_set(IOP, True)
        sleep(0.001)
        self.IO_set(IOP, False)

    def __check_drg(self) -> None:
        if self.__DRG_init:
            return
        raise("DRG didn't configure!")

    def DRCTL(self, is_positive: bool = True) -> None:
        self.__check_drg()
        state = False
        if is_positive:
            state = True
        self.IO_set(gpio=self.__DRC, state=state)

    def DRHOLD(self, hold: bool = True) -> None:
        self.__check_drg()
        state = False
        if hold:
            state = True
        self.IO_set(gpio=self.__DRH, state=state)

    def DROVER(self) -> bool:
        self.__check_drg()
        return self.IO_get(gpio=self.__DRO)

    def OSK(self, positive: bool = True) -> None:
        self.IO_set(self.__OSK, positive)


class AD9910_COM:
    def __init__(self, dev: int = 0, bus: int = 0, spi_speed: Speed = Speed._3_9_MHz, threewire: int = True) -> None:
        self.spi = None
        self.__init_communication(dev=dev, bus=bus, spi_speed=spi_speed, threewire=threewire)

    def __init_communication(self, dev: int = 0, bus: int = 0, spi_speed: Speed = Speed._3_9_MHz, threewire: int = True):
        # self.spi = spi
        self.spi = spidev.SpiDev()
        self.spi.open(dev, bus)
        # self.spi.open(dev, bus)
        self.spi.max_speed_hz = spi_speed.value
        self.spi.threewire = True

    def send_data(self, data: List[int]) -> None:
        # for i in data:
        #     self.spi.writebytes([i])
        self.spi.writebytes(data)
        # self.spi.xfer(data)

    def read_data(self, size: int) -> List[int]:
        return self.spi.readbytes(size)


@dataclass
class PULSE:
    init_freq: float = 0.0
    end_freq: float = 0.0
    end_amp: float = 100.0
    dt_amp: float = 0.0002
    dt_freq: float = 0.0002
    step_amp: OSK_SS = OSK_SS.one
    step_freq: float = 0.0
    recover_freq: bool = False
    recover_amp: bool = True
    time_amp: float = 0
    time_freq: float = 0
    phase: float = 0

    def load_amp(self, data: List[float]) -> None:
        self.end_amp = data[1]
        self.step_amp = data[3]
        self.dt_amp = data[2]
        self.time_amp = data[5]

    def load_freq(self, data: List[float]) -> None:
        self.init_freq = data[0]
        self.end_freq = data[1]
        self.step_freq = data[3]
        self.dt_freq = data[2]
        self.time_freq = data[5]


class AD9910:
    def __init__(self, IO: AD9910_IO, COM: AD9910_COM = AD9910_COM()) -> None:
        self.__COM: AD9910_COM = COM
        self.__IO: AD9910_IO = IO
        self.__crf1 = CRF1()
        self.__crf2 = CRF2()
        self.__crf3 = CRF3()
        self.__SYSCLK = 1*G
        self.__single_tone: Profile_SingleTone = Profile_SingleTone(freq=0, amp=0, phase=0, SYSCLK=1*G)

    @property
    def IO(self) -> AD9910_IO:
        return self.__IO

    @property
    def COM(self) -> AD9910_COM:
        return self.__COM

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

    def send_data(self, data: List[int], update: bool = True) -> None:
        self.COM.send_data(data=data)
        if update:
            self.IO.update_signal()

    # CRF
    def crf_n_send(self, n: int = 1, update: bool = True) -> None:
        if n == 1:
            cmd = self.crf1
        elif n == 2:
            cmd = self.crf2
        else:
            cmd = self.crf3
        self.send_data(data=cmd.generate(), update=update)

    def crf1_send(self, update: bool = True) -> None:
        self.crf_n_send(n=1, update=update)

    def crf2_send(self, update: bool = True) -> None:
        self.crf_n_send(n=2, update=update)

    def crf3_send(self, update: bool = True) -> None:
        self.crf_n_send(n=3, update=update)

    def crf_all_send(self, update: bool = True) -> None:
        for i in range(3):
            self.crf_n_send(n=i+1, update=update)

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
        self.crf_all_send(update=True)

    # RAM
    def RAM_enable(self, enable: bool = True, update: bool = True) -> None:
        self.crf1.RAM_enable = enable
        self.crf1_send(update=update)

    # singel tone

    def set_amplitude(self, amp_100: float) -> float:
        self.single_tone.amp = amp_100
        self.send_data(self.single_tone.generate())
        return self.single_tone.amp

    def set_frequency(self, freq: float) -> float:
        self.single_tone.freq = freq
        self.send_data(self.single_tone.generate())
        return self.single_tone.freq

    def output_single_tone(self, freq: float, amp: float, phase: float = 0) -> float:
        self.single_tone.set_value(freq=freq, amp=amp, phase=phase)
        self.send_data(self.single_tone.generate())
        self.DRG_enable(False)
        self.RAM_enable(False)
        return self.single_tone.fpa

    # DRG

    def DRG_wait_finish(self, interval_ms: int = 0) -> None:
        time = interval_ms/1000
        while not self.IO.DROVER():
            sleep(time)

    def DRG_config(self, dest: DRD, auto_clear: bool = True, amp_from_pf: bool = True, update: bool = True) -> None:
        self.crf2.digital_ramp_destination = dest
        self.crf2.enable_amplitude_scale_from_single_tone_profiles = amp_from_pf
        self.crf1.autoclear_digital_ramp_accumulator = auto_clear
        self.crf1_send(update=update)
        self.crf2_send(update=update)

    def DRG_accumulatorlear(self) -> None:
        self.crf1.clear_digital_ramp_accumulator
        self.crf1_send()

    def DRG_dwell(self, dwell_high: bool = False, dwell_low: bool = True, update: bool = True):
        self.crf2.digital_ramp_no_dwell_high = dwell_high
        self.crf2.digital_ramp_no_dwell_low = dwell_low
        self.crf2_send(update=update)

    def DRG_enable(self, enable: bool = True, update: bool = True) -> None:
        self.crf2.digital_ramp_enable = enable
        self.crf2_send(update=update)

    def output_sweep(self, lower: float, upper: float, dt: float, dx: float, dest: DRD, output: bool = True) -> Tuple[float, float, float, float, float, float]:
        # return Tuple:lower,upper,dt,dx,speed(%/s),time(s)
        ramp_limit = DigitalRampLimit(lower=lower, upper=upper, dest=dest, SYSCLK=self.SYSCLK)
        step_size = DigitalRampStepSize(dx_dec=dx, dx_inc=dx, ramp_dest=dest, SYSCLK=self.SYSCLK)
        ramp_rate = DigitalRampRate(dt_negative=dt, dt_positive=dt, SYSCLK=self.SYSCLK)
        self.send_data(ramp_limit.generate())
        self.send_data(step_size.generate())
        self.send_data(ramp_rate.generate())
        self.DRG_config(dest=dest, auto_clear=True, update=False)
        self.DRG_enable(enable=True, update=output)
        lower = ramp_limit.lower
        upper = ramp_limit.upper
        dt = ramp_rate.negative
        dx = step_size.dec
        speed = step_size.dec/ramp_rate.negative
        time = (upper-lower)/speed
        return lower, upper, dt, dx, speed, time

    def output_sweep_freq(self, lower: float, upper: float, dt: float, df: float, output: bool = True) -> Tuple[float, float, float, float, float]:
        # return Tuple:freq_lower,freq_upper,dt,df,speed(Hz/s),time(s)
        return self.output_sweep(lower=lower, upper=upper, dt=dt, dx=df, dest=DRD.Frequency, output=output)

    def output_sweep_amp(self, lower: float, upper: float, dt: float, da: float, output: bool = True) -> Tuple[float, float, float, float, float]:
        # return Tuple:amp_lower,amp_upper,dt,d_amp(%),speed(%/s),time(s)
        return self.output_sweep(lower=lower, upper=upper, dt=dt, dx=da, dest=DRD.Amplitude, output=output)

    def out_sweep_ctl(self, lower: float, upper: float, dt: float, dx: float, dest: DRD, output: bool = True, pos_ctl: bool = True) -> Tuple[float, float, float, float, float, float]:
        # return Tuple:lower,upper,dt,dx,speed(%/s),time(s)
        info = self.output_sweep(lower=lower, upper=upper, dt=dt, dx=dx, dest=dest, output=False)
        self.IO.DRCTL(pos_ctl)
        self.IO.update_signal()
        return info

    def output_sweep_ctl_freq(self, lower: float, upper: float, dt: float, df: float, pos_ctl: bool = True) -> Tuple[float, float, float, float, float]:
        # return Tuple:freq_lower,freq_upper,dt,df,speed(Hz/s),time(s)
        return self.out_sweep_ctl(lower=lower, upper=upper, dt=dt, dx=df, dest=DRD.Frequency, pos_ctl=pos_ctl)

    def output_sweep_ctl_amp(self, lower: float, upper: float, dt: float, da: float, pos_ctl: bool = True) -> Tuple[float, float, float, float, float]:
        # return Tuple:amp_lower,amp_upper,dt,d_amp(%),speed(%/s),time(s)
        return self.out_sweep_ctl(lower=lower, upper=upper, dt=dt, dx=da, dest=DRD.Amplitude, pos_ctl=pos_ctl)

    # def pulse_trapezoid(self, pulse: PULSE) -> PULSE:
    #     dt = pulse.dt
    #     freq_first_is_pos: bool = pulse.end_freq > pulse.init_freq
    #     self.output_single_tone(freq=pulse.init_freq, amp=pulse.init_amp, phase=0)
    #     amp_info = self.output_sweep_ctl_amp(lower=pulse.init_amp, upper=pulse.end_amp, dt=dt, da=pulse.step_amp, pos_ctl=True)
    #     pulse.add_amp(amp_info)
    #     self.DRG_wait_finish(0)
    #     self.IO.DRHOLD(True)
    #     # self.IO.DRCTL(False)
    #     # self.output_single_tone(freq=pulse.init_freq, amp=pulse.end_amp, phase=0)
    #     self.set_amplitude(pulse.end_amp)
    #     self.IO.DRHOLD(False)
    #     freq_info = self.output_sweep_ctl_freq(lower=pulse.init_freq, upper=pulse.end_freq, dt=dt, df=pulse.step_freq, pos_ctl=freq_first_is_pos)
    #     pulse.add_freq(freq_info)
    #     self.DRG_wait_finish(0)
    #     self.IO.DRHOLD(True)
    #     self.IO.DRCTL(True)
    #     self.set_frequency(pulse.end_freq)
    #     if pulse.recover_amp:
    #         self.output_sweep_ctl_amp(lower=pulse.init_amp, upper=pulse.end_amp, dt=dt, da=pulse.step_amp, pos_ctl=False)
    #         self.IO.DRHOLD(False)
    #         self.DRG_wait_finish(0)
    #         self.IO.DRHOLD(True)
    #         self.IO.DRCTL(False)
    #         self.set_amplitude(pulse.init_amp)
    #     # if pulse.recover_freq:
    #     #     self.output_sweep_ctl_freq(lower=pulse.init_freq, upper=pulse.end_freq, dt=dt, df=pulse.step_freq, pos_ctl=not freq_first_is_pos)
    #     return pulse

    def OSK_enable(self, enable: bool = True, update: bool = True) -> None:
        self.crf1.OSK_enable = enable
        self.crf1.load_ARR_IO_update = False
        self.crf1.select_auto_OSK = True
        self.crf1.manual_OSK_externa = True
        self.crf1_send(update=update)

    def output_sweep_amp_osk(self, max: float, dt: float, step_size: OSK_SS = OSK_SS.one) -> Tuple[float, float, float, float, float]:
        # return Tuple:amp_lower,amp_upper,dt,d_amp(%),speed(%/s),time(s)
        asf = ASF(amp_100=max, dt=dt, SYSCLK=self.SYSCLK, step_size=step_size)
        self.send_data(data=asf.generate(), update=True)
        self.OSK_enable()
        self.IO.OSK(positive=True)
        return 0, asf.amp, asf.dt, asf.step_size.value*100/0x3FFF, 100/asf.time, asf.time

    def pulse_trapezoid(self, pulse: PULSE) -> PULSE:

        self.DRG_dwell(dwell_high=False, dwell_low=False, update=False)
        fpa = self.output_single_tone(freq=pulse.init_freq, amp=0, phase=pulse.phase)
        fpa = [round(i, 3) for i in fpa]
        print("freq={f}Hz\tphase={p}pi\tamplitude={a}%".format(f=fpa[0], p=round(fpa[1]/pi, 4), a=fpa[2]))
        osk_info = self.output_sweep_amp_osk(max=100, dt=pulse.dt_amp)
        dt = round(osk_info[2]/u, 3)
        time = round(osk_info[5]/1, 3)
        osk_info = [round(i, 3) for i in osk_info]
        print("lower={l}%\tupper={u}%\tdt={t}us\td_amp={d}%\tspeed={s}%/s\ttime={time}s"
              .format(l=osk_info[0], u=osk_info[1], t=dt, d=osk_info[3], s=osk_info[4], time=time))
        sleep(time)

        sweep_info = self.output_sweep_ctl_freq(lower=pulse.init_freq, upper=pulse.end_freq, dt=pulse.dt_freq, df=pulse.step_freq)
        dt = round(sweep_info[2]/u, 3)
        sweep_info = [round(i, 3) for i in sweep_info]
        print("lower={l}Hz\tupper={u}Hz\tdt={t}us\tdf={d}Hz\tspeed={s}Hz/s\ttime={time}s"
              .format(l=sweep_info[0], u=sweep_info[1], t=dt, d=sweep_info[3], s=sweep_info[4], time=sweep_info[5]))
        self.DRG_wait_finish()

        self.IO.OSK(False)
        sleep(time)
        pulse.load_amp(osk_info)
        pulse.load_freq(sweep_info)
        return pulse
