from os import getcwd, geteuid, system
from sys import argv
from os.path import isdir, isfile


class Setup(object):
    SCRIPT = "carpi.py"
    HEADLESS_AUTOSTART_PATH = "/etc/rc.local"
    AUTOSTART_PATH = "/home/pi/.config/lxsession/LXDE-pi/autostart"

    @staticmethod
    def read_autostart_file():
        with open(Setup.AUTOSTART_PATH) as o:
            return o.readlines()

    @staticmethod
    def already_autostart_installed():
        for l in Setup.read_autostart_file():
            if l.endswith(Setup.SCRIPT):
                return True
        return False

    @staticmethod
    def _install_autostart():
        print("installing to autostart")
        with open(Setup.AUTOSTART_PATH, 'a') as o:
            # o.write("@lxterminal -e cd " + getcwd() + "/; git pull")
            o.write("@lxterminal -e /usr/bin/sudo /usr/bin/python3 " + getcwd() + "/" + Setup.SCRIPT)
        return True

    @staticmethod
    def install_autostart():
        if Setup.already_autostart_installed():
            print("autostart already installed")
            return True
        Setup._install_autostart()

    @staticmethod
    def _uninstall_autostart():
        print("uninstalling autostart")
        _o = Setup.read_autostart_file()
        with open(Setup.AUTOSTART_PATH, 'w') as o:
            for l in _o:
                if Setup.SCRIPT not in l:
                    o.write(l + "\n")

    @staticmethod
    def uninstall_autostart():
        if not Setup.already_autostart_installed():
            print("autostart already not enabled")
            return True
        Setup._uninstall_autostart()

    @staticmethod
    def install_dependencies():
        system("sudo apt install python3 python3-dev python3-pip gpsd gpsd-clients libjpeg-dev libtiff-dev sox "
               "xserver-xorg-input-evdev libsndfile-dev tcpdump build-essential swig git libpulse-dev libasound2-dev "
               "portaudio19-dev libsox-fmt-mp3 ffmpeg libboost-python-dev -y")
        system("pip3 install -r requirements.txt")
        if not isdir("/opt/PiFmRds"):
            system("cd /opt ; git clone https://github.com/ChristopheJacquet/PiFmRds")
        if not isfile("/opt/PiFmRds/src/pi_fm_rds"):
            system("cd /opt/PiFmRds/src ; make clean ; make")

    @staticmethod
    def install_display_driver():
        system("cp display_configs/vertical.conf /usr/share/X11/xorg.conf.d/99_touchscreen.conf")
        with open("/boot/config.txt", "a") as o:
            print("opened /boot/config.txt")
            if "display_rotate=1" not in o.read():
                o.write("\ndisplay_rotate=1\n")
                print("wrote display_rotate=1 into /boot/config.txt")
        system("cd /tmp ; wget http://osoyoo.com/driver/LCD_show_35hdmi.tar.gz ; tar xf LCD_show_35hdmi.tar.gz ; "
               "rm LCD_show_35hdmi.tar.gz ; cd LCD_show_35hdmi/ ; sudo ./LCD35_480\*320")

    @staticmethod
    def install_submodules():
        system("git submodule update --init")
        system("cd pybt ; ./dependencies.sh ; pip3 install -r requirements.txt")

    @staticmethod
    def help():
        print("usage: python3 carpi.py {arguments}")
        print("{arguments}:")
        print("\t-ia\t--install-autostart")
        print("\t-ua\t--uninstall-autostart")
        print("\t-deps\t--install-dependencies")
        print("\t-subs\t--install-submodules")
        print("\t-dd\t--install-display-driver")
        print("\t-a\t--all")
        exit()

    @staticmethod
    def parse_arguments(arguments):
        i = 1
        print("parsing args")
        while i < len(arguments):
            a = arguments[i]
            if a in ["-ia", "--install-autostart"]:
                should_not_be_root()
                Setup.install_autostart()
            elif a in ["-ua", "--uninstall-autostart"]:
                should_not_be_root()
                Setup.uninstall_autostart()
            elif a in ["-deps", "--install-dependencies"]:
                should_be_root()
                Setup.install_dependencies()
            elif a in ["-subs", "--install-submodules"]:
                should_be_root()
                Setup.install_submodules()
            elif a in ["-dd", "--install-display-driver"]:
                should_be_root()
                Setup.install_display_driver()
            elif a in ["-a", "--all"]:
                should_be_root()
                Setup.install_dependencies()
                Setup.install_submodules()
                Setup.install_display_driver()
            else:
                Setup.help()
            i += 1


def should_not_be_root():
    if geteuid() == 0:
        print("should not modify", Setup.AUTOSTART_PATH, "with root permissions")
        exit()


def should_be_root():
    if geteuid() != 0:
        print("need root for apt calls")
        exit()


if __name__ == '__main__':

    Setup.parse_arguments(argv)
