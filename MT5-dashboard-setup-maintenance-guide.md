# My MT5 Dashboard: Setup & Maintenance Guide

**Saved:** 7 November 2026  
**Purpose:** A read-only personal dashboard for reviewing an Exness MT5 account and trading activity. The dashboard does not place or close trades.

> **Privacy:** The dashboard has no login. Anyone who can access its Render URL can see the account balance, positions, and stored deals. A private GitHub repository does not make the website private. The write connection uses a secret, but that secret does not protect the dashboard's public read access.

## 1. How the system works

```text
MT5 on my Windows PC
  └─ DashboardSync-code EA (read-only)
       └─ sends snapshots about every 60 seconds
            ↓ HTTPS + bridge secret
Render web service: mt5dass.onrender.com
  ├─ serves the HTML/CSS/JavaScript dashboard
  └─ talks to Google Apps Script on the server side
            ↓ HTTPS + bridge secret
Google Apps Script web app
            ↓
Google Sheet: Account, Positions and Deals tabs
```

- **MT5 EA:** Reads the connected account, open positions, and buy/sell deals. It contains no trade-opening, closing, or modification functions.
- **Google Sheet:** Stores the latest account snapshot and positions, plus the accumulated synced deals.
- **Apps Script:** Checks the bridge secret and reads/writes the Sheet.
- **Render:** Runs the Node.js backend and serves the dashboard. It is a Web Service, not a Static Site.
- **GitHub:** Holds the Render source code in the private `mt5dass` repository.

The dashboard reads from the Sheet, not directly from MT5. Your PC must be on, MT5 must be connected, and the EA must be attached to a chart for new data to arrive.

## 2. Where things are

| Component | Location / settings |
|---|---|
| Dashboard | <https://mt5dass.onrender.com> |
| GitHub repository | Private repository `mt5dass` |
| Google Sheet | The spreadsheet with tabs `Account`, `Positions`, and `Deals` |
| Apps Script | The project containing `Code.gs`, deployed as a web app |
| MT5 source | `MQL5/Experts/DashboardSync-code.mq5` inside the MT5 data folder |
| Render type | Node web service; free instance selected during setup |

### Related files in this workspace

- Current fresh-start EA source: `DashboardFreshStart.txt`. Its contents were pasted into `DashboardSync-code.mq5` and compiled in MetaEditor. The older `DashboardSync.mq5` is the original pre-reset version; don't reinstall it if you want to keep the fresh-start behavior.
- Apps Script: `Code-with-test.gs` is the copy with the `testBridge` diagnostic function. The deployed project was updated after this test. `Code.gs` is the base copy without that test function.
- Render source: `server.js`, `index.html`, `style.css`, `app.js`, and `package.json`.

Workspace files are a reference copy. The actual running versions are in MT5, Google Apps Script, and the GitHub repository/Render. If you change those services later, update this reference too so the versions don't drift.

## 3. Secrets and configuration

Never put the secret, MT5 password, or Apps Script URL in GitHub or browser-side JavaScript. Don't send them in chat or screenshots. The website itself never needs an MT5 password.

### Apps Script → Project Settings → Script Properties

- `SPREADSHEET_ID` = ID of the Google Sheet.
- `BRIDGE_SECRET` = a long random secret.

### Render → Environment

- `APPS_SCRIPT_URL` = the deployed Apps Script web app URL ending in `/exec`.
- `BRIDGE_SECRET` = exactly the same secret as in Apps Script.

### MT5 EA Inputs

- **Dashboard URL** = `https://mt5dass.onrender.com` (no trailing slash).
- **Bridge secret** = exactly the same secret.

Keep the Google Sheet and Apps Script project private. People with Apps Script editor access may be able to see Script Properties. EA input values can also be visible to someone with access to your computer or screenshots.

### If the secret is exposed

1. Remove the sync EA from its chart temporarily.
2. Generate a new long random secret. Update `BRIDGE_SECRET` in Apps Script Script Properties and Render Environment. Restart/redeploy Render if prompted.
3. Reattach the EA and enter the new secret in its Inputs. Verify syncing.
4. Never paste the new value into the repository or chat.

This protects the write bridge, not the public dashboard. If you need financial data to be private, add proper authentication/authorization to the dashboard and its data endpoint before using it.

