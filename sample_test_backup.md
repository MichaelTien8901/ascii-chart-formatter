# Sample Architecture Diagram

Here's a system overview:

```
+------------------------+
| API Gateway            |
+------------------------+
| Authentication    |
+------------------------+
| Request Router         |
+------------------------+
```

## Data Flow

The data flows through these components:

```
+------------------+     +------------------+
| Frontend App     |     | Mobile Client    |
+------------------+     +------------------+
        |                        |
        v                        v
+------------------+     +------------------+
| Load Balancer    |       | CDN Cache          |
+------------------+     +------------------+
```

## Nested Architecture

```
+--------------------------------------+
| Kubernetes Cluster                   |
|                                      |
|  +----------------------------+      |
|  | Service Mesh               |      |
|  |                            |      |
|  |  +------------------+      |      |
|  |  | Microservice A   |      |      |
|  |  +------------------+      |      |
|  |  +------------------+      |      |
|  |  | Microservice B   |      |      |
|  |  +------------------+      |      |
|  +----------------------------+      |
+--------------------------------------+
```

## Unicode Stacked Boxes (shared borders)

```
┌────────────────────────┐
│ Request Received       │
├────────────────────────┤
│ Validate Input    │
├────────────────────────┤
│ Process Business Logic  │
├────────────────────────┤
│ Format Response        │
└────────────────────────┘
```

## Unicode Side-by-Side

```
┌──────────────────┐     ┌──────────────────┐
│ Auth Service     │     │ User Database    │
└──────────────────┘     └──────────────────┘
        │                        │
        ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│ Token Generator    │       │ Session Store      │
└──────────────────┘     └──────────────────┘
```

## Mixed ASCII + Unicode Pipeline

```
+----------------+     ┌────────────────┐     +----------------+
| Raw Input       | --> │ Parser          │ --> | AST Builder    |
+----------------+     └────────────────┘     +----------------+
       |                       |                       |
       v                       v                       v
+----------------+     ┌────────────────┐     +----------------+
| Lexer          |     │ Optimizer        │     | Code Generator  |
+----------------+     └────────────────┘     +----------------+
```

## Deeply Nested Unicode

```
┌──────────────────────────────────────────┐
│ Cloud Infrastructure                      │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │ Virtual Private Cloud            │    │
│  │                                  │    │
│  │  ┌────────────────────────┐      │    │
│  │  │ Container Orchestrator  │      │    │
│  │  │                        │      │    │
│  │  │  ┌──────────────┐      │      │    │
│  │  │  │ App Pod        │      │      │    │
│  │  │  └──────────────┘      │      │    │
│  │  │  ┌──────────────┐      │      │    │
│  │  │  │ DB Pod       │      │      │    │
│  │  │  └──────────────┘      │      │    │
│  │  └────────────────────────┘      │    │
│  │                                  │    │
│  └──────────────────────────────────┘    │
│                                          │
└──────────────────────────────────────────┘
```

## Three-Column Layout

```
+------------+     +------------+     +------------+
| Web Server  |     | App Server  |     | DB Server  |
| (nginx)    |     | (node.js)   |     | (postgres)  |
+------------+     +------------+     +------------+
      |                  |                  |
      v                  v                  v
+------------+     +------------+     +------------+
| SSL Term   |     | Auth MW      |     | Connection  |
|            |     |             |     | Pooler      |
+------------+     +------------+     +------------+
```

## Event-Driven Architecture (ASCII)

```
+-------------------+
| Event Producer     |
+-------------------+
         |
         v
+-------------------+
| Message Queue     |
+-------------------+
    |           |
    v           v
+--------+  +--------+
| Worker  |  | Worker  |
| Pool A |  | Pool B  |
+--------+  +--------+
    |           |
    v           v
+-------------------+
| Result Aggregator  |
+-------------------+
         |
         v
+-------------------+
| Notification Svc  |
+-------------------+
```

## Event-Driven Architecture (Unicode)

```
┌───────────────────┐
│ Event Producer     │
└───────────────────┘
         │
         ▼
┌───────────────────┐
│ Message Queue     │
└───────────────────┘
    │           │
    ▼           ▼
┌────────┐  ┌────────┐
│ Worker  │  │ Worker  │
│ Pool A │  │ Pool B  │
└────────┘  └────────┘
    │           │
    ▼           ▼
┌───────────────────┐
│ Result Aggregator  │
└───────────────────┘
         │
         ▼
┌───────────────────┐
│ Notification Svc  │
└───────────────────┘
```

## Nested with Side-by-Side Inside

```
+------------------------------------------+
| Deployment Pipeline                       |
|                                          |
|  +----------------+     +-------------+  |
|  | Build Stage     |     | Test Stage   |  |
|  +----------------+     +-------------+  |
|         |                      |         |
|         v                      v         |
|  +----------------+     +-------------+  |
|  | Docker Build   |     | Integration  |  |
|  |               |     | Tests        |  |
|  +----------------+     +-------------+  |
|                                          |
+------------------------------------------+
         |
         v
+------------------------------------------+
| Production Deploy                        |
+------------------------------------------+
```

## Adjacent Boxes (no gap between them)

```
+------++------+
| Left  || Right |
+------++------+
```

## T-Junction Border (single wide box)

```
+----+----+----+
| spanning box  |
+----+----+----+
```

## Tab Characters in Content

```
+------------------+
|	Indented	|
|		Double	|
| Normal           |
+------------------+
```

## CJK / Fullwidth Content

```
+--------------------+
| 日本語テスト          |
| English Text       |
| 中文测试              |
+--------------------+
```

## Content Wider Than Box

```
+------+
| This content is much wider than the border |
+------+
```

## Tilde Code Fence

~~~
+--------+
| tilde   |
| fence  |
+--------+
~~~

## Unclosed Code Fence

```
+--------+
| no      |
| closing |
+--------+

## Mixed-Weight Box Drawing (double/light mix)

╒══════════════╕
│ Mixed weight  │
╘══════════════╛

## Dashed Line Borders

┌┄┄┄┄┄┄┄┄┄┄┄┄┄┄┐
┆ Dashed box     ┆
└┄┄┄┄┄┄┄┄┄┄┄┄┄┄┘

## Wide Search Window (pipe far from expected)

```
+----------+
| drifted far right              |
| normal   |
+----------+
```

## Regular Markdown Table (should not be changed)

| Component | Status | Version |
|-----------|--------|---------|
| API       | Active | 2.1.0   |
| DB        | Active | 5.7.0   |

## Another Table (should not be changed)

| Metric      | Value | Trend |
|-------------|-------|-------|
| Latency     | 42ms  | Down  |
| Throughput  | 1.2k  | Up    |
| Error Rate  | 0.01% | Flat  |
