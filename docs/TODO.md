# Implementation TODO

Work top to bottom. Finish one step, leave the app runnable, then start the next. Each step is sized for a single AI-assisted session.

A step is done when every box in it is checked, including the security box and the documentation box.

Source of truth for behavior: [requirements.md](requirements.md).

## Step 1 — Project initialization and basic UI

- [x] Add a Python 3 package layout: `app/`, `tests/`, pinned `requirements.txt`, `README.md`, and `.gitignore`.
- [x] Add a Flask app factory that serves one shared layout and a placeholder home page.
- [x] Add one stylesheet: readable type, generous spacing, a restrained palette, and static Healthy / Warning / Critical / Unreachable labels so status is color plus text.
- [x] Read the listen host and port from environment variables, with a local default.
- [x] Security: leave debug off unless an explicit environment flag enables it. Gitignore `.env`, database files, and key files. Commit no passwords, keys, or database.
- [x] Documentation: README lists the Python version and the commands to create a virtualenv, install dependencies, and open the placeholder page.

## Step 2 — Sign-in functionality and unit tests

- [ ] Add a sign-in page. Prefill the username with `admin` and leave the field editable. Include a password field.
- [ ] On startup, hash `ADMIN_PASSWORD` with Werkzeug’s salted PBKDF2. Compare sign-in input to that hash.
- [ ] On success, start a session and redirect to the placeholder home page. On failure, show one message: the username or password is incorrect.
- [ ] Require `SECRET_KEY` and `ADMIN_PASSWORD` before the app serves traffic.
- [ ] Add unit tests for a correct sign-in, an unknown username, a wrong password, a missing password, and the generic failure message. Tests supply their own fake secrets.
- [ ] Security: session cookie is HttpOnly. Logs, templates, and assertion messages omit the plaintext password and the hash input. Tests never read a real secret.
- [ ] Documentation: README describes `ADMIN_PASSWORD`, `SECRET_KEY`, the shared `admin` username, and how to run the unit tests.

## Step 3 — CI/CD with GitHub Actions

- [ ] Add `.github/workflows/ci.yml` on push and pull request. It installs pinned dependencies and runs the unit tests on a current Python 3.
- [ ] Add `.github/workflows/cd.yml` that, on a version tag, builds a source package and uploads it as a workflow artifact. The operator installs that artifact on an internal host.
- [ ] Pin action references. Set workflow `permissions` to `contents: read`.
- [ ] Security: workflows contain no passwords, SSH keys, or `SECRET_KEY` values. Test jobs inject only fake environment values. The CD job does not deploy to a server and does not contact monitored hosts.
- [ ] Documentation: README describes what each workflow runs, and that a green CI run is required before starting the next feature step.

## Step 4 — Sign-out, session lifetime, and attempt pause

- [ ] Add sign-out on every signed-in page. Signing out ends the session.
- [ ] Expire the session after 8 hours of inactivity.
- [ ] After five failed sign-in attempts in a row, pause further attempts from that browser session for 60 seconds.
- [ ] Send every route except sign-in back to the sign-in page when the session is missing or expired.
- [ ] Unit-test sign-out, idle expiry, the fifth-failure pause, and a blocked post during the pause.
- [ ] Security: the pause response uses the same generic sign-in error. The session cookie stays HttpOnly, and is marked Secure when the request is HTTPS.
- [ ] Documentation: README records the idle timeout and the pause rule.

## Step 5 — SQLite foundation and stored admin hash

- [ ] Open a SQLite file at a path from the environment. Create the file on first start.
- [ ] Store the admin password hash in that database. On startup, replace the stored hash when `ADMIN_PASSWORD` has changed.
- [ ] Keep server inventory and samples out of this step. One table for the account hash is enough.
- [ ] Unit-test fresh creation, restart with the same password, and restart with a new password.
- [ ] Security: the database stores the salted hash only. Gitignore the database file. Tests use a temporary database path.
- [ ] Documentation: README names the database path variable and states that the file holds a hash.

## Step 6 — Signed-in empty dashboard

