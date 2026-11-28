param([Parameter(Mandatory)][string]$DatabaseFile, [string]$ComposeFile = 'docker-compose.yml', [switch]$ConfirmRestore)
$ErrorActionPreference = 'Stop'
if (-not $ConfirmRestore) { throw 'Restore replaces database records. Verify an isolated target and pass -ConfirmRestore only after explicit authorization.' }
$restoreSource = (Resolve-Path -LiteralPath $DatabaseFile).Path
if (-not (Test-Path -LiteralPath $restoreSource -PathType Leaf)) { throw 'SQL file not found' }
docker compose -f $ComposeFile cp $restoreSource db:/tmp/bnut-restore.sql
if ($LASTEXITCODE -ne 0) { throw 'Copy failed' }
docker compose -f $ComposeFile exec -T db sh -c 'MYSQL_PWD="$MYSQL_PASSWORD" mysql -u"$MYSQL_USER" "$MYSQL_DATABASE" < /tmp/bnut-restore.sql'
if ($LASTEXITCODE -ne 0) { throw 'Database restore failed; inspect the isolated target before retrying' }
docker compose -f $ComposeFile exec -T db rm /tmp/bnut-restore.sql
