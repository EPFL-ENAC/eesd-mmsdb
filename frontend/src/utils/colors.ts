export function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  s /= 100;
  l /= 100;
  const k = (n: number) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n: number) =>
    l - a * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1));
  
  return [
    Math.round(255 * f(0)),
    Math.round(255 * f(8)),
    Math.round(255 * f(4))
  ];
}

export function hslStringToRgb(hsl: string): [number, number, number] {
  const match = hsl.match(/hsl\(\s*(\d+),\s*(\d+)%,\s*(\d+)%\s*\)/);
  if (!match || match.length !== 4) {
    throw new Error('Invalid HSL color format');
  }
  
  const h = parseInt(match[1]!, 10);
  const s = parseInt(match[2]!, 10);
  const l = parseInt(match[3]!, 10);
  
  return hslToRgb(h, s, l);
}