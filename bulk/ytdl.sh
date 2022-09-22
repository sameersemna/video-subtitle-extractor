#!/bin/bash

# apt install youtube-dl
# youtube-dl --version
# which youtube-dl

dirVidOcr='.'
# dirVidOcr='/Users/sameer.shemna/Private/Test/Python/video-subtitle-extractor'
dirBulk="$dirVidOcr/bulk"
listBulk="$dirBulk/errorDownload.csv"
listDone="$dirBulk/done.csv"

ytPrefix='https://www.youtube.com/watch?v='

while IFS=, read -r yt lang; do
  lang=${lang//[$'\t\r\n']}

  if [ -z "$lang" ]; then
    lang='eng'
  fi
  if [[ "$yt" == *"$ytPrefix"* ]]; then
    ytId=${yt//"$ytPrefix"}
  else
    ytId=${yt//[$'\t\r\n ']}
  fi

  ytIdSearch="-- $ytId"

  if grep -Fxq $ytIdSearch $listDone; then
    echo "# Processed earlier $ytId"
    continue
  else
    echo "# Processing $ytId"
  fi

  fileMp4="$ytId.mp4"

  if [ -f "$fileMp4" ]; then
    echo "No need to download Video, exists: $fileMp4"
  else
    cmd="youtube-dl -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4' --output '$ytId.%(ext)s' 'https://youtu.be/$ytId'"
    echo $cmd
    eval $cmd
    sleep 5
  fi

  cmd="mv \"./$fileMp4\" \"$dirBulk/download/$fileMp4\""
  echo $cmd
  eval $cmd

done < $listBulk

echo '# *** DONE ***'

