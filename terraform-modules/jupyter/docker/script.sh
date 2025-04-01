#!/bin/bash
set -e

REPORT_EXT=${REPORT_EXT:="pdf"}

echo "Fetching notebook ${NOTEBOOK_NAME}"
./fetch-notebook.sh
echo "Running notebook"
ipython --colors NoColor notebook.ipynb

if [[ -z "${REPORT_NAME}" ]]
then
  echo "REPORT_NAME not defined, skipping reporting part"
else
    ./publish-result.py
    [[ -z "${TEAMS_WEBHOOK_URL}" ]] || ./notify-teams.py
    [[ -z "${LAILO_WEBHOOK_URL}" ]] || ./notify-lailo.py
    [[ -z "${TELEGRAM_BOT_TOKEN}" || -z "${TELEGRAM_CHAT_ID}" ]] || ./notify-telegram.py
fi

