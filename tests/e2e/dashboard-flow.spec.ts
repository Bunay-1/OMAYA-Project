import { test, expect } from '@playwright/test';

test.describe('OMAYA dashboard flow', () => {
  test('navigation between dashboard tabs works', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByText('OMAYA Platform')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Alerts' })).toBeVisible();

    await page.getByRole('button', { name: 'Alerts' }).click();
    await expect(page.getByText('Alert Center')).toBeVisible();

    await page.getByRole('button', { name: 'Predictive AI' }).click();
    await expect(page.getByText('Predictive Analytics')).toBeVisible();

    await page.getByRole('button', { name: 'Tool Wear' }).click();
    await expect(page.getByText('Tool Wear Tracking')).toBeVisible();

    await page.getByRole('button', { name: 'Live Telemetry' }).click();
    await expect(page.getByRole('heading', { name: 'Live Telemetry' })).toBeVisible();
  });

  test('fleet overview search filters machine list', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByText('Fleet Overview')).toBeVisible();
    const searchInput = page.locator('input[placeholder="Search machines by ID or name..."]');
    await expect(searchInput).toBeVisible();

    await expect(page.locator('text=machines monitored')).toBeVisible();

    await searchInput.fill('001');
    await expect(searchInput).toHaveValue('001');
    await expect(page.locator('button:has-text("001")')).toBeVisible();
  });
});
