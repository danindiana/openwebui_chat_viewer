# Fail2ban Monitoring and UFW Permaban System

## Overview
Your system is now configured with:
- **Fail2ban ban duration**: 1 year (31536000 seconds)
- **Automated monitoring**: Hourly export of banned IPs
- **UFW integration**: Automatic permanent firewall blocking

## Configuration Files
- **Fail2ban config**: `/etc/fail2ban/jail.local`
- **Permaban list**: `/home/randy/ufw_permaban_list.txt`
- **Activity log**: `/home/randy/fail2ban_monitor.log`
- **Monitor script**: `/home/randy/fail2ban_monitor.sh`
- **Auto-export script**: `/home/randy/fail2ban_auto_export.sh`

## Active Jails
- `sshd` - SSH authentication attempts
- `nginx-http-auth` - Nginx HTTP authentication failures
- `nginx-botsearch` - Nginx bot/scanner detection

## Using the Monitoring System

### View Current Status
```bash
./fail2ban_monitor.sh status
```
Shows all active jails and their current ban status.

### List All Banned IPs
```bash
./fail2ban_monitor.sh banned
```
Displays currently banned IPs across all jails.

### Watch Real-Time Activity
```bash
./fail2ban_monitor.sh watch
```
Live tail of fail2ban log showing bans, unbans, and alerts (Ctrl+C to stop).

### Generate Ban Report
```bash
./fail2ban_monitor.sh report
```
Shows statistics and top banned IPs from logs.

### Export Banned IPs to Permaban List
```bash
./fail2ban_monitor.sh export
```
Exports all currently banned IPs to your permanent ban list.

### Apply Permaban List to UFW
```bash
./fail2ban_monitor.sh apply
```
Applies all IPs in your permaban list as UFW deny rules.

### Manual IP Management
```bash
# Add a specific IP to permaban and block in UFW
./fail2ban_monitor.sh add-to-permaban 192.168.1.100

# Unban an IP from fail2ban (but not UFW)
./fail2ban_monitor.sh unban 192.168.1.100

# Check specific jail details
./fail2ban_monitor.sh jail sshd
```

## Automated System
A cron job runs every hour to automatically:
1. Check all fail2ban jails for banned IPs
2. Export new banned IPs to the permaban list
3. Automatically add UFW deny rules for new IPs

You can verify the cron job is active:
```bash
crontab -l
```

## Checking Logs
```bash
# View fail2ban activity log
tail -f /home/randy/fail2ban_monitor.log

# View fail2ban system log
sudo tail -f /var/log/fail2ban.log

# View authentication attempts in system logs
sudo journalctl -u sshd -f
sudo journalctl -u nginx -f
```

## Viewing Current UFW Rules
```bash
# Show all UFW rules
sudo ufw status numbered

# Show only deny rules
sudo ufw status | grep DENY
```

## Testing the System
To see if fail2ban is detecting and banning attempts:
1. Try multiple failed SSH logins from another machine
2. Watch with: `./fail2ban_monitor.sh watch`
3. Check banned IPs: `./fail2ban_monitor.sh banned`

## Best Practices
1. **Regular Review**: Periodically check `./fail2ban_monitor.sh report` to see attack patterns
2. **Backup Permaban List**: Keep a backup of `/home/randy/ufw_permaban_list.txt`
3. **Monitor Disk Space**: Fail2ban logs can grow large over time
4. **Whitelist Important IPs**: Add trusted IPs to fail2ban ignore list in `/etc/fail2ban/jail.local`:
   ```
   [DEFAULT]
   ignoreip = 127.0.0.1/8 ::1 YOUR_TRUSTED_IP
   ```

## Troubleshooting
```bash
# Check fail2ban service status
sudo systemctl status fail2ban

# Restart fail2ban if needed
sudo systemctl restart fail2ban

# Test fail2ban configuration
sudo fail2ban-client -d

# Check if UFW is active
sudo ufw status verbose
```

## What Gets Monitored
- **SSH**: Failed login attempts, brute force attacks
- **Nginx**: HTTP authentication failures, bot scanning, bad requests
- **System**: All authentication attempts logged by the system

## Next Steps
1. Run `./fail2ban_monitor.sh watch` to see real-time activity
2. Run `./fail2ban_monitor.sh report` to see historical data
3. Monitor `/home/randy/fail2ban_monitor.log` for automated actions
4. Consider adding more jails for other services you're running

---
Generated: $(date)