- [ ] Replace the placeholder home page with the dashboard layout: page title, sign-out, and an add-server action.
- [ ] Show an empty state that says no servers are registered yet and offers the add action.
- [ ] Keep the add action as a link only. The form arrives in a later step.
- [ ] Security: the dashboard template renders no credentials and no sample payload from another system. The route stays behind the session check from Step 4.
- [ ] Documentation: add a short comment at the top of the dashboard template pointing to PRD section 7.1.

## Step 7 — Server records and secret encryption

- [ ] Add a `servers` table: display name, host, SSH port, SSH username, auth method, encrypted secret, and host-key columns.
- [ ] Encrypt the SSH secret with a key derived from `SECRET_KEY` before insert. Decrypt only inside the process that needs the secret.
- [ ] Enforce a unique display name in the schema.
- [ ] Unit-test round-trip encryption, unique display name, and default SSH port storage.
- [ ] Security: ciphertext is non-reversible from the database file without `SECRET_KEY`. Tests assert the plaintext secret is absent from the row. Logs omit the secret.
- [ ] Documentation: note the columns and the encryption rule in the README data section.

## Step 8 — Add-server validation

- [ ] Add the server form: display name, host, SSH port (default 22), SSH username, and auth method (password or private key).
- [ ] Validate required fields, unique display name, and an SSH port from 1 to 65535. Show field errors on the form.
- [ ] Save a valid server and return to the dashboard. The secret input is empty again after save.
- [ ] The dashboard lists saved servers by display name and address, still without live metrics.
- [ ] Unit-test each validation failure and one successful save.
- [ ] Security: the secret field is write-only. The list and the HTML response omit the secret and its ciphertext. Host and username are stored as data, never interpolated into a command in this step.
- [ ] Documentation: README lists the form fields and the validation rules.

## Step 9 — Edit server

- [ ] Add an edit form prefilled with display name, host, port, username, and auth method.
- [ ] Saving with a blank secret keeps the stored secret. Saving with a new secret replaces it.
- [ ] Unit-test keep-secret and replace-secret.
- [ ] Security: the edit page never echoes the current secret into HTML, attributes, or logs. A validation failure also leaves the secret out of the response.
- [ ] Documentation: README states the blank-secret edit rule.

## Step 10 — Remove server

- [ ] Add a remove action with an explicit confirmation step.
- [ ] Deleting a server removes its row and its stored secret.
- [ ] Unit-test confirm-and-delete, and test that cancel leaves the row in place.
- [ ] Security: the confirmation page identifies the server by display name and address only. The delete handler checks the session.
- [ ] Documentation: README describes remove and confirmation.

## Step 11 — Health labels

- [ ] Implement a pure function that maps CPU percent, memory percent, and poll success to Healthy, Warning, Critical, or Unreachable.
- [ ] Warning is 80% up to but not including 95%. Critical is 95% and above. The label uses the more severe of CPU and memory.
- [ ] Warning and critical text names the resource and the percent, for example `Memory 96%`.
- [ ] Unit-test the boundaries 79, 80, 94, 95, both resources elevated, and a failed poll.
- [ ] Security: the function accepts numbers and a status flag only. It has no I/O and no secret parameters.
- [ ] Documentation: comment the thresholds with a pointer to PRD section 7.2.

## Step 12 — Sample storage

- [ ] Add tables for poll status and metric samples, keyed by server, with timestamps stored in UTC.
- [ ] Record a failure category and time without deleting earlier samples.
- [ ] Unit-test insert, latest-sample lookup, and a failure that preserves the previous sample.
- [ ] Security: sample rows contain metrics only. Tests use a temporary database. Fixture data includes no real hostnames from the organization and no secrets.
- [ ] Documentation: README lists sample fields and the UTC rule.

## Step 13 — CPU and memory parsers

- [ ] Parse overall CPU busy percent from `/proc/stat` text.
- [ ] Parse memory used, total, and used percent from `/proc/meminfo` text, treating cache the way `free` does.
- [ ] Unit-test both parsers with checked-in fixture files under `tests/fixtures/`.
- [ ] Security: parsers accept text and return numbers. They do not open sockets or run commands.
- [ ] Documentation: fixture file headers name the source (`/proc/stat`, `/proc/meminfo`) and the expected figures.

## Step 14 — Load, uptime, and disk parsers