## 4. Normal day-to-day use

1. Open MT5 on Windows and connect to the intended trading account.
2. Keep `DashboardSync-code` attached to its chart. The default sync interval is 60 seconds. Other EAs can run on separate charts.
3. Open the Render dashboard and click **Refresh**. The dashboard may show cached data for up to about 30 seconds; Render's free service can also take time to wake up.
4. Check the **Synced** timestamp, balance/equity, and open positions against MT5. Account snapshot time is UTC; deal times are broker-server time.
5. When the computer or MT5 is off, data won't update. Some missed deals may be picked up later within the configured lookback and record limit, but complete catch-up is not guaranteed.

The MT5 mobile app can still be used for trading; desktop MT5 should receive those transactions when connected. MT5 mobile alone cannot run this EA.

## 5. Fresh-start behavior and limitations

The current EA was changed after the original history was cleared. It creates a fresh-start cutoff when it first starts while connected, and saves it in an MT5 terminal global variable named `DashboardFreshStart_` followed by the account login. It imports only buy/sell deals at or after that cutoff, subject to the history lookback and count limits. Current balance and already-open positions are still displayed.

- The cutoff is local to that particular MT5 terminal and account. A different terminal, a new installation, or a different account will establish its own cutoff.
- Terminal global variables expire after four weeks without access; the running EA normally reads the variable on each sync. If the terminal is left unused long enough or its global variable is deleted, the EA can create a new cutoff later, potentially missing deals in between. See MQL5 terminal global variables.
- The cutoff uses `TimeTradeServer()`, which is estimated using the computer's time settings. Keep the Windows clock accurate; see MQL5 `TimeTradeServer`.
- Trades/deals made before the EA was reattached are excluded by design. A position opened before the cutoff but closed after it may contribute a closing deal without its original opening deal or opening costs.
- With defaults, each sync considers at most 300 newest buy/sell deals within 30 days. The EA permits `MaxDeals` up to 1000 and `HistoryDays` up to 3650, but increasing them does not guarantee complete import or catch-up. If more than the limit occur between syncs, or MT5 is offline beyond the lookback, some deals can be missed. Past records already stored in the Sheet are retained on later syncs.
- The sheet and dashboard track individual deals/fills, not fully reconstructed trades. Partial closes can create multiple closing deals. Closed-deal win rate uses positive profit + commission + swap on closing deals; zero is not counted as a win. Opening costs aren't allocated to closes. Net deal P/L sums profit, commission, and swap on stored buy/sell deals, and excludes other deal types such as deposits and withdrawals. It can differ from the broker's report.
- Currency is reported as MT5 provides it (for example, USC). Don't assume a USC amount is a USD amount. Check the broker's account denomination and conversion.

## 6. Updating the dashboard or backend

- Visual changes: `index.html` = structure; `style.css` = styling; `app.js` = displayed data and calculations.
- Backend changes: `server.js` handles requests, the Apps Script connection, caching, and write authentication. `package.json` defines the Node start command.

1. Edit the relevant file in the GitHub `mt5dass` repository, or upload an updated file with the same name.
2. Commit the change. Render normally redeploys when the linked branch changes; check **Render → Deploys**. If automatic deployment is off, trigger a manual deploy.
3. Open the dashboard, refresh it, and check Render logs if needed.
4. Keep secrets in Render Environment, not in the repository. A private repository still doesn't protect anything sent to a browser.

## 7. Updating Apps Script

1. Edit and save the project code in Apps Script.
2. In **Deploy → Manage deployments**, edit the existing web app (pencil icon), choose **New version**, and deploy. Saving the editor code alone does not update the deployed web app.
3. Web app settings used here: **Execute as Me**, access **Anyone** so Render can make requests. The script's bridge secret is required for its POST actions. Keep the `/exec` URL in Render Environment.
4. Test the dashboard. The editor-only `testBridge` function can test whether the current editor code reads the Sheet using its own Script Properties; it does not prove that the deployed version or Render is working.

`setupSheets` creates the managed tabs/headers if the relevant sheet is empty. Don't run an unrelated script or edit/remove the `Account`, `Positions`, or `Deals` headers without understanding the code.

