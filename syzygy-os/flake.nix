{
  description = "SyzygyOS Immutable Infrastructure";

  inputs = {
    # Use stable NixOS channel (24.05 as of late 2025)
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";

    # Home Manager for personalization (themes, dotfiles)
    home-manager.url = "github:nix-community/home-manager/release-24.05";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";

    # Generators for cloud images
    nixos-generators.url = "github:nix-community/nixos-generators";
    nixos-generators.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, home-manager, nixos-generators, ... }@inputs: {

    # Define the main NixOS configuration
    nixosConfigurations.syzygy-gce = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./hosts/syzygy-gce/configuration.nix
        # Integrate home-manager into the system configuration
        home-manager.nixosModules.home-manager
      ];
      specialArgs = { inherit inputs; };
    };

    # Define the GCE Image Generator Output (The artifact CI/CD will build)
    packages.x86_64-linux.gce-image = nixos-generators.nixosGenerate {
      system = "x86_64-linux";
      # Inherit the modules from the configuration defined above
      modules = self.nixosConfigurations.syzygy-gce.config.modules;
      format = "gce"; # Generate GCE compatible image (tar.gz)
    };
  };
}