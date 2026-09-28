import { describe, it, expect } from 'vitest';
import { CATEGORIES, PRIORITIES, STATUSES } from '../src/api/types';

describe('Domain types', () => {
  it('should have exactly six category values matching the assignment', () => {
    expect(CATEGORIES).toEqual([
      'water', 'electricity', 'sanitation', 'roads', 'streetlights', 'other',
    ]);
  });

  it('should have exactly three priority values matching the assignment', () => {
    expect(PRIORITIES).toEqual(['high', 'normal', 'low']);
  });

  it('should have exactly four status values matching the assignment', () => {
    expect(STATUSES).toEqual(['open', 'in_progress', 'resolved', 'rejected']);
  });
});
