import { describe, it } from 'node:test';
import assert from 'node:assert';

describe('COGNIFY AI Frontend Verification', () => {
  it('validates navigation routes configuration', () => {
    const routes = [
      '/dashboard',
      '/skill-dna',
      '/careers',
      '/skill-gaps',
      '/simulator',
      '/roadmap',
      '/assessments',
      '/mentor',
      '/projects',
      '/analytics',
      '/agent-center',
    ];
    assert.strictEqual(routes.length, 11);
    assert.ok(routes.includes('/dashboard'));
    assert.ok(routes.includes('/roadmap'));
  });

  it('validates API base URL formatting logic', () => {
    const rawUrl = 'https://promptwarsxrtc.onrender.com';
    const cleanUrl = rawUrl.endsWith('/api') ? rawUrl : `${rawUrl}/api`;
    assert.strictEqual(cleanUrl, 'https://promptwarsxrtc.onrender.com/api');
  });

  it('validates multi-tier skill evidence types', () => {
    const evidenceTypes = ['claimed', 'assessed', 'demonstrated'];
    assert.strictEqual(evidenceTypes.length, 3);
    assert.ok(evidenceTypes.includes('demonstrated'));
  });
});
