import { type Action, AsyncResult, type ErrorBase } from "unwrapped/core";
import { useLazyAction } from "unwrapped/vue";
import { onMounted, ref, triggerRef } from "vue";

type AsyncResultListState = "any-loading" | "all-settled";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export class AsyncResultList<T = any, E extends ErrorBase = ErrorBase> {
    private _queue = new Map<string, AsyncResult<T, E>>();
    private _listeners: Set<(taskQueue: AsyncResultList<T, E>) => void> = new Set();
    private _state: AsyncResultListState = "all-settled";

    get tasks() {
        return this._queue;
    }

    get state() {
        return this._state;
    }

    private set state(s: AsyncResultListState) {
        this._state = s;
        this._listeners.forEach(f => f(this));
    }

    private _onTaskFinished() {
        this.state = this.anyLoading() ? "any-loading" : "all-settled";
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    listen(listener: () => any) {
        this._listeners.add(listener);
        return () => {
            this._listeners.delete(listener);
        };
    }

    add(key: string, task: AsyncResult<T, E>, removeOnSettle: boolean = true): AsyncResult<T, E> {
        this._queue.set(key, task);
        this.state = "any-loading";

        if (removeOnSettle) {
            task.listenUntilSettled((r) => {
                if (r.isLoading() || r.isIdle()) return;
                this._onTaskFinished();
                this._queue.delete(key);
            }, true);
        } else {
            task.listen((r) => {
                if (r.isLoading() || r.isIdle()) return;
                this._onTaskFinished();
            }, true);
        }

        return task;
    }

    anyLoading(): boolean {
        for (const task of this._queue.values()) {
            if (task.isLoading()) {
                return true;
            }
        }
        return false;
    }

    getAllSuccess(): AsyncResult<T, E>[] {
        const success: AsyncResult<T, E>[] = [];
        for (const task of this._queue.values()) {
            if (task.isSuccess()) {
                success.push(task);
            }
        }
        return success;
    }

    getAllSuccessValues(): T[] {
        const successValues: T[] = [];
        for (const task of this._queue.values()) {
            const v = task.unwrapOrNull();
            if (v !== null) {
                successValues.push(v);
            }
        }
        return successValues;
    }

    get length(): number {
        return this._queue.size;
    }

    get items(): AsyncResult<T, E>[] {
        return Array.from(this._queue.values());
    }

    log(name?: string) {
        const time = (new Date()).toTimeString().slice(0, 8);
        console.log(`${name ?? '<Anonymous TaskQueue>'} ; State at ${time} :`, this.state, this._queue);
    }

    debug(name?: string) {
        return this.listen(() => {
            this.log(name);
        });
    }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function useAsyncResultList<T = any, E extends ErrorBase = ErrorBase>() {
    const queue = new AsyncResultList<T, E>();
    const queueRef = ref(queue);

    queue.listen(() => {
        triggerRef(queueRef);
    });

    return queueRef;
}

export function delay(ms: number): AsyncResult<true> {
    return AsyncResult.fromValuePromise(new Promise(resolve => {
        setTimeout(() => resolve(true), ms);
    }));
}

export function useActionOnMounted<T, E extends ErrorBase = ErrorBase>(action: Action<T, E>) {
    const { resultRef, trigger } = useLazyAction(action);
    
    onMounted(() => {
        trigger();
    });

    return resultRef;
}