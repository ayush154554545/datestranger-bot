# High Scale Architecture (50,000+ Users / 1,000+ Concurrent)

## 1. Capacity Targets & Bottleneck Analysis

```text
Registered Users Target: 50,000+
Concurrent Active Users: 1,000+
Peak Message Relay Throughput: ~250 msg/sec
Peak Matching Request Throughput: ~50 matches/sec
```

---

## 2. Component Scaling Architecture

```mermaid
graph TD
    TG["Telegram API Users"] --> LB["Load Balancer"]
    LB --> BOT1["Bot Instance 1"]
    LB --> BOT2["Bot Instance 2"]
    
    BOT1 & BOT2 --> REDIS["Redis Cluster (Queue, Locks, Cache)"]
    BOT1 & BOT2 --> PG["Supabase PostgreSQL (Pooled via Supavisor)"]
    
    BOT1 & BOT2 --> WQ["Redis Worker Queue"]
    WQ --> MW["Media Workers"]
    WQ --> DW["Discord Archival Workers"]
    
    MW --> R2["Cloudflare R2 Storage"]
```

---

## 3. Bottleneck Mitigations
1. **Database Connection Limits**: Supabase database connection pooler (`Supavisor`) manages thousands of lightweight API connections.
2. **Matching Queue Bottleneck**: Redis candidate queue handles sub-millisecond filtering before atomic PostgreSQL match creation (`SKIP LOCKED`).
3. **Media Egress & Storage**: Direct Cloudflare R2 uploads bypass bot server CPU and memory. Egress bandwidth is free.
