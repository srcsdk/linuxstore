#!/bin/bash
# install arch packages

packages=(
    firefox
    vlc
    libreoffice
    terminator
    htop
    thunar
    scrot
    gimp
    audacity
    transmission-gtk
    pidgin
    hexchat
    bleachbit
    gparted
    filezilla
    wireshark-qt
    nmap
    aircrack-ng
    john
    hydra
    virtualbox
    qemu
    vagrant
    neofetch
    screenfetch
    tor-browser
    openvpn
    macchanger
    proxychains-ng
    hashcat
    cmatrix
    cowsay
    figlet
    lolcat
    sl
    tmux
    ranger
    mc
    ncdu
    iotop
    lsof
    strace
    ettercap
    metasploit
    nikto
    sqlmap
    tcpdump
    netcat
    curl
    wget
    git
    openssh
    rsync
    tree
    the_silver_searcher
    rxvt-unicode
    zsh
    vim
    emacs
    python
    ruby
    gcc
    make
    cmake
    nodejs
    npm
    docker
    keepassxc
    clamav
    rkhunter
    lynis
)

echo "installing ${#packages[@]} packages..."

for pkg in "${packages[@]}"; do
    if ! pacman -Qi "$pkg" &>/dev/null; then
        echo "installing $pkg..."
        sudo pacman -S --noconfirm "$pkg" 2>/dev/null || echo "  not found in repos: $pkg"
    else
        echo "already installed: $pkg"
    fi
done

echo "done"
