const appBasePath = process.env.NEXT_PUBLIC_APP_BASE_PATH ?? "";

function normalizePath(path: string) {
  return path.startsWith("/") ? path : `/${path}`;
}

export function backendApiPath(path: string) {
  return `${appBasePath}/api/backend${normalizePath(path)}`;
}
