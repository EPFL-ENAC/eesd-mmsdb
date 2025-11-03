export class ErrorBase {
  code: string;
  message?: string | undefined;

  constructor(code: string, message?: string) {
    this.code = code;
    this.message = message;
  }
}