{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    
    flake-utils.url = "github:numtide/flake-utils";

    mfenniak = {
      url = "github:mfenniak/custom-nixpkgs?dir=flake";
      # url = "/home/mfenniak/Dev/custom-nixpkgs/flake";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, mfenniak }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        python = "python311";
        pkgs = nixpkgs.legacyPackages.${system};
      in rec {
        overlays.default = self: super: {
          rpiclock = packages.default;
        };

        packages.default = pkgs.${python}.pkgs.buildPythonApplication {
          pname = "rpiclock";
          version = "0.1";
          src = ./.;
          propagatedBuildInputs = [
            (mfenniak.packages.${system}.python-librgbmatrix pkgs.${python})
            pkgs.${python}.pkgs.aiohttp
          ];
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            # mfenniak.packages.${system}.lib-rpi-rgb-led-matrix
            # python-librgbmatrix

            (pkgs.${python}.withPackages
              (ps: with ps; [
                (mfenniak.packages.${system}.python-librgbmatrix pkgs.${python})
                aiohttp
              ]))
          ];
        };
      });
}
