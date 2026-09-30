import { test, expect } from '@playwright/test';

test('sends a message and receives an AI reply', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'AI Receptionist' })).toBeVisible();

    const input = page.getByPlaceholder('Type a message...');
    const sendButton = page.getByRole('button', { name: 'Send' });

    await input.fill('Hello');
    await sendButton.click();

    await expect(page.getByText('Hello', { exact: true })).toBeVisible();

    const aiMessages = page.locator('.message-bubble-ai');
    await expect(aiMessages).toHaveCount(2, { timeout: 15000 });
});

test('shows an error banner when the backend is unreachable', async ({ page }) => {
    await page.route('**/chat', (route) => route.abort('failed'));

    await page.goto('/');

    const input = page.getByPlaceholder('Type a message...');
    await input.fill('Hello');
    await page.getByRole('button', { name: 'Send' }).click();

    await expect(page.getByRole('alert')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Not delivered')).toBeVisible();
});

test('clear conversation resets to the greeting only', async ({ page }) => {
    await page.goto('/');

    const input = page.getByPlaceholder('Type a message...');
    await input.fill('Hello');
    await page.getByRole('button', { name: 'Send' }).click();

    await expect(page.locator('.message-bubble-ai')).toHaveCount(2, { timeout: 15000 });

    await page.getByRole('button', { name: 'Clear conversation' }).click();

    await expect(page.locator('.message-bubble')).toHaveCount(1);
});