# Resolving `OSError: [Errno 28] No space left on device` During `pip install` on Google Compute Engine

This guide covers how to diagnose, remediate, and prevent disk exhaustion on Google Compute Engine (GCE) virtual machines when Python package installations fail with `OSError: [Errno 28]`. All remediation steps rely exclusively on Bash commands so that you can automate the workflow in shell scripts or remote sessions without opening editors.

---

## 1. Why the Error Happens

### 1.1 Temporary workspace pressure

`pip` downloads archives, extracts them, and then builds wheels inside a temporary workspace (usually `/tmp`). Packages such as `torch`, `transformers`, and GPU wheels like `nvidia-cufft-cu12` can allocate several gigabytes of scratch space. When `/tmp` is mounted on a small partition or RAM-backed `tmpfs`, even a VM that appears to have free disk can fail mid-install.

### 1.2 Root filesystem exhaustion

Minimal GCE images often ship with 10 GB boot disks. System logs, package caches, Docker layers, orphaned virtual environments, and old kernels quickly eat into the root filesystem (`/`). Once the filesystem reaches 100 % usage, any additional write—including `pip` builds—triggers `Errno 28`.

### 1.3 Cache, log, and artifact buildup

Repeated experiments accumulate gigabytes of cached wheels, apt artifacts, container layers, and build directories under `$HOME`, `/var`, and `/opt`. Without periodic pruning the VM eventually runs out of space even if the initial install succeeded.

---

## 2. Diagnose Disk Usage with Bash

Run the following commands in sequence to identify the pressure point before deleting anything.

### 2.1 Inspect mounted filesystems

```bash
df -h
```

Focus on `/`, `/tmp`, `/var`, `/home`, and any data disks.

### 2.2 Review block devices and partitions

```bash
lsblk
sudo fdisk -l   # or: sudo parted -l
```

These commands reveal the underlying disk geometry and confirm whether a partition can be expanded.

### 2.3 Identify large directories

```bash
sudo du -h --max-depth=1 / \| sort -hr \| head -20
```

Repeat with `/var`, `/home/<user>`, and any suspicious mount points.

### 2.4 Surface oversized files

```bash
sudo find / -xdev -type f -size +100M -exec du -sh {} + | sort -hr | head -20
```

`-xdev` prevents the command from traversing additional filesystems such as attached data disks.

### 2.5 Optional interactive inspection

Install `ncdu` if you prefer a navigable terminal UI:

```bash
sudo apt-get update
sudo apt-get install -y ncdu
sudo ncdu /
```

---

## 3. Free Space Without Editors

Use the following Bash-only one-liners to reclaim space. Run the commands that match your environment and then re-check disk usage.

| Target | Command | Notes |
| --- | --- | --- |
| Apt cache | `sudo apt-get clean` | Removes all cached `.deb` archives. |
|  | `sudo apt-get autoclean` | Removes obsolete packages only. |
|  | `sudo apt-get autoremove --purge` | Purges auto-installed packages and old kernels. |
| Pip cache | `python3 -m pip cache purge` | Works with pip ≥ 20.1. |
|  | `rm -rf ~/.cache/pip` | Safe fallback when purge is unavailable. |
| General caches | `rm -rf ~/.cache/* ~/.local/tmp/*` | Clears per-user caches and temp directories. |
| User trash | `rm -rf ~/.local/share/Trash/*` | Frees graphical trash bins. |
| System logs | `sudo journalctl --vacuum-time=2d` | Shrinks journald history to two days. |
|  | `sudo rm -rf /var/log/*.gz /var/log/*.1 /var/log/*.[0-9]` | Removes rotated logs. |
| Docker artifacts | `docker system prune -af --volumes` | Deletes unused images, containers, networks, and volumes. |
|  | `sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log` | Clears oversized container logs. |
| Temporary directories | `sudo rm -rf /tmp/*` | Clean cautiously on single-user systems. |
| Old kernels | `dpkg -l 'linux-image*' \| grep '^ii'` | Audit installed kernels. |
|  | `sudo apt-get autoremove --purge` | Removes unused kernels automatically. |

> **Tip:** Always double-check the command output, especially when pruning Docker images or kernels, to avoid deleting active resources.

---

## 4. Work Around `/tmp` Limitations

### 4.1 Redirect temporary files for a single install

```bash
mkdir -p "$HOME/tmp_install"
TMPDIR="$HOME/tmp_install" pip install --no-cache-dir torch transformers nvidia-cufft-cu12
```

Setting `TMPDIR` ensures `pip` extracts build artifacts on a filesystem with sufficient space, while `--no-cache-dir` prevents wheel caching.

### 4.2 Persistently export `TMPDIR`

Add the export to your shell session or automation script:

```bash
export TMPDIR="$HOME/tmp_install"
```

### 4.3 Remount a larger `/tmp`

When `/tmp` is a `tmpfs` with limited capacity, remount it with more space (requires adequate RAM or swap):

```bash
sudo mount -o remount,size=10G /tmp
```

