import { describe, expect, it } from 'vitest';

import {
  formatCurrencyBRL,
  formatDate,
  formatDateTime,
  formatDecimal,
  formatPercent,
} from './format';

describe('formatação pt-BR sem ponto flutuante', () => {
  it.each([
    ['15780.00', 'R$ 15.780,00'],
    ['14900', 'R$ 14.900,00'],
    ['880.5', 'R$ 880,50'],
    ['0.05', 'R$ 0,05'],
    ['1234567.8912', 'R$ 1.234.567,8912'],
    ['-12.30', '-R$ 12,30'],
    ['-0.00', 'R$ 0,00'],
  ])('moeda %s -> %s', (raw, expected) => {
    expect(formatCurrencyBRL(raw)).toBe(expected);
  });

  it('preserva valores maiores que a precisão de float', () => {
    expect(formatCurrencyBRL('90071992547409931.23')).toBe('R$ 90.071.992.547.409.931,23');
  });

  it('formata percentuais e decimais', () => {
    expect(formatPercent('5.91')).toBe('5,91%');
    expect(formatDecimal('30')).toBe('30');
    expect(formatDecimal('0001.50')).toBe('1,50');
  });

  it('rejeita entradas inválidas', () => {
    expect(() => formatCurrencyBRL('1,5')).toThrow();
    expect(() => formatCurrencyBRL('abc')).toThrow();
    expect(() => formatDate('26/09/2026')).toThrow();
  });

  it('formata datas no padrão DD/MM/AAAA', () => {
    expect(formatDate('2026-09-26')).toBe('26/09/2026');
  });

  it('converte timestamps UTC para o fuso de Brasília', () => {
    expect(formatDateTime('2026-09-26T15:30:00Z')).toBe('26/09/2026, 12:30');
  });
});
