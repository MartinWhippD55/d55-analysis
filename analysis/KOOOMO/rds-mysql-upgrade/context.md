# RDS MySQL Upgrade: 5.7 → 8.4 (Production)

## Background

Kooomo wants to remove extended MySQL 5.7 support for their production RDS instance (`kooomo-rds-prod`) to save ~$800/month. They've been testing MySQL 8.4 on dev environments for several months without issues.

## Proposed Plan (from Kooomo)

1. Choose a low-traffic maintenance window (6 AM or midnight)
2. Notify clients of maintenance date, time, and duration
3. Create a read replica of `kooomo-rds-prod`
4. Modify replica → upgrade to MySQL 8.0 (intermediate step, can't go direct to 8.4)
5. Modify replica → upgrade to MySQL 8.4
6. Create a backup of the current database
7. Stop cron jobs and workers
8. Set maintenance page (allow specific IPs)
9. Promote the MySQL 8.4 replica to primary (~2 min)
10. Update Route 53 CNAME `kooomo-db.kooomo.cloud` to new instance endpoint
11. Test new instance (e2e)
12. Remove maintenance page
13. Start cron jobs and workers
14. Enable delete protection on new instance
15. Disable delete protection on old instance and stop it
16. Notify customers of maintenance completion

## Key Details

- Current instance: `kooomo-rds-prod` (MySQL 5.7 with extended support)
- Target version: MySQL 8.4
- DNS: `kooomo-db.kooomo.cloud` (Route 53 CNAME)
- Dev testing: completed successfully
- Cost saving: ~$800/month

## Status

- [ ] Review plan and provide feedback
- [ ] Confirm availability for migration support
