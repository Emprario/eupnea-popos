from functions import *


def config(de_name: str, distro_version: str, username: str, root_partuuid: str, verbose: bool) -> None:
    set_verbose(verbose)
    print_status("Configuring Manjaro")

    # Apply temporary fix for pacman
    bash("mount --bind /mnt/depthboot /mnt/depthboot")
    with open("/mnt/depthboot/etc/pacman.conf", "r") as conf:
        temp_pacman = conf.readlines()
    # temporarily comment out CheckSpace, coz Pacman fails to check available storage space when run from a chroot
    temp_pacman[34] = f"#{temp_pacman[34]}"
    with open("/mnt/depthboot/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)

    print_status("Preparing pacman")
    chroot("pacman-key --init")
    chroot("pacman-key --populate archlinux manjaro")
    chroot("pacman -Syy --noconfirm")
    chroot("pacman -Syu --noconfirm")

    print_status("Installing packages")
    start_progress()  # start fake progress
    chroot("pacman -S --noconfirm nano networkmanager xkeyboard-config linux-firmware cloud-utils "
           "dmidecode")
    stop_progress()  # stop fake progress

    print_status("Extracting and installing de, might take a while")
    start_progress()  # start fake progress
    match de_name:
        case "gnome":
            print_status("Installing GNOME")
            bash("unsquashfs -d /mnt/depthboot /tmp/depthboot-build/cdrom/manjaro/x86_64/desktopfs.sfs")
            chroot("pacman -S --noconfirm gnome-initial-setup")
            chroot("systemctl enable gdm.service")
        case "kde":
            print_status("Installing KDE")
            bash("unsquashfs -d /mnt/depthboot /tmp/depthboot-build/cdrom/manjaro/x86_64/desktopfs.sfs")
            chroot("systemctl enable sddm.service")
        case "mate": # should be tested
            print_status("Installing MATE")
            bash("unsquashfs -d /mnt/depthboot /tmp/depthboot-build/cdrom/manjaro/x86_64/desktopfs.sfs")
            chroot("systemctl enable lightdm.service")
        case "xfce":
            print_status("Installing Xfce")
            bash("unsquashfs -d /mnt/depthboot /tmp/depthboot-build/cdrom/manjaro/x86_64/desktopfs.sfs")
            chroot("systemctl enable lightdm.service")
        case "budgie": # should be tested
            print_status("Installing Budgie")
            bash("unsquashfs -d /mnt/depthboot /tmp/depthboot-build/cdrom/manjaro/x86_64/desktopfs.sfs""")
            chroot("systemctl enable lightdm.service")
        case "cli": # shouldn't work
            print_status("Skipping desktop environment install")
        # TODO: add more DE support
        case _:
            print_error("Invalid desktop environment! Please create an issue")
            exit(1)

    stop_progress()  # stop fake progress
    print_status("Desktop environment setup complete")

    # enable networkmanager systemd service
    chroot("systemctl enable NetworkManager.service")

    # Configure sudo
    with open("/mnt/depthboot/etc/sudoers", "r") as conf:
        temp_sudoers = conf.readlines()
    # uncomment wheel group
    temp_sudoers[84] = temp_sudoers[84][2:]
    with open("/mnt/depthboot/etc/sudoers", "w") as conf:
        conf.writelines(temp_sudoers)

    print_status("Restoring pacman config")
    with open("/mnt/depthboot/etc/pacman.conf", "r") as conf:
        temp_pacman = conf.readlines()
    # comment out CheckSpace
    temp_pacman[34] = temp_pacman[34][1:]
    with open("/mnt/depthboot/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)

    # TODO: add depthboot to arch name
    # Add depthboot to version(this is purely cosmetic)
    with open("/mnt/depthboot/etc/os-release", "r") as f:
        os_release = f.readlines()
    os_release[0] = os_release[0][:-2] + ' (Depthboot)"\n'
    os_release[1] = os_release[1][:-2] + ' (Depthboot)"\n'
    with open("/mnt/depthboot/etc/os-release", "w") as f:
        f.writelines(os_release)

    print_status("Manjaro configuration complete")


# using arch-chroot for manjaro
def chroot(command: str):
    if verbose:
        bash(f'arch-chroot /mnt/depthboot zsh -c "{command}"')
    else:
        bash(f'arch-chroot /mnt/depthboot zsh -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output
