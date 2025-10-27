// For overhaul stores

type ResultState<T, E> =
  | { status: 'success'; value: T }
  | { status: 'error'; error: E };

export function ok<T>(value: T): ResultState<T, never> {
  return { status: 'success', value };
}

export function err<E>(error: E): ResultState<never, E> {
  return { status: 'error', error };
}

export async function tryPromise<T, E>(promise: Promise<T>, errorMapper: (error: unknown) => E): Promise<ResultState<T, E>> {
  try {
    const value = await promise;
    return ok(value);
  } catch (error) {
    return err(errorMapper(error));
  }
}

export async function tryFunction<T, E>(fn: () => Promise<T>, errorMapper: (error: unknown) => E): Promise<ResultState<T, E>> {
  return tryPromise(fn(), errorMapper);
}

export type AsyncResultState<T, E> =
  | { status: 'idle' }
  | { status: 'loading'; promise: Promise<ResultState<T, E>> }
  | ResultState<T, E>;

export type PipeFunction<I, O, E> = (input: I) => ResultState<O, E> | Promise<ResultState<O, E>>;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type AsyncResultListener<T, E> = (result: AsyncResult<T, E>) => any;

export class AsyncResult<T, E> {
  private _state: AsyncResultState<T, E>;
  private _listeners: Set<AsyncResultListener<T, E>> = new Set();

  constructor(state?: AsyncResultState<T, E>) {
    this._state = state || { status: 'idle' };
  }

  get state() {
    return this._state;
  }

  private set state(newState: AsyncResultState<T, E>) {
    this._state = newState;
    this._listeners.forEach((listener) => listener(this));
  }

  listen(listener: AsyncResultListener<T, E>, immediate = true) {
    this._listeners.add(listener);
    if (immediate) {
      listener(this);
    }

    return () => {
      this._listeners.delete(listener);
    };
  }

  setState(newState: AsyncResultState<T, E>) {
    this.state = newState;
  }

  update(newState: ResultState<T, E>) {
    this.state = newState;
  }

  updateToValue(value: T) {
    this.state = { status: 'success', value };
  }

  updateToError(error: E) {
    this.state = { status: 'error', error };
  }

  static fromValue<T>(value: T): AsyncResult<T, never> {
    return new AsyncResult<T, never>({ status: 'success', value });
  }

  static fromError<E>(error: E): AsyncResult<never, E> {
    return new AsyncResult<never, E>({ status: 'error', error });
  }

  updateFromResultPromise(promise: Promise<ResultState<T, E>>) {
    this.state = { status: 'loading', promise };
    promise
      .then((res) => {
        this.state = res;
      })
      .catch((error) => {
        this.state = { status: 'error', error };
      });
  }

  static fromResultPromise<T, E>(promise: Promise<ResultState<T, E>>): AsyncResult<T, E> {
    const result = new AsyncResult<T, E>();
    result.updateFromResultPromise(promise);
    return result;
  }

  updateFromValuePromise(promise: Promise<T>) {
    const resultStatePromise = async (): Promise<ResultState<T, E>> => {
      try {
        const value = await promise;
        return { status: 'success', value };
      } catch (error) {
        return { status: 'error', error: error as E };
      }
    };
    this.updateFromResultPromise(resultStatePromise());
  }

  static fromValuePromise<T, E>(promise: Promise<T>): AsyncResult<T, E> {
    const result = new AsyncResult<T, E>();
    result.updateFromValuePromise(promise);
    return result;
  }

  static ok<T>(value: T): AsyncResult<T, never> {
    return new AsyncResult<T, never>({ status: 'success', value });
  }

  static err<E>(error: E): AsyncResult<never, E> {
    return new AsyncResult<never, E>({ status: 'error', error });
  }

  async toResultPromise(): Promise<AsyncResult<T, E>> {
    if (this._state.status === 'loading') {
      try {
        const value = await this._state.promise;
        this._state = value;
      } catch (error) {
        this._state = { status: 'error', error: error as E };
      }
    }
    return this;
  }

  unwrapOrNull(): T | null {
    if (this._state.status === 'success') {
      return this._state.value;
    }
    return null;
  }

  async unwrapOrNullOnceSettled(): Promise<T | null> {
    return (await this.toResultPromise()).unwrapOrNull();
  }

  unwrapOrThrow(): T {
    if (this._state.status === 'success') {
      return this._state.value;
    }
    throw new Error('Tried to unwrap an AsyncResult that is not successful');
  }

  async unwrapOrThrowOnceSettled(): Promise<T> {
    return (await this.toResultPromise()).unwrapOrThrow();
  }

  pipe<O, E2 = E>(fn: PipeFunction<T, O, E | E2>): AsyncResult<O, E | E2> {
    const newResultBuilder = async (): Promise<ResultState<O, E | E2>> => {
      const settled = await this.toResultPromise();
      if (settled.state.status === 'loading' || settled.state.status === 'idle') {
        throw new Error('Unexpected state after waitForSettled'); // TODO handle this case properly
      }
      if (settled.state.status === 'error') {
        return { status: 'error', error: settled.state.error };
      }

      return fn(settled.state.value);
    };

    return AsyncResult.fromResultPromise<O, E | E2>(newResultBuilder());
  }

  // pipeParallel PipeFunction[] -> AsyncResult<T, E>[]
  // pipeParallelAndCollapse PipeFunction[] -> AsyncResult<T[], E>
}