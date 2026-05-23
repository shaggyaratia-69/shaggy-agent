# nix/packages.nix — Shaggy Agent package built with uv2nix
{ inputs, ... }:
{
  perSystem =
    { pkgs, inputs', ... }:
    let
      shaggyAgent = pkgs.callPackage ./shaggy-agent.nix {
        inherit (inputs) uv2nix pyproject-nix pyproject-build-systems;
        npm-lockfile-fix = inputs'.npm-lockfile-fix.packages.default;
        # Only embed clean revs — dirtyRev doesn't represent any upstream
        # commit, so comparing it would always claim "update available".
        rev = inputs.self.rev or null;
      };
    in
    {
      packages = {
        default = shaggyAgent;
        tui = shaggyAgent.shaggyTui;
        web = shaggyAgent.shaggyWeb;

        fix-lockfiles = shaggyAgent.shaggyNpmLib.mkFixLockfiles {
          packages = [ shaggyAgent.shaggyTui shaggyAgent.shaggyWeb ];
        };
      };
    };
}
