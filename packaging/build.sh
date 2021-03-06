#!/usr/bin/env bash


# ##########################################################################################
#                       Archey 4 distribution packages building script                     #
#
# Dependencies :
# * python3
# * rpm
# * bsdtar
# * debsigs
# * fpm >= 1.11.0
# * twine >= 3.1.1
#
# Procedure to install them on Debian :
# $ sudo apt install ruby rpm build-essential libarchive-tools debsigs rubygems python3-pip
# $ sudo gem install --no-document fpm
# $ sudo pip3 install setuptools twine
#
# Run it as :
# $ bash packaging/build.sh [REVISION] [0xGPG_IDENTITY]
#
# Known packages error (FPM bug ?) :
# * Arch Linux :
#     * `--pacman-optional-depends` appears to be ignored [jordansissel/fpm#1619]
#
# If you happen to tweak packaging scripts, please lint them before submitting changes :
# $ shellcheck packaging/*
#
# ##########################################################################################


# Abort on error, don't allow usages of undeclared variable.
set -e ; set -u


# Let's gather some metadata from the `setup.py` file.
NAME="$(python3 setup.py --name)"
VERSION="$(python3 setup.py --version)"
AUTHOR="$(python3 setup.py --author)"
AUTHOR_EMAIL="$(python3 setup.py --author-email)"
SUPPORTED_PYTHON_VERSIONS="$(python3 setup.py --classifiers | grep 'Programming Language' | grep -Po '\d\.\d')"


# DRY.
REVISION="${1:-1}"
GPG_IDENTITY="${2:-}"
DIST_OUTPUT='./dist'
FPM_COMMON_ARGS=(
	--input-type python \
	--force \
	--log error \
	--iteration "$REVISION" \
	--category 'utils' \
	--provides 'archey' \
	--provides 'archey4' \
	--config-files "etc/archey4" \
	--config-files "etc/archey4/config.json" \
	--architecture all \
	--maintainer "${AUTHOR} <${AUTHOR_EMAIL}>" \
	--after-install packaging/after_install \
	--after-upgrade packaging/after_install \
	--before-remove packaging/before_remove \
	--python-bin python3 \
	--no-python-fix-name \
	--no-python-dependencies \
)


echo ">>> Packages generation for ${NAME}_v${VERSION}-${REVISION} <<<"


# Prepare the configuration file under a regular `etc/` directory.
mkdir -p etc/archey4 && cp archey/config.json etc/archey4/config.json


# Prevent Setuptools from generating byte-code files.
export PYTHONDONTWRITEBYTECODE=1


# Build a Debian (.DEB) package.
echo 'Now generating Debian package...'
fpm \
	"${FPM_COMMON_ARGS[@]}" \
	--output-type deb \
	--package "${DIST_OUTPUT}/${NAME}_${VERSION}-${REVISION}_all.deb" \
	--depends 'procps' \
	--depends 'python3 >= 3.4' \
	--depends 'python3-distro' \
	--depends 'python3-netifaces' \
	--python-install-bin usr/bin \
	--python-install-lib usr/lib/python3/dist-packages \
	--deb-priority 'optional' \
	--deb-field 'Suggests: dnsutils, lm-sensors, pciutils, wmctrl, virt-what, btrfs-progs' \
	--deb-no-default-config-files \
	setup.py

# Sign the resulting Debian package if a GPG identity has been provided.
if [ -n "$GPG_IDENTITY" ]; then
	echo "Now signing Debian package with ${GPG_IDENTITY}..."
	debsigs \
		--sign=origin \
		-k "$GPG_IDENTITY" \
		./dist/*.deb
fi


# Build Red Hat / CentOS / Fedora (.RPM) packages.
for python_version in $SUPPORTED_PYTHON_VERSIONS; do
	echo "Now generating RPM package (Python ${python_version})..."
	fpm \
		"${FPM_COMMON_ARGS[@]}" \
		--output-type rpm \
		--package "${DIST_OUTPUT}/${NAME}-${VERSION}-${REVISION}.py${python_version//.}.noarch.rpm" \
		--depends 'procps' \
		--depends "python3 >= ${python_version}" \
		--depends 'python3-distro' \
		--depends 'python3-netifaces' \
		--python-install-bin usr/bin \
		--python-install-lib "usr/lib/python${python_version}/site-packages" \
		setup.py
done


# Build an Arch Linux (.TAR.XZ) package.
ARCH_LINUX_PYTHON_VERSION='3.8'  # See <https://www.archlinux.org/packages/extra/x86_64/python/>.
echo "Now generating Arch Linux package (Python ${python_version})..."
fpm \
	"${FPM_COMMON_ARGS[@]}" \
	--output-type pacman \
	--package "${DIST_OUTPUT}/${NAME}-${VERSION}-${REVISION}-any.pkg.tar.xz" \
	--depends 'procps-ng' \
	--depends "python>=${ARCH_LINUX_PYTHON_VERSION}" \
	--depends 'python-distro' \
	--depends 'python-netifaces' \
	--conflicts 'archey-git' \
	--conflicts 'archey2' \
	--conflicts 'archey3-git' \
	--conflicts 'pyarchey' \
	--python-install-bin usr/bin \
	--python-install-lib "usr/lib/python${ARCH_LINUX_PYTHON_VERSION}/site-packages" \
	--pacman-optional-depends 'bind-tools: WAN_IP would be detected faster' \
	--pacman-optional-depends 'lm_sensors: Temperature would be more accurate' \
	--pacman-optional-depends 'pciutils: GPU wouldn'"'"'t be detected without it' \
	--pacman-optional-depends 'wmctrl: WindowManager would be more accurate' \
	--pacman-optional-depends 'virt-what: Model would contain details about the hypervisor' \
	--pacman-optional-depends 'btrfs-progs: Disk would support BTRFS in usage computations' \
	setup.py


# Remove the fake `etc/` directory.
rm -rf etc/


# Silence some Setuptools warnings by re-enabling byte-code generation.
unset PYTHONDONTWRITEBYTECODE


# Build Python source TAR and WHEEL distribution packages.
echo 'Now building source TAR and WHEEL distribution packages...'
python3 setup.py -q sdist bdist_wheel

# Check whether packages description will render correctly on PyPI.
echo 'Now checking PyPI description rendering...'
if twine check dist/*.{tar.gz,whl}; then
	echo -n 'Upload source and wheel distribution packages to PyPI ? [y/N] '
	read -r -n 1 -p '' && echo
	if [[ "$REPLY" =~ ^[yY]$ ]]; then
		echo 'Now signing & uploading source TAR and WHEEL to PyPI...'
		twine upload \
			--sign --identity "$GPG_IDENTITY" \
			dist/*.{tar.gz,whl}
	fi
fi
