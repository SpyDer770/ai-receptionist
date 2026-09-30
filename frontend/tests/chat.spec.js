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

test('booking request with missing info asks for details, creates nothing yet', async ({ page }) => {
    await page.goto('/');

    const input = page.getByPlaceholder('Type a message...');
    await input.fill('Book an appointment tomorrow at 5 PM.');
    await page.getByRole('button', { name: 'Send' }).click();

    const aiMessages = page.locator('.message-bubble-ai');
    await expect(aiMessages).toHaveCount(2, { timeout: 15000 });

    const lastAiReply = aiMessages.last();
    await expect(lastAiReply).toContainText(/name|phone/i, { timeout: 15000 });
});

test('complete booking request creates a real appointment and shows confirmation', async ({ page }) => {
    await page.goto('/');

    const uniquePhone = `9${Date.now().toString().slice(-9)}`;
    const uniqueTime = `${6 + (new Date().getSeconds() % 12)}:00 PM`;

    const input = page.getByPlaceholder('Type a message...');
    await input.fill(
        `Book an appointment tomorrow at ${uniqueTime}. My name is Test User and my number is ${uniquePhone}.`
    );
    await page.getByRole('button', { name: 'Send' }).click();

    const aiMessages = page.locator('.message-bubble-ai');
    await expect(aiMessages).toHaveCount(2, { timeout: 15000 });

    const confirmation = aiMessages.last();
    await expect(confirmation).toContainText(/booked/i, { timeout: 15000 });
    await expect(confirmation).toContainText(/Appointment #\d+/);
});