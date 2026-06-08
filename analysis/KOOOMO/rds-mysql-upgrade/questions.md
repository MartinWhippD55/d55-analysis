# Questions & Review Notes: RDS MySQL Upgrade

## Strategy Validation

The read replica upgrade + promote approach is an **AWS-documented strategy** for RDS MySQL (not Aurora-specific). AWS explicitly documents this as the reduced-downtime upgrade path for RDS MySQL. Replication continues to work cross-version (5.7 source → 8.0 replica), allowing the replica to stay in sync until promotion.

Reference: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.MySQL.ReducedDowntime.html

## Key Feedback

1. **Do the replica upgrades BEFORE the maintenance window** — upgrading 5.7→8.0→8.4 can take 30–60+ min depending on DB size. Only the promote + DNS switch should happen during downtime.
2. **Verify replication lag = 0** before promoting (`SHOW REPLICA STATUS`, check `Seconds_Behind_Master`).
3. **Lower DNS TTL** on `kooomo-db.kooomo.cloud` to 60s a day or two before migration.
4. **Take the backup first** — before any replica/upgrade work, not at step 6.
5. **Parameter group** — MySQL 8.0/8.4 needs its own parameter group on the replica.
6. **Connection pools** — app servers may cache DNS; may need restart after CNAME switch.
7. **Multi-AZ** — enable on the new instance post-promotion if current instance uses it.
8. **Rollback plan** — if e2e fails, switch DNS back to old instance (still running). Define the point of no return.

## Questions for Kooomo

1. DB size? (affects upgrade duration)
2. Is current instance Multi-AZ?
3. Current DNS TTL?
4. Did they test the upgrade *path* (replica upgrade) or just build dev fresh on 8.4?
5. Rollback plan if e2e fails?
6. Any stored procedures/triggers using deprecated 5.7 syntax?
7. Do they want us on-call or actively performing steps?
