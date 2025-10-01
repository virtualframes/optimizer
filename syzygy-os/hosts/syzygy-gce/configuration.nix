{ config, pkgs, inputs, ... }:

{
  imports =
    [
      # Import user configuration
      ../../users/operator/home.nix
    ];

  # 1. Boot Configuration (UEFI required for GCE)
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  # 2. Networking & GCE Optimization (MANDATORY)
  networking.hostName = "syzygy-core";
  # Enable GCE network drivers and guest agents
  nixpkgs.config.google-compute-image.enable = true;
  services.google-guest-agent.enable = true;

  # 3. Security (Hardened)
  services.openssh.enable = true;
  services.openssh.passwordAuthentication = false;
  services.openssh.permitRootLogin = "no";
  networking.firewall.allowedTCPPorts = [ 22 ];

  # 4. Synapse Stack Prerequisites
  virtualisation.docker.enable = true;
  environment.systemPackages = with pkgs; [
    git neovim htop tmux kubectl helm temporal-cli rustc cargo
    nodejs_22 python312
  ];

  # 5. User Accounts
  users.users.operator = {
    isNormalUser = true;
    extraGroups = [ "wheel" "docker" ];
    # CRITICAL: Add your SSH public key here
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAA... your_public_key"
    ];
  };

  # 6. Git Integration (Clone repository on first boot)
  systemd.services.clone-optimizer = {
    description = "Clone virtualframes/optimizer repository";
    after = [ "network.target" ];
    wantedBy = [ "multi-user.target" ];
    script = ''
      if [ ! -d "/home/operator/optimizer" ]; then
        ${pkgs.git}/bin/git clone https://github.com/virtualframes/optimizer.git /home/operator/optimizer
        chown -R operator:users /home/operator/optimizer
      fi
    '';
    serviceConfig = {
      Type = "oneshot";
    };
  };
}