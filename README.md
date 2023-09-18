# Raspberry Pi NixOS Configuration

## flake.nix
```
{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    rpiclock.url = "github:mfenniak/rpiclock";
    nixos-hardware.url = "github:NixOS/nixos-hardware";
  };

  outputs = { self, nixpkgs, nixos-hardware, rpiclock, ... }: {
    nixosConfigurations.nixclock = nixpkgs.lib.nixosSystem rec {
      system = "aarch64-linux";
      modules = [
        ./nixclock.nix
        nixos-hardware.nixosModules.raspberry-pi-4
        { nixpkgs.overlays = [ rpiclock.overlays.${system}.default ]; }
      ];
    };
  };
}
```

## nixclock.nix

```
{ config, pkgs, lib, ... }:

{
  boot = {
    kernelPackages = pkgs.linuxKernel.packages.linux_rpi4;
    initrd.availableKernelModules = [ "xhci_pci" "usbhid" "usb_storage" ];
    loader = {
      grub.enable = false;
      generic-extlinux-compatible.enable = true;
    };

    kernelParams = [
      # per https://github.com/hzeller/rpi-rgb-led-matrix#cpu-use...
      "isolcpus=3"
      # https://github.com/NixOS/nixpkgs/issues/122993
      "iomem=relaxed"
      "strict-devmem=0"
    ];

    blacklistedKernelModules = [
      # disable snd module: https://github.com/hzeller/rpi-rgb-led-matrix#use-minimal-raspbian-distribution
      "snd_bcm2835"
    ];
  };

  fileSystems = {
    "/" = {
      device = "/dev/disk/by-label/NIXOS_SD";
      fsType = "ext4";
      options = [ "noatime" ];
    };
  };

  networking = {
    hostName = "nixclock";
    wireless = {
      enable = true;
      networks."...yourSID...".psk = "...yourPSK..."; # FIXME: there's probably a better way than hardcoding a pwd here
      interfaces = [ "wlan0" ];
    };
  };

  environment.systemPackages = with pkgs; [ vim ];

  services.openssh.enable = true;

  time.timeZone = "America/Edmonton";

  # nix settings
  nix.settings.experimental-features = [ "nix-command" "flakes" ];
  nix.settings.trusted-users = [ "root" ];
  nix.settings.auto-optimise-store = true;
  nix.gc = {
    automatic = true;
    dates = "weekly";
    options = "--delete-older-than 30d";
  };

  systemd.services.rpiclock = {
    description = "rpiclock";
    after = [ "network-online.target" ];
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      Restart = "always";
      # NOTE: any % in the iCal URL needs to be escaped as %% due to systemd's usage of it as a special char;
      # Google Calendar's private shared URLs have % embedded in them
      ExecStart = ''
        ${pkgs.rpiclock}/bin/rpiclock.py \
          --led-rows=32 \
          --led-cols=64 \
          --led-gpio-mapping=regular \
          --led-slowdown-gpio=4 \
          --font-path ${pkgs.rpiclock}/fonts \
          --ical-url="...your-ical-url..."
        '';
    };
  };

  hardware.enableRedistributableFirmware = true;
  system.stateVersion = "23.11";
}
```
