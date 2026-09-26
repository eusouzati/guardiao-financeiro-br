/**
 * Formatação pt-BR somente para exibição.
 *
 * Valores decimais chegam da API como string (ADR-007) e são formatados por manipulação
 * de texto — sem conversão para número de ponto flutuante, preservando todas as casas.
 */

const DECIMAL_PATTERN = /^(-)?(\d+)(?:\.(\d+))?$/;
export const DISPLAY_TIME_ZONE = 'America/Sao_Paulo';

function groupThousands(integerPart: string): string {
  return integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

/** Formata uma string decimal ("15780.5") como número pt-BR ("15.780,50"). */
export function formatDecimal(value: string, minFractionDigits = 0): string {
  const match = DECIMAL_PATTERN.exec(value.trim());
  if (!match) {
    throw new Error(`Valor decimal inválido: ${value}`);
  }
  const [, sign = '', rawInteger = '0', rawFraction = ''] = match;
  const integer = rawInteger.replace(/^0+(?=\d)/, '');
  const fraction = rawFraction.padEnd(minFractionDigits, '0');
  const isZero = /^0*$/.test(integer + fraction);
  const prefix = sign && !isZero ? '-' : '';
  return `${prefix}${groupThousands(integer)}${fraction ? `,${fraction}` : ''}`;
}

/** "15780.00" -> "R$ 15.780,00" (mínimo de 2 casas; casas extras preservadas). */
export function formatCurrencyBRL(value: string): string {
  const formatted = formatDecimal(value, 2);
  return formatted.startsWith('-') ? `-R$ ${formatted.slice(1)}` : `R$ ${formatted}`;
}

/** "5.91" -> "5,91%" */
export function formatPercent(value: string): string {
  return `${formatDecimal(value)}%`;
}

/** Data ISO (AAAA-MM-DD) -> DD/MM/AAAA, sem conversão de fuso. */
export function formatDate(isoDate: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(isoDate);
  if (!match) {
    throw new Error(`Data inválida: ${isoDate}`);
  }
  const [, year, month, day] = match;
  return `${day ?? ''}/${month ?? ''}/${year ?? ''}`;
}

const dateTimeFormatter = new Intl.DateTimeFormat('pt-BR', {
  dateStyle: 'short',
  timeStyle: 'short',
  timeZone: DISPLAY_TIME_ZONE,
});

/** Timestamp ISO 8601 em UTC -> "26/09/2026, 14:30" no fuso de Brasília. */
export function formatDateTime(isoTimestamp: string): string {
  const date = new Date(isoTimestamp);
  if (Number.isNaN(date.getTime())) {
    throw new Error(`Data/hora inválida: ${isoTimestamp}`);
  }
  return dateTimeFormatter.format(date);
}
