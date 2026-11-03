# Demo Monitoring Infrastructure for Linux Servers

**Status:** Draft for the demo  
**Audience:** Internal infrastructure and application teams  
**Stack:** Python, Flask

## 1. Summary

Build a small internal web application that shows live health for Linux servers, so L1, L2, and L3 staff can see CPU, memory, network, disk, load, uptime, top processes, and listening ports without signing in to each host.

The demo supports up to 10 servers. One shared `admin` account signs in. That account can register servers. Every monitoring screen is read-only: the product displays data and does not change anything on the monitored hosts.

The application collects data by SSH. It polls each server on a fixed schedule, keeps about one hour of samples, and draws short trend charts next to the current values. Health is shown on screen with fixed CPU and memory thresholds. There is no email, ticket, or webhook notification in this demo.

## 2. Problem

Today, engineers open a shell on each server to answer basic questions:

- How busy is the CPU right now?
- How much memory is in use?
- Is the network link up, and what is the traffic rate?
- Which ports are listening, and which process owns them?
- Is disk space getting tight?
- What is the load and uptime, and which processes are using the most CPU or memory?

That workflow is slow, easy to do inconsistently, and it requires host login rights for every person who only needs to look.

## 3. Users

| Team | What they need from this demo |
| --- | --- |
| L1 | A quick view of whether a server is reachable and which resource looks hot. |
| L2 | Current figures plus the last hour, so a spike can be compared with “right now.” |
| L3 and application developers | Process and listening-port detail when a service looks unhealthy. |

All of these groups use the same sign-in for the demo. The product does not create separate L1, L2, or L3 accounts.

## 4. Decisions locked for this demo

| Topic | Decision |
| --- | --- |
| Sign-in | One shared account. The username is `admin`. |
| Password | Stored only as a salted hash. The plaintext password is supplied at startup and is never written to the database or source code. |
| Who can add servers | The `admin` account. |
| What “read-only” means | Monitoring screens cannot restart services, edit files, open a shell, or push configuration to a host. |
| Collection | The Flask app opens SSH to each server and runs a fixed set of read-only commands. |
| Credentials | SSH user and secret (password or private key) are stored with that server’s record. |
| Time window | Current values, plus charts for the last 60 minutes. |
| Network view | Total inbound rate, total outbound rate, and link status (up or down). |
| Health warnings | On-screen only, from fixed CPU and memory thresholds. |
| Capacity | Designed and accepted for fewer than 10 servers. |

## 5. Goals

1. Show live server health in a browser within one sign-in.
2. Make the interface clear to L1 on first use, and detailed enough for L2 and L3 on a server page.
3. Add a Linux server from the UI and start seeing its metrics after the next successful poll.
4. Keep host access limited to read-only collection over SSH.
5. Leave a one-hour trail so a recent change is visible without a separate monitoring stack.

## 6. Demo scope

**In this demo**

- Sign-in and sign-out for the shared `admin` account.
- A server inventory: add a Linux server, correct its connection details, and remove it from monitoring.
- A dashboard of every registered server with a health label.
- A server detail page with current metrics, one-hour charts, top processes, and listening ports.
- Automatic polling and a one-hour sample history.
- On-screen warning and critical labels for CPU and memory.
- A clear unreachable state when SSH fails.

**Deferred**

- Windows or other operating systems.
- Per-person accounts, groups, and role-based access.
- Email, chat, webhook, or ticket alerts.
- An agent installed on the servers.
- Retention longer than 60 minutes, downsampling, or export.
- More than 10 servers, high availability, and multi-instance deployment.
- Changing host configuration from the UI.
- Custom thresholds per server.
- Authentication against company SSO.

## 7. User experience

The UI is a Flask-rendered web application with a single, consistent visual design: readable type, generous spacing, a restrained color set, and status color that is meaningful without being the only cue (each state also has a text label).

Screens are usable on a laptop browser at a typical operations desk. The demo does not need a native mobile app.

### 7.1 Screens

**Sign in**

- Username and password fields.
- Username is prefilled with `admin` and remains editable.
- A failed attempt shows a single message: the username or password is incorrect. The message does not say which field was wrong.
- After success, the browser lands on the dashboard.

**Dashboard**

- Lists each registered server: display name, address, health label, CPU, memory, disk (highest filesystem use), network rates, and link status.
- Unreachable servers stay visible and show the last error in plain language (“SSH authentication failed”, “timed out”, “connection refused”).
- Each row links to that server’s detail page.
- An obvious action adds a server.
- An empty state explains that no servers are registered yet and offers the add action.
- Values refresh on their own while the page stays open.

**Server detail**

