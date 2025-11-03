export class ErrorBase {
  code: string;
  message?: string | undefined;
  thrownError?: any;

  constructor(code: string, message?: string, thrownError?: any, log: boolean = true) {
    this.code = code;
    this.message = message;
    this.thrownError = thrownError;

    if (log) {
      this.logError();
    }
  }

  toString(): string {
    return `Error ${this.code}: ${this.message ?? ''}`;
  }

  logError(): void {
    console.error(this.toString(), this.thrownError);
  }
}