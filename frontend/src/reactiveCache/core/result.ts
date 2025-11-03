import type { ErrorBase } from "./error";

export type ResultState<T, E = ErrorBase> =
  | { status: 'success'; value: T }
  | { status: 'error'; error: E };


export class Result<T, E = ErrorBase> {
  private _state: ResultState<T, E>;

  constructor(state: ResultState<T, E>) {
    this._state = state;
  }

  get state() {
    return this._state;
  }

  static ok<T>(value: T): Result<T, never> {
    return new Result({ status: 'success', value });
  }

  static err<E>(error: E): Result<never, E> {
    return new Result({ status: 'error', error });
  }

  unwrapOrNull(): T | null {
    if (this._state.status === 'success') {
      return this._state.value;
    }
    return null;
  }

  unwrapOrThrow(): T {
    if (this._state.status === 'success') {
      return this._state.value;
    }
    throw new Error('Tried to unwrap a Result that is not successful');
  }

  unwrapOr<O>(defaultValue: O): T | O {
    if (this._state.status === 'success') {
      return this._state.value;
    }
    return defaultValue;
  }

  isSuccess(): boolean {
    return this._state.status === 'success';
  }

  isError(): boolean {
    return this._state.status === 'error';
  }

  static tryPromise<T, E>(promise: Promise<T>, errorMapper: (error: unknown) => E): Promise<Result<T, E>> {
    return promise
      .then((value) => Result.ok(value))
      .catch((error) => Result.err(errorMapper(error)));
  }

  static tryFunction<T, E extends ErrorBase = ErrorBase>(fn: () => Promise<T>, errorMapper: (error: unknown) => E): Promise<Result<T, E>> {
    return Result.tryPromise(fn(), errorMapper);
  }

  chain<O, E2>(fn: (input: T) => ResultState<O, E | E2>): Result<O, E | E2> {
    if (this._state.status === 'success') {
      return new Result<O, E | E2>(fn(this._state.value));
    }
    return Result.err<E>(this._state.error);
  }
}
