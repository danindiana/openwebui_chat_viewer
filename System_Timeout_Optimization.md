# System Timeout Optimization for Fast Boot/Shutdown

**Date**: October 5, 2025  
**System**: Dell Precision T3600 with Ollama GPU inference  
**Objective**: Reduce service timeout waits from 90s to 30s for faster reboot/shutdown

## Changes Applied

### 1. System-wide Service Timeouts (`/etc/systemd/system.conf`)
```ini
# Reduced from default 90s to 30s
DefaultTimeoutStartSec=30s
DefaultTimeoutStopSec=30s  
DefaultTimeoutAbortSec=30s
DefaultDeviceTimeoutSec=30s
DefaultRestartSec=5s
DefaultEnvironment="SYSTEMD_LOG_LEVEL=warning"
```

### 2. User Session Timeouts (`/etc/systemd/user.conf`)  
```ini
# Faster user service shutdown
DefaultTimeoutStartSec=30s
DefaultTimeoutStopSec=30s
DefaultTimeoutAbortSec=30s
```

### 3. Critical Service Overrides

**Ollama Service** (`/etc/systemd/system/ollama.service.d/timeout.conf`):
```ini
[Service]
# Allow extra time for GPU model state cleanup
TimeoutStopSec=60s
TimeoutStartSec=30s
```

**Docker Service** (`/etc/systemd/system/docker.service.d/timeout.conf`):
```ini
[Service]  
# Allow time for container graceful shutdown
TimeoutStopSec=60s
TimeoutStartSec=30s
```

### 4. Kernel Boot Parameters (`/etc/default/grub`)
```bash
GRUB_CMDLINE_LINUX="quiet splash systemd.show_status=false rd.udev.log_level=3 rd.systemd=false"
```

## Timeout Strategy

### Standard Services: 30 seconds
- Most services get 30s to start/stop
- Faster than default 90s
- Still reasonable for normal operation
- Prevents hanging on problematic services

### Critical Services: 60 seconds  
- Ollama: Needs time to unload GPU models safely
- Docker: Requires container shutdown time
- Balance between speed and data safety

### Benefits Achieved

1. **Faster Shutdown**: 60s reduction per problematic service
2. **Faster Boot**: Reduced startup timeout waits  
3. **Better Responsiveness**: Services that fail start/stop quickly rather than hanging
4. **GPU Safety**: Ollama gets adequate time for model cleanup
5. **Container Safety**: Docker containers shut down gracefully

## Expected Performance Improvements

### Before Optimization
- **Service timeout**: 90 seconds per service
- **Potential hang time**: Up to 90s × number of failing services
- **Total shutdown**: Could exceed 5+ minutes with multiple service issues

### After Optimization  
- **Standard timeout**: 30 seconds per service
- **Critical services**: 60 seconds (Ollama, Docker)
- **Boot parameters**: Reduced logging overhead
- **Expected shutdown**: 1-2 minutes typical, 3 minutes worst case

## Configuration Verification

**Active timeout settings confirmed**:
```bash
systemctl show ollama.service | grep Timeout
# TimeoutStartUSec=30s
# TimeoutStopUSec=1min

systemctl show docker.service | grep Timeout  
# TimeoutStartUSec=30s
# TimeoutStopUSec=1min
```

**System configuration reloaded**: `systemctl daemon-reload` ✅  
**GRUB updated**: `update-grub` ✅

## Monitoring and Testing

### Test Commands
```bash
# Test service restart times
time sudo systemctl restart docker
time sudo systemctl restart ollama

# Monitor shutdown time
sudo shutdown -r +1  # Schedule reboot to test timing
```

### Verification Commands
```bash
# Check active timeout settings
systemctl show <service> | grep Timeout

# Check system-wide defaults  
grep Timeout /etc/systemd/system.conf

# Monitor service status during shutdown
journalctl -f -u systemd-shutdown
```

## Rollback Instructions

If any issues arise, restore original settings:

```bash
# Restore original GRUB
sudo cp /etc/default/grub.backup /etc/default/grub
sudo update-grub

# Remove service overrides
sudo rm /etc/systemd/system/ollama.service.d/timeout.conf
sudo rm /etc/systemd/system/docker.service.d/timeout.conf

# Reset system.conf (comment out additions)
sudo systemctl daemon-reload
```

## Summary

The timeout optimizations provide a good balance between:
- **Speed**: 3x faster standard service timeouts (30s vs 90s)
- **Safety**: Critical services (Ollama, Docker) get adequate shutdown time  
- **Reliability**: Prevents system hangs from problematic services
- **GPU Protection**: Ollama model cleanup time preserved

**Expected Result**: Significantly faster boot and shutdown times while maintaining system stability and data safety for GPU inference workloads.

---

*Configuration applied: October 5, 2025*  
*Standard timeout: 30s (66% reduction)*  
*Critical services: 60s with graceful handling*  
*Status: Ready for testing on next reboot*