- [ ] Parse 1, 5, and 15 minute load averages and uptime from `/proc` text.
- [ ] Parse local filesystem rows (mount, size, used, available, percent) and drop `tmpfs` and `devtmpfs`.
- [ ] Unit-test a normal fixture and a fixture that contains only pseudo filesystems.
- [ ] Security: same rule as Step 13. Parser input is fixture text in tests.
- [ ] Documentation: note excluded filesystem types next to the disk parser.

## Step 15 — Network summary and rates

- [ ] Parse non-loopback interface counters and operational state.
- [ ] Derive link status: Up when any non-loopback interface is up, Down when none are.
- [ ] Compute total inbound and outbound rates from two successive counter samples. Return no rate for the first sample or across a gap.
- [ ] Unit-test Up, Down, loopback exclusion, a normal rate, and a gap.
- [ ] Security: rate math uses stored counters only. It does not read the host network itself.
- [ ] Documentation: state the units (bytes per second) beside the function.

## Step 16 — Process and port parsers

- [ ] Parse a process snapshot into the top 10 by CPU and the top 10 by memory: pid, user, CPU percent, memory percent, command name.
- [ ] Parse listening TCP and UDP sockets: local address, port, protocol, process name, and pid. Leave the process unknown when it is absent from the text.
- [ ] Unit-test ordering, the top-10 cutoff, both protocols, and a socket with no process name.
- [ ] Security: command names are stored as display text. Templates that later render them will escape output. Tests cover a command name that contains HTML characters and expect the raw characters preserved in the parsed data, not executed.
- [ ] Documentation: describe the unknown-process case in the parser docstring.

## Step 17 — Fixed read-only command set

- [ ] Define one constant command list for CPU, memory, load, uptime, network counters, disk, processes, and listening ports.
- [ ] Add a collector function that accepts already-fetched command output and returns one sample structure by calling the parsers.
- [ ] Unit-test the collector with fixtures only. This step does not open SSH.
- [ ] Security: review the command list and keep every entry read-only. The collector takes no host, username, or secret argument, so user input cannot be concatenated into a command here.
- [ ] Documentation: put the command list in `docs/collection.md` with the matching PRD section 10 purpose of each command.

## Step 18 — SSH transport

- [ ] Add a transport that connects with host, port, username, and either a password or a private key, runs the constant command list, and closes the session.
- [ ] Pass connection fields as SSH parameters. Build commands from the constant list only.
- [ ] Fail a poll that runs longer than 8 seconds and classify it as timed out.
- [ ] Map authentication failure, timeout, and connection refused to the plain-language categories from PRD section 7.1.
- [ ] Unit-test the transport with a fake SSH client: success, each failure category, timeout, and proof that a display name or host value containing shell metacharacters is never joined onto a command string.
- [ ] Security: disable interactive shell and file upload. Log the failure category and server id only. The fake client in tests records the command list it was given.
- [ ] Documentation: extend `docs/collection.md` with the timeout and the failure categories.

## Step 19 — Host-key pinning

- [ ] On the first successful SSH connection, store the server host key on the server row.
- [ ] On a later poll, accept only that key. A different key fails the poll as “host key changed” and writes no sample.
- [ ] Editing the server provides a way to accept a new key and store it in place of the old one.
- [ ] Unit-test first store, match, mismatch, and replace-on-edit.
- [ ] Security: use an explicit host-key policy. Auto-accept of any key is absent. The key is not a secret, and the secret is still omitted from the mismatch error.
- [ ] Documentation: `docs/collection.md` explains first-use trust and how an admin accepts a new key.

## Step 20 — Poller loop

- [ ] Run one background poller in the application process. Poll each registered server every 10 seconds.
- [ ] A single slow server fails at 8 seconds and the cycle continues with the other servers.
- [ ] Persist a successful sample or a failure category, and leave older samples in place on failure.
- [ ] Start the loop at process start; with an empty inventory it wakes, finds nothing, and sleeps.
- [ ] Unit-test scheduling against a fake clock and a fake transport, including one slow server among several fast ones.
- [ ] Security: the poller reads secrets only through the decrypt path inside the transport call. Exceptions are recorded as failure categories and are not written with secret text.
- [ ] Documentation: README describes the 10-second interval, the in-process poller, and the empty-inventory behavior.

## Step 21 — One-hour retention

