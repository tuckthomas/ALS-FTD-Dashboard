import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from "path";
// https://vitejs.dev/config/
export default defineConfig(function (_a) {
    var mode = _a.mode;
    // Load env file based on `mode` in the current working directory.
    // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
    var env = loadEnv(mode, path.resolve(__dirname, '..'), '');
    var allowedHosts = env.ALLOWED_HOSTS
        ? env.ALLOWED_HOSTS.split(',').map(function (host) { return host.trim(); })
        : [];
    console.log("Allowed Hosts:", allowedHosts);
    return {
        plugins: [react()],
        resolve: {
            alias: {
                "@": path.resolve(__dirname, "./src"),
            },
        },
        server: {
            allowedHosts: allowedHosts,
            proxy: {
                '/api': {
                    target: 'http://127.0.0.1:8000',
                    changeOrigin: true,
                    secure: false,
                },
                '/static': {
                    target: 'http://127.0.0.1:8000',
                    changeOrigin: true,
                    secure: false,
                },
            }
        }
    };
});
