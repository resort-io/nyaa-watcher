export type NyaaType = "nyaa" | "sukebei";

export type WebhookService = "discord";

export type ErrorCategory = 'database' | 'network' | 'validation' | 'webhook' | 'unknown';

export type DatabaseError = 'migration' | 'seeding' | 'query' | 'connection';
export type NetworkError = 'timeout' | 'dns' | 'refused';
export type ValidationError = 'invalid_input' | 'missing_field';
export type WebhookError = 'send_failed' | 'invalid_payload';
export type UnknownError = 'internal_server_error';

export interface ErrorMap {
    database: DatabaseError;
    network: NetworkError;
    validation: ValidationError;
    webhook: WebhookError;
    unknown: UnknownError;
}

export type ServerError = {
    [K in ErrorCategory]: `${K}:${ErrorMap[K]}`
}[ErrorCategory];

export type Response<
    T = null,
    E = Error,
> =
    | SuccessResponse<T>
    | ErrorResponse<E>;

export interface SuccessResponse<
    T = null,
> {
    status: 'success',
    data: T,
    message: string,
}

export interface ErrorResponse<
    E = Error,
> {
    status: 'error',
    data: null,
    message: string,
    error: E | string,
}