- [ ] After each cycle, delete samples older than 60 minutes.
- [ ] Keep the server row, the secret, and the host key when samples are deleted.
- [ ] Unit-test that a 59-minute sample remains, a 61-minute sample is removed, and the server row remains.
- [ ] Security: the delete statement is scoped by timestamp. It does not take a table name or a clause from user input.
- [ ] Documentation: README states the 60-minute retention window.

## Step 22 — Dashboard metrics

- [ ] Render each server with health label, CPU, memory, highest filesystem use, inbound rate, outbound rate, and link status.
- [ ] Show Unreachable servers with the latest plain-language cause.
- [ ] Link each row to a detail URL. The detail page can be a stub until Step 23.
- [ ] Escape server names and error text in the template.
- [ ] Test the rendered dashboard with fixture samples for Healthy, Warning, Critical, and Unreachable.
- [ ] Security: view the page source in the test and assert secrets and ciphertext are absent. Confirm the page contains no button that restarts a service, edits a host file, or opens a shell.
- [ ] Documentation: note the dashboard columns in the README.

## Step 23 — Server detail page

- [ ] Show display name, address, SSH port, and the poll time of the latest sample.
- [ ] Show current CPU, memory, load, uptime, network summary, and each disk filesystem.
- [ ] Show both top-10 process lists and the listening-port table, including an unknown process when the pid is missing.
- [ ] Reuse the same health label as the dashboard.
- [ ] Test a populated server and an unreachable server that still shows its last good sample beside the failure.
- [ ] Security: the page is read-only. Template review confirms there is no command box and no host-mutating control. Process command text is escaped.
- [ ] Documentation: map each detail block to PRD section 7.1 in a short template comment.

## Step 24 — One-hour charts

- [ ] Add charts for CPU percent, memory percent, and total inbound and outbound rate over the last 60 minutes.
- [ ] Plot a missing poll as a gap.
- [ ] Hide a rate series until two successive samples exist.
- [ ] Test chart data for a full hour, a gap in the middle, and a single fresh sample.
- [ ] Security: chart data is same-origin JSON or inline data for that server only. The endpoint that feeds the chart checks the session. It returns metrics, never secrets.
- [ ] Documentation: describe the three series and the gap rule in the README.

## Step 25 — In-place refresh

- [ ] While the dashboard or detail page is open, refresh its figures within one poll interval without a full manual reload.
- [ ] Keep the signed-out user on the sign-in page if the session expires during refresh.
- [ ] Test that a refresh request without a session is rejected, and that a signed-in request returns the new sample.
- [ ] Security: the refresh endpoint is GET, checks the session, and returns the same escaped fields as the page. It is not a general query API.
- [ ] Documentation: README mentions the automatic refresh behavior.

## Step 26 — Units and local time

- [ ] Format CPU and memory as percents, disk and process memory as MiB or GiB, and network rates with an explicit per-second unit.
- [ ] Store timestamps in UTC and render them in the viewer’s local timezone, with the zone labeled.
- [ ] Unit-test formatting boundaries (bytes, large disk values) and a known UTC instant.
- [ ] Security: timezone formatting does not change who can see a page. Formatting helpers stay pure.
- [ ] Documentation: README lists the units and the timezone display rule.

## Step 27 — Acceptance pass

- [ ] Walk PRD section 14 and check each criterion against the running app and the test suite.
- [ ] Add any missing test that section 14 still lacks, especially: signed-out visitors see no server data; ten servers stay on a 10-second cadence with the fake transport; removing a server deletes its samples and its secret.
- [ ] Security: repeat a secret scan of logs, HTML, and the SQLite file during the acceptance run. Confirm host-key mismatch and bad SSH credentials surface as categories and leave prior samples in place.
- [ ] Documentation: add `docs/acceptance.md` with the ten PRD criteria and the test or manual check that covers each one. Link it from the README.

## Working agreement

- [ ] Keep one step in progress at a time.
- [ ] Run the unit tests at the end of every step before checking its boxes.
- [ ] Treat a new test as part of the step that introduces the behavior, and keep GitHub Actions green.
- [ ] Leave Windows hosts, extra user accounts, SSO, email or webhook alerts, agents, retention past 60 minutes, custom thresholds, and any control that changes a monitored host out of this list. Those stay deferred in the PRD.
