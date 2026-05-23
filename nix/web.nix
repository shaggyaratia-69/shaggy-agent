# nix/web.nix — Shaggy Web Dashboard (Vite/React) frontend build
{ pkgs, shaggyNpmLib, ... }:
let
  src = ../web;
  npmDeps = pkgs.fetchNpmDeps {
    inherit src;
    hash = "sha256-GxSmEpclOwmv94KmGMediPITxqXAsxqTEQOoDIbYkUw=";
  };

  npm = shaggyNpmLib.mkNpmPassthru { folder = "web"; attr = "web"; pname = "shaggy-web"; };

  packageJson = builtins.fromJSON (builtins.readFile (src + "/package.json"));
  version = packageJson.version;
in
pkgs.buildNpmPackage (npm // {
  pname = "shaggy-web";
  inherit src npmDeps version;

  doCheck = false;

  buildPhase = ''
    npx tsc -b
    npx vite build --outDir dist
  '';

  installPhase = ''
    runHook preInstall
    cp -r dist $out
    runHook postInstall
  '';
})
