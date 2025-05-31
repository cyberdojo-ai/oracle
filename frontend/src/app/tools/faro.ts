import { initializeFaro, getWebInstrumentations, } from '@grafana/faro-web-sdk';
import { TracingInstrumentation } from '@grafana/faro-web-tracing';
import { EnvType } from './env';


export type { Faro } from '@grafana/faro-web-sdk';

export default function initFaro({
    url,
    name,
    environment,
    propagateTraceHeaderCorsUrls = [
        new RegExp("http://localhost:*"),
        new RegExp("http://127.0.0.1:*")
    ],
}: {
    url: string;
    name: string;
    environment?: EnvType;
    propagateTraceHeaderCorsUrls?: RegExp[];
}) {

    return initializeFaro({
        url: url,
        app: {
            name: name,
            version: '1.0.0',
            environment: environment,
        },
        
        instrumentations: [
            ...getWebInstrumentations(),
            new TracingInstrumentation({
                instrumentationOptions: {
                    propagateTraceHeaderCorsUrls: propagateTraceHeaderCorsUrls
                }
            })
        ],
    });
}

