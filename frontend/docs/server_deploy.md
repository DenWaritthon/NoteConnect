# Server Deployment with PM2

This guide explains how to deploy the NoteConnect frontend on a server with PM2.

## Requirements

Install these on the server:

- Node.js 20 or newer
- npm
- Git
- PM2
- Running NoteConnect backend API

Install PM2 globally:

```bash
npm install -g pm2
```

## Clone the Project

```bash
git clone <your-repository-url> NoteConnect
cd NoteConnect/frontend
```

## Install Dependencies

```bash
npm install
```

## Configure Environment

Create the production environment file:

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_APP_BASE_PATH=/fibo6550/NoteConnect
NOTE_CONNECT_API_BASE_URL=http://127.0.0.1:6550
API_SECRET_KEY=your_api_secret_key
API_KEY_HEADER_NAME=NoteConnect-API-Key
```

Environment variables:

- `NEXT_PUBLIC_APP_BASE_PATH`: public subpath where the frontend is mounted. Leave empty when serving from the domain root.
- `NOTE_CONNECT_API_BASE_URL`: backend API base URL.
- `API_SECRET_KEY`: API key sent from the frontend proxy to the backend.
- `NOTE_CONNECT_API_KEY`: optional fallback API key variable.
- `API_KEY_HEADER_NAME`: header name used when sending the API key.

## Build the Frontend

```bash
npm run build
```

## Start with PM2

Start the Next.js production server:

```bash
pm2 start npm --name noteconnect-frontend -- start
```

Next.js starts on port `3000` by default.

To choose a port:

```bash
PORT=3000 pm2 start npm --name noteconnect-frontend -- start
```

## Verify the App

Check PM2 status:

```bash
pm2 status
```

View logs:

```bash
pm2 logs noteconnect-frontend
```

Open the app:

```text
http://your-server-ip:3000
```

## Start App After Server Reboot

Save the PM2 process list:

```bash
pm2 save
```

Generate the startup command:

```bash
pm2 startup
```

PM2 prints a command that starts with `sudo`. Run that printed command on the server.

## Update an Existing Deployment

```bash
cd NoteConnect
git pull
cd frontend
npm install
npm run build
pm2 restart noteconnect-frontend
```

If `.env.local` changes, rebuild and restart the PM2 process.

## Useful PM2 Commands

Show running processes:

```bash
pm2 status
```

Show logs:

```bash
pm2 logs noteconnect-frontend
```

Restart the app:

```bash
pm2 restart noteconnect-frontend
```

Stop the app:

```bash
pm2 stop noteconnect-frontend
```

Remove the app from PM2:

```bash
pm2 delete noteconnect-frontend
```

Save the current process list:

```bash
pm2 save
```

## Reverse Proxy Note

For production domains, place Nginx or another reverse proxy in front of the app.

The proxy should forward traffic to:

```text
http://127.0.0.1:3000
```

Also make sure the backend API remains reachable from the frontend server at `NOTE_CONNECT_API_BASE_URL`.

## Troubleshooting

### App Does Not Start

Check logs:

```bash
pm2 logs noteconnect-frontend
```

Then confirm:

- Dependencies are installed.
- `npm run build` completed successfully.
- `.env.local` exists.
- Port `3000` is available or a different `PORT` is configured.

### Missing API Key

Set `API_SECRET_KEY` in `.env.local`, rebuild, and restart:

```bash
npm run build
pm2 restart noteconnect-frontend
```

### Backend Requests Fail

Confirm:

- Backend service is running.
- `NOTE_CONNECT_API_BASE_URL` is correct.
- `API_KEY_HEADER_NAME` matches the backend.
- `API_SECRET_KEY` matches the backend secret.
