#!/bin/bash
# ============================================================================
# HEARTFL DATABASE BACKUP SCRIPT
# ============================================================================
# Run this script regularly (via cron job) to backup your database
# Syntax: ./backup_database.sh [backup_dir]
# Example: ./backup_database.sh /backups/heartfl/
# ============================================================================

BACKUP_DIR="${1:-.}/backups"
DB_FILE="db.sqlite3"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="db_backup_${TIMESTAMP}.sqlite3"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup database
echo "[$(date)] Starting database backup..."
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_DIR/$BACKUP_NAME"
    
    # Verify backup
    if [ -f "$BACKUP_DIR/$BACKUP_NAME" ]; then
        echo "[$(date)] ✅ Backup successful: $BACKUP_DIR/$BACKUP_NAME"
        echo "[$(date)] File size: $(du -h "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)"
        
        # Keep only last 30 days of backups
        RETENTION_DAYS=30
        find "$BACKUP_DIR" -name "db_backup_*.sqlite3" -type f -mtime +$RETENTION_DAYS -delete
        echo "[$(date)] ✅ Old backups (>$RETENTION_DAYS days) removed"
    else
        echo "[$(date)] ❌ Backup failed: Could not copy database file"
        exit 1
    fi
else
    echo "[$(date)] ❌ Database file not found: $DB_FILE"
    exit 1
fi

echo "[$(date)] Backup process completed"
