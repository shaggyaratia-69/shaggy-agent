# nix/tui.nix — Shaggy TUI (Ink/React) compiled with tsc and bundled
{ pkgs, shaggyNpmLib, ... }:
let
  src = ../ui-tui;
  npmDeps = pkgs.fetchNpmDeps {
    inherit src;
    hash = "sha256-dNL/J4tyQQ7Ji3xfIE5b5Jdi6rQyCFjqYpzLYftJVdc=";
  };

  npm = shaggyNpmLib.mkNpmPassthru { folder = "ui-tui"; attr = "tui"; pname = "shaggy-tui"; };

  packageJson = builtins.fromJSON (builtins.readFile (src + "/package.json"));
  version = packageJson.version;
in
pkgs.buildNpmPackage (npm // {
  pname = "shaggy-tui";
  inherit src npmDeps version;

  doCheck = false;
  npmFlags = [ "--legacy-peer-deps" ];

  installPhase = ''
    runHook preInstall

    mkdir -p $out/lib/shaggy-tui

    # Single self-contained bundle built by scripts/build.mjs (esbuild).
    cp -r dist $out/lib/shaggy-tui/dist

    # package.json kept for "type": "module" resolution on `node dist/entry.js`.
    cp package.json $out/lib/shaggy-tui/

    runHook postInstall
  '';
})
