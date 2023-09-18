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
          pixelperfectpi = packages.default;
        };

        packages.default = pkgs.${python}.pkgs.buildPythonApplication {
          pname = "pixelperfectpi";
          version = "0.1";
          src = ./.;
          propagatedBuildInputs = with pkgs.${python}.pkgs; [
            (mfenniak.packages.${system}.python-librgbmatrix pkgs.${python})
            aiohttp
            lxml
            icalendar
            pytz
            recurring-ical-events
          ] ++ lib.optional (system == "x86_64-linux") (mfenniak.packages.${system}.python-rgbmatrixemulator pkgs.${python});
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            (pkgs.${python}.withPackages
              (ps: with ps;
                [
                  (mfenniak.packages.${system}.python-librgbmatrix pkgs.${python})
                  aiohttp
                  lxml
                  icalendar
                  pytz
                  recurring-ical-events
                ] ++ lib.optional (system == "x86_64-linux") (mfenniak.packages.${system}.python-rgbmatrixemulator pkgs.${python})
              )
            )
          ];
        };
      });
}