## 8. Updating the EA

1. In MT5, use **File → Open Data Folder → MQL5 → Experts** to locate the EA. Stop/remove the sync EA before replacing it.
2. Open `DashboardSync-code.mq5` in MetaEditor. Replace or edit the code and press **F7 / Compile**. Check for 0 errors; troubleshoot any warnings.
3. In MT5 Navigator, refresh Expert Advisors and attach the EA to a chart. Verify the URL and secret in Inputs; don't show the secret in screenshots.
4. Confirm **Tools → Options → Expert Advisors → Allow WebRequest for listed URL** includes `https://mt5dass.onrender.com`. This EA does not require permission to place trades.
5. Check MT5's **Toolbox → Experts** tab for fresh-start and sync messages, wait at least one interval, then refresh the dashboard.

## 9. If I want another fresh start

> **Warning:** This is destructive for the dashboard's stored deal records. It does not erase broker or MT5 history. Back up the Sheet first if there is any chance you might want the records. Do not delete records until you're sure.

1. Remove `DashboardSync-code` from its chart so it can't sync while resetting.
2. In Google Sheets, clear only the data in the `Deals` tab below row 1; keep the column headers and tab. If headers are accidentally cleared and the tab is empty, run `setupSheets` from the Apps Script editor to restore them.
3. In the relevant MT5 terminal, open **Tools → Global Variables** (usually F3). Locate the variable named `DashboardFreshStart_` followed by the relevant account login, and delete only that specific variable. Do not delete other EAs' variables. This resets the local cutoff.
4. Reattach the current fresh-start EA to the intended account. When connected, it establishes a new cutoff; trades between removal and this new cutoff are excluded. Confirm the Experts log, wait for a sync, and check the dashboard reports zero stored deals until a new one arrives.

Account totals and existing open positions are not cleared by this process. If an older position is closed after the new cutoff, its closing deal can still appear.

## 10. Troubleshooting

| Symptom | Check |
|---|---|
| Dashboard says waiting for first MT5 sync | Make sure the EA is attached, account connected, URL/secret correct, and WebRequest URL allowed. Wait at least 60 seconds, then check MT5 Toolbox → Experts. |
| Dashboard data is stale | Check the sync timestamp, MT5 connection and PC uptime; check the EA's Experts log. Render may be waking up; the backend also caches reads briefly. |
| Render log says Apps Script returned HTTP 401 | Check the deployed `/exec` URL and web app access settings, including execution as the owner and anonymous access. Do not share the URL in chat. |
| Render says HTML/Unexpected token `'<'` instead of JSON | The Apps Script endpoint returned HTML, possibly due to an old deployment or an error. Check Apps Script → Executions, correct settings, and deploy a new version. We fixed this during setup by updating the Apps Script deployment. |
| Apps Script `testBridge` says OK, but dashboard fails | That only tests editor code. Check the deployed version, Render environment variables, and logs. |
| Apps Script returns unauthorized | Make sure `BRIDGE_SECRET` matches exactly in Apps Script and Render. Do not reveal it while troubleshooting. |
| Old deals reappear after a reset | Stop the EA; confirm the fresh-start source was compiled and that you are using the correct chart/terminal/account. Check its saved cutoff and the sheet; don't reinstall the original pre-reset EA. |
| Balances differ from MT5 | Confirm the correct account is connected, the sync is recent, and the account currency is interpreted correctly. The dashboard is not a broker statement. |

## 11. Free-tier and reliability notes

Render's free web services may spin down after inactivity, wake slowly, and are subject to monthly limits. The EA's frequent requests may keep the service awake and consume free instance hours. Check current Render free-tier limits and billing FAQ; usage beyond included amounts may incur charges if a payment method is on file. Google Apps Script also has quotas. This is a prototype, not a guaranteed real-time reporting or audit system.

## 12. Ideas for future changes

- Add dashboard authentication and protect `/api/dashboard` before relying on it for privacy.
- Group deals by position/trade and correctly account for partial closes and opening costs.
- Add date filters, symbol analysis, journal notes, and screenshots stored securely.
- Build a paginated historical backfill or more durable queue to avoid the 300-deal per-sync gap.
- Add error alerts, backups, tests, and a more durable fresh-start setting.
