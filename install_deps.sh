#!/usr/bin/env bash
set -eo pipefail

LITEFS_INSTALL_PATH=./run/bin/litefs
LITEFS_VERSION=0.5.4

KRAKEND_INSTALL_PATH=./run/bin/krakend
KRAKEND_VERSION=2.4.3

GOOS=linux
GOARCH=
	
case $(uname -m) in
x86_64)
	GOARCH=amd64
	;;
aarch64)
	GOARCH=arm64
	;;
*)
	echo "unsupported architecture: $(uname -m)" >&2
	exit 1
	;;
esac

install_litefs() {
	if is_installed "litefs" "${LITEFS_INSTALL_PATH}"; then
		return
	fi

	LITEFS_URL=
	LITEFS_URL+="https://github.com/superfly/litefs/releases/download"
	LITEFS_URL+="/v${LITEFS_VERSION}"
	LITEFS_URL+="/litefs-v${LITEFS_VERSION}-${GOOS}-${GOARCH}.tar.gz"

	echo "Downloading litefs from ${LITEFS_URL}..." >&2

	dstDir=$(mktemp -d)
	wget -qO- "${LITEFS_URL}" | tar xz -C "${dstDir}"
	
	mkdir -p "$(dirname "${LITEFS_INSTALL_PATH}")"
	install -m 755 "${dstDir}/litefs" "${LITEFS_INSTALL_PATH}"
	
	rm -r "${dstDir}"

	echo "Installed litefs to ${LITEFS_INSTALL_PATH}" >&2
}

install_krakend() {
	if is_installed "krakend" "${KRAKEND_INSTALL_PATH}"; then
		return
	fi

	KRAKEND_URL=
	KRAKEND_URL+="https://github.com/krakend/krakend-ce/releases/download"
	KRAKEND_URL+="/v${KRAKEND_VERSION}"
	KRAKEND_URL+="/krakend_${KRAKEND_VERSION}_${GOARCH}_generic-${GOOS}.tar.gz"

	echo "Downloading krakend from ${KRAKEND_URL}..." >&2
	
	dstDir=$(mktemp -d)
	wget -qO- "${KRAKEND_URL}" | tar xz -C "${dstDir}"
	
	mkdir -p "$(dirname "${KRAKEND_INSTALL_PATH}")"
	install -m 755 "${dstDir}/usr/bin/krakend" "${KRAKEND_INSTALL_PATH}"
	
	rm -r "${dstDir}"

	echo "Installed krakend to ${KRAKEND_INSTALL_PATH}" >&2
}

# is_installed $pname $installPath
is_installed() {
	local pname=$1
	local installPath=$2

	if command -v "$pname" > /dev/null; then
		echo "$pname has already been installed globally" >&2
		return 0
	fi
	
	if [[ -x "$installPath" ]]; then
		echo "$pname has already been installed locally" >&2
		return 0
	fi

	return 1
}

# install_url $pname $installPath $url -> $tmpDir
install_url() {
	local pname=$1
	local installPath=$2
	local url=$3
	
	echo "Downloading $pname from $url..." >&2
	
	dstDir=$(mktemp -d)
	wget -qO "$dstDir" "${LITEFS_URL}"
}

install_litefs
install_krakend
