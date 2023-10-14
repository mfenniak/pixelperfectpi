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
        pythonPackages = (pythonInterpreter: (ps:
          [
            (mfenniak.packages.${system}.python-librgbmatrix pythonInterpreter)
            # FIXME: not all these dependencies are needed for the package; some could be split into devShell only
            ps.aiohttp
            ps.aiomqtt
            ps.backoff
            ps.dependency-injector
            ps.icalendar
            ps.lxml
            ps.mypy
            ps.pylint
            ps.pytest
            ps.pytest-asyncio
            ps.pytz
            ps.recurring-ical-events
            ps.types-pillow
            ps.types-pytz
          ] ++ ps.lib.optional (system == "x86_64-linux") (mfenniak.packages.${system}.python-rgbmatrixemulator pythonInterpreter)
        ));
      in rec {
        overlays.default = self: super: {
          pixelperfectpi = packages.default;
        };

        packages.default = pkgs.${python}.pkgs.buildPythonApplication {
          pname = "pixelperfectpi";
          version = "0.1";
          src = ./.;
          propagatedBuildInputs = [] ++ ((pythonPackages pkgs.${python}) pkgs.${python}.pkgs);
          doCheck = false; # unit tests fail due to home assistant component's presence
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            (pkgs.${python}.withPackages (pythonPackages pkgs.${python}))
            pkgs.mosquitto # for mosquitto_sub & mosquitto_pub test cmds
          ];
        };
      });
}
