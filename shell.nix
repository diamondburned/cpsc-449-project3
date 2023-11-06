{ pkgs ? import <nixpkgs> {} }:

let
	krakend = pkgs.buildGoModule rec {
		pname = "krakend";
		version = "2.4.3";
		src = pkgs.fetchFromGitHub {
			owner = "krakend";
			repo = "krakend-ce";
			rev = "v${version}";
			sha256 = "sha256-LSFrXThaAbnZjDAIzInzytjvTp1+YhWiSmatu3dOkGo=";
		};
		vendorSha256 = "sha256-RzhEetQ8HrIOM39PiIJ9CXmHoj4Rc2g9BtMVjNoP86U=";
		patchPhase = "sed -i 's|@go get.*|@true|g' Makefile";
		buildPhase = "make build";
		installPhase = "install -Dm755 krakend $out/bin/krakend";
	};
in

pkgs.mkShell {
	buildInputs = with pkgs; [
		krakend
		litefs
		python3
		python3Packages.black
		pyright
		sqlite
		sqlfluff
		litecli
		foreman
		httpie
		entr
		awscli
		jre_headless
	];

	shellHook = ''
		# Reset PYTHONPATH to avoid conflicts with nixpkgs' python.
		unset PYTHONPATH

		python3 -m venv .venv
		source .venv/bin/activate
	'';
}