- Identity: display name, address, SSH port, and poll time of the latest sample.
- Current CPU, memory, load average, uptime, network summary, and disk filesystems.
- Charts for CPU percent, memory percent, and total inbound and outbound rate across the last 60 minutes.
- Top processes by CPU and by memory.
- Listening ports: port, protocol (TCP or UDP), address, and owning process.
- The same health label as the dashboard.
- No command box, no “run this”, and no buttons that act on the host.

**Add or edit server**

- Display name.
- Host name or IP address.
- SSH port, default 22.
- SSH username.
- Authentication method: password or private key.
- The secret field is write-only. After save, the UI shows that a secret is stored and does not reveal it.
- Save validates required fields before attempting SSH.
- A successful save returns to the dashboard. The first sample appears after the next poll.
- Edit can replace the secret. Leaving the secret blank on edit keeps the stored secret.
- Remove asks for confirmation, then deletes the server and its samples.

**Sign out**

- Ends the session from any signed-in screen.

### 7.2 Health labels

Every server shows one label:

| Label | When it applies |
| --- | --- |
| Healthy | Latest poll succeeded, CPU is under 80%, and memory is under 80%. |
| Warning | Latest poll succeeded, and CPU or memory is at least 80% and under 95%. |
| Critical | Latest poll succeeded, and CPU or memory is at least 95%. |
| Unreachable | The latest poll did not return a sample. |

When both CPU and memory are elevated, the label uses the more severe of the two. Warning and critical copy names the resource, for example “Memory 96%”.

Disk, load, ports, and processes are shown as data. They do not change the health label in this demo.

## 8. Functional requirements

### 8.1 Sign-in

1. The only username the demo accepts is `admin`.
2. The operator provides the initial password in the `ADMIN_PASSWORD` environment variable when the process starts.
3. On startup the application stores a salted password hash and does not keep the plaintext password.
4. If `ADMIN_PASSWORD` is missing on a fresh install, the application refuses to serve sign-in until it is set.
5. Changing `ADMIN_PASSWORD` and restarting replaces the stored hash.
6. Sign-in creates a server-side session. The session cookie is HttpOnly.
7. A session ends on sign-out, and it expires after 8 hours of inactivity.
8. Every page except sign-in requires a valid session.
9. Five failed attempts in a row for the same browser session pause further attempts for 60 seconds.

### 8.2 Server inventory

1. A signed-in user can add a Linux server with the fields in section 7.1.
2. Display name must be unique among registered servers.
3. Host and SSH port are required. SSH port must be an integer from 1 to 65535.
4. The SSH username is required.
5. Exactly one secret is stored: a password or a private key.
6. The user can edit connection details and can remove a server.
7. Removing a server deletes its stored samples and its SSH secret.
8. The inventory is the only data the user can change. Metric samples are written by the poller.

### 8.3 Collection

1. A background poller runs inside the Flask application process.
2. The poll interval is 10 seconds for every registered server.
3. A poll that exceeds 8 seconds is failed as a timeout so one slow host does not stall the cycle.
4. Each poll opens SSH, runs only the read-only command set in section 10, then closes the session.
5. Commands are fixed by the application. User input is never concatenated into a shell command. Host, port, username, and secret are connection parameters only.
6. A failed poll records the failure category and timestamp and leaves previous samples in place.
7. Samples older than 60 minutes are deleted.

### 8.4 Display

1. Dashboard and detail pages show the latest successful sample and the latest poll status.
2. Charts cover the last 60 minutes and plot missing polls as gaps.
3. Rates are computed from counters on successive successful samples. The first sample after add or after a gap shows a current state and waits for a second sample before showing a rate.
4. The open dashboard and detail pages pick up new samples within one poll interval without a manual reload.
5. Numbers use units people can scan: percent for CPU and memory, mebibytes or gibibytes for disk and process memory, and bits or bytes per second for network rate, labeled with the unit.

## 9. Metrics

Collected on each successful poll.

| Metric | What the UI shows |
| --- | --- |
| CPU | Overall busy percent across all cores. |
| Memory | Used, total, and used percent. Cache may be excluded from “used” so the figure matches what operators expect from `free`. |
| Load | One, five, and fifteen minute load averages. |
| Uptime | Time since boot. |
| Network | Sum of inbound and outbound byte rates across non-loopback interfaces, plus whether at least one non-loopback interface is up. |
| Disk | Each mounted local filesystem: mount point, size, used, available, and used percent. Pseudo filesystems such as `tmpfs` and `devtmpfs` are omitted. |
| Processes | Top 10 by CPU and top 10 by memory: pid, user, CPU percent, memory percent, and command name. |
| Ports | Listening TCP and UDP sockets: local address, port, protocol, and process name with pid when the command is allowed to see it. |

Network “link status” is **Up** when any non-loopback interface is operationally up, and **Down** when none are.

## 10. Collection method

