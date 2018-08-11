#!/bin/bash
# install packages - base + security + wireless

base_packages=(
    firefox vlc libreoffice terminator htop thunar scrot gimp audacity
    transmission-gtk bleachbit gparted filezilla tmux ranger mc ncdu
    iotop lsof strace rxvt-unicode zsh vim neofetch curl wget git
    openssh rsync tree the_silver_searcher python ruby gcc make cmake
    nodejs npm docker keepassxc
)

security_packages=(
    nmap wireshark-qt tcpdump netcat aircrack-ng ettercap nikto sqlmap
    john hydra hashcat metasploit proxychains-ng macchanger tor-browser
    openvpn clamav rkhunter lynis burpsuite wpscan gobuster dirb
    enum4linux smbclient nbtscan dnsenum dnsrecon fierce recon-ng
    theharvester maltego beef-xss zaproxy mitmproxy responder
    impacket crackmapexec bloodhound
)

wireless_packages=(
    aircrack-ng
    wifite
    reaver
    bully
    pixiewps
    hostapd
    dnsmasq
    create_ap
    iw
    wireless_tools
    wpa_supplicant
    macchanger
    kismet
    horst
)

install_packages() {
    local name="$1"
    shift
    local pkgs=("$@")
    local installed=0
    local skipped=0
    echo "=== $name (${#pkgs[@]} packages) ==="
    for pkg in "${pkgs[@]}"; do
        if pacman -Qi "$pkg" &>/dev/null; then
            installed=$((installed + 1))
            continue
        fi
        sudo pacman -S --noconfirm "$pkg" 2>/dev/null
        if [ $? -ne 0 ]; then
            yay -S --noconfirm "$pkg" 2>/dev/null
            if [ $? -ne 0 ]; then
                echo "  skip: $pkg"
                skipped=$((skipped + 1))
                continue
            fi
        fi
        installed=$((installed + 1))
    done
    echo "  $installed installed, $skipped skipped"
    echo ""
}

echo "arch package installer"
echo ""

install_packages "base" "${base_packages[@]}"
install_packages "security" "${security_packages[@]}"
install_packages "wireless" "${wireless_packages[@]}"

echo "done"
