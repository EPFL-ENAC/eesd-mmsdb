import { AsyncResult, type AsyncResultState, type ChainFunction } from "./asyncResult";
import type { ErrorBase } from "./error";

type KeyedAsyncCacheRefetchOptions = {
    policy: 'refetch' | 'if-error' | 'no-refetch';
};

type CacheItem<P, V, E> = {
    result: AsyncResult<V, E>;
    fetcherParams: P;
};

const _defaultRefetchOptions: KeyedAsyncCacheRefetchOptions = { policy: 'no-refetch' };

function defaultParamsToKey<P>(params: P): string {
  if (typeof params === 'object') {
    return JSON.stringify(params);
  }
  return String(params);
}

export class KeyedAsyncCache<P, V, E = ErrorBase> {
  private _cache: Map<string, CacheItem<P, V, E>> = new Map();
  private _fetcher: ChainFunction<P, V, E>;
  private _paramsToKey: (params: P) => string;

  constructor(fetcher: ChainFunction<P, V, E>, paramsToKey: (params: P) => string = defaultParamsToKey) {
    this._fetcher = fetcher;
    this._paramsToKey = paramsToKey;
  }

  private makeCacheItem(result: AsyncResult<V, E>, fetcherParams: P): CacheItem<P, V, E> {
    return { result, fetcherParams };
  }

  private shouldRefetch(existingResult: CacheItem<P, V, E>, refetch: KeyedAsyncCacheRefetchOptions): boolean {
    if (refetch.policy === 'refetch') {
      return true;
    }
    if (refetch.policy === 'if-error') {
      return existingResult.result.state.status === 'error';
    }
    return false;
  }

  get(params: P, refetch: KeyedAsyncCacheRefetchOptions = _defaultRefetchOptions): AsyncResult<V, E> {
    const key = this._paramsToKey(params);
    if (this._cache.has(key)) {
      const cacheItem = this._cache.get(key)!;
      if (!this.shouldRefetch(cacheItem, refetch)) {
        return cacheItem.result;
      } else {
        cacheItem.result.updateFromResultPromise(Promise.resolve(this._fetcher(cacheItem.fetcherParams)));
        return cacheItem.result;
      }
    }

    const asyncResult = AsyncResult.fromResultPromise(Promise.resolve(this._fetcher(params)));
    this._cache.set(key, this.makeCacheItem(asyncResult, params));
    return asyncResult;
  }

  async getSettledState(params: P, refetch: KeyedAsyncCacheRefetchOptions = _defaultRefetchOptions): Promise<AsyncResultState<V, E>> {
    const asyncResult = this.get(params, refetch);
    await asyncResult.waitForSettled();
    return asyncResult.state;
  }

  anyLoading(): boolean {
    for (const cacheItem of this._cache.values()) {
      if (cacheItem.result.isLoading()) {
        return true;
      }
    }
    return false;
  }

  clear() {
    this._cache.clear();
  }
}
