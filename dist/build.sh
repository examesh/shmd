#!/bin/bash

set -o errtrace
set -o nounset
set -o errexit
set -o pipefail
#set -o posix

MY_FP=$(readlink -f "${0}")
MY_DP=${MY_FP%/*}
APP=shmd
APP_BIN=${APP}.linux_x86-64
TMP_DP=/tmp/.pyinstaller_${APP}

cd ${MY_DP}/..
echo "Building ${APP_BIN}"
rm -f ${TMP_DP}/${APP}.spec
pyinstaller \
  --workpath ${TMP_DP} \
  --specpath ${TMP_DP} \
  --log-level=WARN \
  --noconfirm \
  --onefile \
  ${APP}.py
mv ${MY_DP}/${APP} ${MY_DP}/${APP_BIN}
echo "Done: ${MY_DP}/${APP_BIN} created"
