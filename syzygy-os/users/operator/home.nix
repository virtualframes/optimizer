{ config, pkgs, ... }:

{
  # Integrate home-manager with the NixOS configuration
  home-manager.users.operator = {
    # 1. Shell Configuration (Zsh + Powerlevel10k Theme)
    programs.zsh = {
      enable = true;
      oh-my-zsh = {
        enable = true;
        plugins = [ "git" "kubectl" "docker" "terraform" ];
        # Use Powerlevel10k for advanced visual customization
        theme = "powerlevel10k/powerlevel10k";
      };
    };

    # 2. Custom Dotfiles (Example: Neovim with Gruvbox)
    programs.neovim = {
      enable = true;
      vimAlias = true;
      plugins = with pkgs.vimPlugins; [ gruvbox ];
      extraConfig = ''
        colorscheme gruvbox
        set number
      '';
    };

    home.stateVersion = "24.05";
  };
}