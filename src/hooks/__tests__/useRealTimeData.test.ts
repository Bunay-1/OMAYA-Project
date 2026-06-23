import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useRealTimeData } from '../useRealTimeData';

// Mock global fetch
global.fetch = vi.fn();

describe('useRealTimeData hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return initial data', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok', machines: [] }),
    });

    const { result } = renderHook(() => useRealTimeData());
    expect(result.current).toBeDefined();
    expect(result.current.machines).toBeDefined();
  });
});