The poller uses SSH as the Linux monitoring user configured for that server. That account should be a dedicated, unprivileged user on the host. Privilege escalation is out of scope. If a port’s process name requires extra rights, the UI shows the socket and leaves the process as unknown.

The command set is read-only and limited to local inspection, equivalent to reading kernel and process information that these commands already expose:

- CPU, memory, load, and uptime from `/proc`
- Interface counters and link flags for the network summary
- Filesystem usage for local mounts
- A process snapshot sorted for the top-10 lists
- Listening sockets (`ss` or the same data from `/proc`)

The application rejects any path that would start an interactive shell, transfer files to the host, or change system state.

SSH host-key checking is on. The first successful connection stores the host key with the server record. A later key change fails the poll with a visible “host key changed” error until an admin edits the server and accepts the new key.

## 11. Security

1. Passwords are stored with a salted adaptive hash (Werkzeug’s salted PBKDF2, or bcrypt). Plaintext passwords are not logged.
2. SSH secrets are encrypted at rest with an application key from the `SECRET_KEY` environment variable. The database file alone is not sufficient to recover them.
3. `SECRET_KEY` is also the session signing key. Both `ADMIN_PASSWORD` and `SECRET_KEY` are required configuration and are absent from the repository.
4. Secrets are omitted from pages, logs, and error text.
5. Session cookies are HttpOnly. They are marked Secure when the app is served over HTTPS.
6. The demo is for an internal network. Browser access is limited to the teams who already share the `admin` password.
7. SSH from the app to the servers uses the stored account only for the command set in section 10.
8. Sign-in errors and poll errors stay generic enough that they do not reveal secret material. Poll errors may name the failure category so an operator can fix the inventory record.

## 12. Technical approach

| Piece | Choice |
| --- | --- |
| Language | Python 3 |
| Web | Flask, server-rendered templates |
| UI | Jinja templates, one shared stylesheet, and a small script that refreshes dashboard and detail data in place |
| Persistence | SQLite in a single file: account hash, servers, encrypted secrets, accepted host keys, and samples |
| SSH | A Python SSH client such as Paramiko |
| Process model | One web process and one poller thread or equivalent background worker in the same demo deployment |
| Configuration | Environment variables for `ADMIN_PASSWORD`, `SECRET_KEY`, the database path, and the listen address |

Suggested runtime shape for the demo:

- Listen on an internal interface and port chosen at deploy time.
- Create the SQLite file on first start.
- Hash `ADMIN_PASSWORD` before serving traffic.
- Start polling only after a server exists.

Dependencies and exact module layout belong in the implementation, as long as they stay inside this stack and do not add a separate frontend application.

## 13. Non-functional requirements

| Area | Requirement |
| --- | --- |
| Scale | Correct behavior from 1 through 10 servers. |
| Freshness | With all 10 servers reachable, each server gets a new sample about every 10 seconds. |
| History | 60 minutes of samples are queryable for charts. Older rows are removed. |
| Availability | A single process is acceptable. A poller failure is visible (stale poll time) and does not wipe inventory. |
| Browser | Current Chrome or Firefox. |
| Time | Timestamps are stored in UTC and shown in the viewer’s local timezone, with the zone labeled. |
| Privacy of the demo | No metric payload is sent to a third-party service. |

## 14. Acceptance criteria

1. Opening the app while signed out shows the sign-in page and no server data.
2. `admin` plus the configured password reaches the dashboard. Any other username or a wrong password stays on sign-in.
3. The database and logs contain a password hash, and they do not contain `ADMIN_PASSWORD` or an SSH secret in plaintext.
4. Adding a reachable Linux server with valid SSH details produces a Healthy, Warning, or Critical card after the next polls, with CPU, memory, load, uptime, disk, network summary, top processes, and listening ports populated from that host.
5. The detail page shows 60-minute charts for CPU, memory, and network rate once enough samples exist. A gap in polling is a gap in the chart.
6. CPU at 80–94% or memory at 80–94% shows Warning. CPU or memory at 95% or more shows Critical. Below 80% on both shows Healthy.
7. Stopping SSH, or using a bad password, shows Unreachable and a plain-language cause. Restoring access returns the server to a data-backed label without re-adding it.
8. The UI exposes no control that restarts a service, edits a file, or opens a shell on the host.
9. Editing a server updates how the next poll connects. Removing it drops the card, the samples, and the stored secret.
10. With 10 servers configured, polling continues on the 10-second cadence and the dashboard lists all 10.

## 15. Later phase ideas

These are recorded so the demo stays small. They are not commitments.

- Separate viewer accounts for L1, L2, and L3, with admin-only inventory changes.
- Company SSO in place of the shared password.
- Per-server thresholds and notification channels.
- Disk, load, and process restarts as inputs to the health label.
- An optional host agent where SSH is not allowed.
- Retention beyond one hour and a way to export samples.
