param([string]$Destination = './backups', [string]$ComposeFile = 'docker-compose.yml')
$ErrorActionPreference = 'Stop'
$backupDestination = [IO.Path]::GetFullPath($Destination)
New-Item -ItemType Directory -Force -Path $backupDestination | Out-Null
$backupStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
docker compose -f $ComposeFile exec -T db sh -c 'MYSQL_PWD="$MYSQL_PASSWORD" mysqldump -u"$MYSQL_USER" --single-transaction --no-tablespaces --set-gtid-purged=OFF "$MYSQL_DATABASE" > /tmp/bnut-backup.sql'
if ($LASTEXITCODE -ne 0) { throw 'Database backup failed' }
docker compose -f $ComposeFile cp db:/tmp/bnut-backup.sql "$backupDestination/database-$backupStamp.sql"
if ($LASTEXITCODE -ne 0) { throw 'Database copy failed' }
docker compose -f $ComposeFile exec -T db rm /tmp/bnut-backup.sql
docker compose -f $ComposeFile exec -T backend tar -czf /tmp/bnut-media.tar.gz -C /app private-media
if ($LASTEXITCODE -ne 0) { throw 'Media backup failed' }
docker compose -f $ComposeFile cp backend:/tmp/bnut-media.tar.gz "$backupDestination/media-$backupStamp.tar.gz"
if ($LASTEXITCODE -ne 0) { throw 'Media copy failed' }
docker compose -f $ComposeFile exec -T backend rm /tmp/bnut-media.tar.gz
Get-ChildItem -LiteralPath $backupDestination -File | Where-Object Name -Like "*-$backupStamp.*" | Get-FileHash -Algorithm SHA256
