
export type EnvType = "development" | "production" | "staging";

export type Env = {
    appName: string;
    apiBaseUrl: string;
    environment: EnvType;
    
    faroUrl?: string | undefined;
    faroTraceHeaderCorsUrls?: RegExp[] | undefined;
};

export default function getEnv(): Env {
    const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "Oracle";
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
    const environment = (process.env.NEXT_PUBLIC_ENVIRONMENT as EnvType) ?? "development";
    
    const faroUrl = process.env.NEXT_PUBLIC_FARO_URL;
    const faroTraceHeaderCorsUrls = process.env.NEXT_PUBLIC_FARO_TRACE_HEADER_CORS_URLS
        ? process.env.NEXT_PUBLIC_FARO_TRACE_HEADER_CORS_URLS.split(",").map(url => new RegExp(url.trim()))
        : undefined;

    return {
        appName,
        apiBaseUrl,
        environment,
        faroUrl,
        faroTraceHeaderCorsUrls
    };
}
