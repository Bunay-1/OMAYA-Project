import { test, expect } from '@playwright/test';

test.describe('OMAYA dashboard flow', () => {
  test('navigation between dashboard tabs works', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByText('OMAYA Platform')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Alerts' })).toBeVisible();

    const sidebar = page.locator('aside');

    await sidebar.getByRole('button', { name: 'Alerts' }).click({ force: true });
    await expect(page.getByText('Alert Center')).toBeVisible();

    await sidebar.getByRole('button', { name: 'Predictive AI' }).click({ force: true });
    await expect(page.getByText('Predictive Analytics')).toBeVisible();

    await sidebar.getByRole('button', { name: 'Tool Wear' }).click({ force: true });
    await expect(page.getByText('Tool Wear Tracking')).toBeVisible();

    await sidebar.getByRole('button', { name: 'Live Telemetry' }).click({ force: true });
    await expect(page.locator('h1:has-text("Live Telemetry")')).toBeVisible();
  });

  test('fleet overview search filters machine list', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'Fleet Overview' })).toBeVisible();
    const searchInput = page.locator('input[placeholder="Search machines by ID or name..."]');
    await expect(searchInput).toBeVisible();

    await expect(page.locator('text=machines monitored')).toBeVisible();

    await searchInput.fill('001');
    await expect(searchInput).toHaveValue('001');
    await expect(page.locator('button:has-text("001")')).toBeVisible();
  });
});
