export function toMaxDecimals(x: number | null, n: number): number | null {
  if (x === null) {
    return null;
  }
  return +x.toFixed(n);
}

export function toFixed(x: number | null, n: number): string | null {
  if (x === null) {
    return null;
  }
  return x.toFixed(n);
}

export function makeLiteralLabel(values: number[]): string {
  const last = values.pop();
  if (values.length === 0) {
    return last + '';
  }
  return values.join(', ') + ' and ' + last;
}

export function getSizeLabel(size: number | undefined) {
  if (size === undefined || isNaN(size)) {
    return '-';
  }
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(2)} KB`;
  }
  if (size < 1024 * 1024 * 1024) {
    return `${(size / 1024 / 1024).toFixed(2)} MB`;
  }
  return `${(size / 1024 / 1024 / 1024).toFixed(2)} GB`;
}

export function withRange(range: [number, number], defaultRange: [number, number]) {
  return range[0] !== defaultRange[0] || range[1] !== defaultRange[1];
}
