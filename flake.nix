{
  description = "Idle Shutdown Container - AI cluster monitoring with REST API";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.python3Packages.psutil
          pkgs.python3Packages.pynvml
          pkgs.python3Packages.requests
          pkgs.python3Packages.fastapi
          pkgs.python3Packages.uvicorn
        ];

        shellHook = ''
          # TODO soruce env does not work
          soruce .env.example
        '';
      };
    };
}