The change lasts until reboot. Permanent adjustments require editing `/etc/fstab`, which is outside this Bash-only scope.

---

## 5. Expand a GCE Persistent Disk

When cleanup is insufficient, resize the boot disk. The process is safe and usually does not require a reboot.

1. **Resize the disk from Cloud Shell or your local workstation:**
   ```bash
   gcloud compute disks resize <disk-name> --size=<new-size-gb> --zone=<zone>
   ```

2. **SSH into the VM and install partition utilities if needed:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y cloud-guest-utils
   ```

3. **Grow the root partition:**
   ```bash
   sudo growpart /dev/sda 1
   ```

4. **Expand the filesystem:**
   - ext4:
     ```bash
     sudo resize2fs /dev/sda1
     ```
   - XFS:
     ```bash
     sudo xfs_growfs -d /
     ```

5. **Verify capacity:**
   ```bash
df -h
lsblk
```

Adjust device names if your root disk differs (e.g., `/dev/sdb`).

---

## 6. Attach and Mount an Additional Disk

For large datasets or scratch space, attach a secondary persistent disk and mount it under `/mnt/data`.

```bash
# Create and attach the disk
gcloud compute disks create data-disk --size=100GB --zone=<zone>
gcloud compute instances attach-disk <instance-name> --disk=data-disk --zone=<zone>

# Inside the VM
sudo lsblk                             # confirm device name (e.g., /dev/sdb)
sudo mkfs.ext4 -m 0 -F -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/sdb
sudo mkdir -p /mnt/data
sudo mount -o discard,defaults /dev/sdb /mnt/data
sudo chmod a+w /mnt/data

df -h | grep /mnt/data
```

To remount automatically after reboot, add an `/etc/fstab` entry using the disk's UUID (not covered here per the no-editor requirement).

---

## 7. Preventative Maintenance for AI Workloads

- **Provision larger boot disks by default.** Start new AI-focused instances at 20 GB or more to avoid repeated resizing.
- **Schedule periodic cleanups.** Add a cron job that runs `apt-get clean`, clears pip caches, and prunes Docker artifacts weekly:
  ```bash
  (crontab -l 2>/dev/null; echo '0 3 * * 0 apt-get clean && apt-get autoremove --purge && python3 -m pip cache purge && docker system prune -af --volumes') | crontab -
  ```
- **Monitor disk usage.** Incorporate `df -h` or `du -sh` checks in monitoring scripts; alert before utilization reaches 80 %.
- **Clean virtual environments and build directories.** Delete unused virtualenvs and `build/` artifacts once experiments finish.
- **Install large packages individually.** Installing heavyweight dependencies one at a time simplifies troubleshooting and frees space sooner.
- **Use `--no-cache-dir` by default for heavyweight installs.** Especially valuable on shared CI workers or ephemeral build agents.

---

## 8. Troubleshooting GPU Package Installs

- **Verify wheel availability.** If `pip` reports 404 errors for `nvidia-*` packages, confirm the package exists for your Python version and architecture.
- **Clean half-downloaded wheels.** Remove stale files from `~/.cache/pip` before retrying a failed install.
- **Check `/var/log/syslog` or `dmesg`.** Disk and memory pressure can cause abrupt termination; logs reveal whether the kernel killed the process.
- **Pin compatible versions.** Combine GPU packages with the CUDA toolkit versions recommended by PyTorch or TensorFlow release notes to avoid repeated reinstall attempts.

---

## 9. Quick Reference

| Action | Command |
| --- | --- |
| Show free space | `df -h` |
| Largest directories (root) | `sudo du -h --max-depth=1 / \| sort -hr \| head -20` |
| Largest files | `sudo find / -xdev -type f -size +1G -exec du -sh {} + \| sort -hr \| head` |
| Clear apt cache | `sudo apt-get clean && sudo apt-get autoclean` |
| Purge pip cache | `python3 -m pip cache purge` |
| Prune Docker | `docker system prune -af --volumes` |
| Redirect pip temp directory | `TMPDIR=$HOME/tmp_install pip install --no-cache-dir <pkg>` |
| Resize disk (Cloud Shell) | `gcloud compute disks resize <disk> --size=<GB> --zone=<zone>` |
| Expand partition (VM) | `sudo growpart /dev/sda 1` |
| Resize ext4 filesystem | `sudo resize2fs /dev/sda1` |
| Mount new disk | `sudo mount -o discard,defaults /dev/sdb /mnt/data` |

---

## 10. Key Takeaways

1. Combine `df`, `du`, and `find` to pinpoint the exact storage pressure before deleting files.
2. Automate cache and log cleanup so that routine package installs do not fail unexpectedly.
3. Redirect `TMPDIR` or remount `/tmp` when temporary space is the bottleneck.
4. Resize the persistent disk or attach additional volumes for long-term scalability.
5. Harden your AI workstation with monitoring, cron-driven maintenance, and consistent package management hygiene.

By treating disk space as a first-class resource, you can keep GCE-based AI environments stable and avoid future `Errno 28` interruptions.
