import { test, expect } from '@playwright/test';

test('homepage should load and show OMAYA title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/\//);
  await expect(page.locator('body')).toContainText('OMAYA');
});
