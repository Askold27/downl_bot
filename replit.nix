{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.python310Packages.requests
    pkgs.python310Packages.pyrogram
    pkgs.python310Packages.tgcrypto
    pkgs.python310Packages.python-dotenv
  ];
  env = {
    PYTHONPATH = "$PYTHONPATH${pkgs.python310}";
  };
}
