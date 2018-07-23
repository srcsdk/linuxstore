#!/bin/bash
# install packages - base system + security tools

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
    openvpn clamav rkhunter lynis
    burpsuite
    wpscan
    gobuster
    dirb
    enum4linux
    smbclient
    nbtscan
    dnsenum
    dnsrecon
    fierce
    recon-ng
    theharvester
    maltego
    beef-xss
    zaproxy
    mitmproxy
    responder
    impacket
    crackmapexec
    bloodhound
)

install_packages() {
    local name="$1"
    shift
    local pkgs=("$@")
    echo "=== $name (${#pkgs[@]} packages) ==="
    for pkg in "${pkgs[@]}"; do
        if ! pacman -Qi "$pkg" &>/dev/null; then
            sudo pacman -S --noconfirm "$pkg" 2>/dev/null
            if [ $? -ne 0 ]; then
                yay -S --noconfirm "$pkg" 2>/dev/null || echo "  skip: $pkg"
            fi
        fi
    done
    echo ""
}

install_packages "base" "${base_packages[@]}"
install_packages "security" "${security_packages[@]}"

echo "done"
