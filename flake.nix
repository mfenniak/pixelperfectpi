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
        stretchable = (pythonInterpreter: pkgs.rustPlatform.buildRustPackage rec {
          pname = "stretchable";
          version = "v1.0.0";
          # format = "pyproject";

          src = pkgs.fetchFromGitHub {
            owner = "mortencombat";
            repo = "stretchable";
            rev = version;
            sha256 = "sha256-XKMRtGoyPCG4g8UBfPB8CGK0bIgPSFNCLmNXHr/2Mvs=";
          };

          nativeBuildInputs = [
            pkgs.rustc
            pkgs.cargo
            pkgs.maturin
          ];

          # "Mark" this derivation as a Python module so that
          # requiredPythonModules/hasPythonModule recognizes it as such...
          pythonModule = pythonInterpreter;

          cargoHash = "sha256-1Fe3UfREQ2fiQYiwCT/ohXgeJqEmhwyQGyQrFRpd78A=";
          cargoPatches = [
            ./stretchable-Cargo.lock.patch
          ];
          buildPhase = ''
            ${pkgs.maturin}/bin/maturin build --interpreter ${pythonInterpreter}/bin/python
          '';
          installPhase = ''
            TARGET=$out/lib/python$(${pythonInterpreter}/bin/python -c "import sysconfig; print(sysconfig.get_python_version())")/site-packages
            mkdir -p $TARGET
            ${pkgs.unzip}/bin/unzip -o target/wheels/*.whl -d $TARGET
          '';

        });
        pythonPackages = (pythonInterpreter: (ps:
          [
            (mfenniak.packages.${system}.python-librgbmatrix pythonInterpreter)
            # FIXME: not all these dependencies are needed for the package; some could be split into devShell only
            ps.aiohttp
            ps.aiomqtt
            ps.backoff
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
            (stretchable pythonInterpreter)
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
          doCheck = false; # unit tests fail due to home assistant component's presence (FIXME this is probably very dated?)
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            (pkgs.${python}.withPackages (pythonPackages pkgs.${python}))
            pkgs.mosquitto # for mosquitto_sub & mosquitto_pub test cmds
          ];
        };
      });
}
