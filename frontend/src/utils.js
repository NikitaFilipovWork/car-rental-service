import moment from 'moment';

export const DATE_FORMAT = 'YYYY-MM-DD';

export const FUEL_TYPES = [
  { id: 'GAS', name: 'Gas' },
  { id: 'DIESEL', name: 'Diesel' },
  { id: 'HYBRID', name: 'Hybrid' },
  { id: 'ELECTRIC', name: 'Electric' }
];

export const RENTAL_STATUSES = [
  { id: 'BOOKED', name: 'Booked' },
  { id: 'OVERDUE', name: 'Overdue' },
  { id: 'COMPLETED', name: 'Completed' },
  { id: 'CANCELED', name: 'Canceled' }
];

export const PAYMENT_STATUSES = [
  { id: 'PENDING', name: 'Pending' },
  { id: 'PAID', name: 'Paid' },
  { id: 'EXPIRED', name: 'Expired' }
];

export const PAYMENT_TYPES = [
  { id: 'RENTAL', name: 'Rental' },
  { id: 'OVERDUE_FEE', name: 'Overdue fee' },
  { id: 'CANCELLATION_FEE', name: 'Cancellation fee' }
];

export function optionName (options, id) {
  const option = options.find(item => item.id === id);
  return option ? option.name : id;
}

export function today () {
  return moment().format(DATE_FORMAT);
}

export function formatDate (date) {
  return date ? moment(date, DATE_FORMAT).format('DD MMM YYYY') : '—';
}

export function formatMoney (amount) {
  return `$${Number(amount).toFixed(2)}`;
}

// Rental days are inclusive, like on the backend: end - start + 1
export function rentalDays (start, end) {
  return moment(end, DATE_FORMAT).diff(moment(start, DATE_FORMAT), 'days') + 1;
}
