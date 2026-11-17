import data from '../data/state.json';
export const D = data.devices;
export const LN = { iphone: 'iPhone', ipad: 'iPad', mac: 'Mac', watch: 'Apple Watch', airpods: 'AirPods', vision: 'Apple Vision', home: 'Home' };
export const lines = Object.keys(LN);
export const groupsOf = k => [...((k === 'iphone' ? D.groups : D.lines[k]) || [])].sort((a, b) => b.date.localeCompare(a.date));
export const fmt = d => new Date(d + 'T12:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
