{
  description = "A Nix-flake-based Python development environment";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";

  outputs = {
    self,
    nixpkgs,
  }: let
    supportedSystems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];
    forEachSupportedSystem = f:
      nixpkgs.lib.genAttrs supportedSystems
      (system: f {pkgs = import nixpkgs {inherit system;};});
  in {
    devShells = forEachSupportedSystem ({pkgs}: {
      default = pkgs.mkShell {
        venvDir = "venv";
        packages = with pkgs;
          [
            # LSP
            pyright

            # python311
            # python3Packages.pip
            # git
            openvswitch
            texlive.combined.scheme-full
            glibcLocales
          ]
          ++ (with pkgs.python3Packages; [
            # pip
            venvShellHook
          ]);
        # Run this command, only after creating the virtual environment
        postVenvCreation = ''
          git clone https://github.com/cengwins/ahc
          cd ahc
          pip install -r requirements.txt
          pip install adhoccomputing
          pip install sphinx-autodoc-typehints
          pip install nbsphinx
        '';

        postShellHook = ''
          export LANG="en_US.UTF-8"
          export LOCALE_ARCHIVE="${pkgs.glibcLocales}/lib/locale/locale-archive"
          export PYTHONPATH=`pwd`
          export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib/:/run/opengl-driver/lib/
        '';
      };
    });
  };
}
