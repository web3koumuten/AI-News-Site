#!/bin/bash
# AI-News-Site更新スクリプト

# 設定
FTP_HOST="your-ftp-host.com"
FTP_USER="your-username"
FTP_PASS="your-password"
REMOTE_DIR="/public_html/ai-news/"
LOCAL_DIR="/Users/takaokayuuta/Desktop/AI-News-Site/"

# FTPでアップロード
echo "Uploading files to WordPress site..."

ftp -n $FTP_HOST <<END_SCRIPT
quote USER $FTP_USER
quote PASS $FTP_PASS
cd $REMOTE_DIR
lcd $LOCAL_DIR
put index.html
cd posts
lcd posts
put *.html
quit
END_SCRIPT

echo "Upload complete!"